from celery import shared_task
from celery_progress.backend import ProgressRecorder
from cvv.models import CreditCardInformation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, transaction
import hashlib
from cryptography.fernet import Fernet
import base64
from django.utils import timezone
from bininfo.models import BIN
import logging
from .models import Category
from django.db.models import F
from sellers.models import Seller

# Logger for error logging
logger = logging.getLogger(__name__)

# key for encryption
key = b'CPd6uxuc-ag1k79BCpYm6knRRJYtjHhmZ5m44T43a_Q='
cipher_suite = Fernet(key)

def generate_card_hash(card_number):
    hash_object = hashlib.sha256(card_number.encode())
    return hash_object.hexdigest()

@shared_task(bind=True)
def process_batch(self, seller_id, batch, base_id, refund, usprice, nonusprice):

    progress_recorder = ProgressRecorder(self)
    total_records = len(batch)

    # Fetch the Seller instance using seller_id instead of User
    seller_instance = Seller.objects.get(pk=seller_id)


    category_instance = Category.objects.get(id=base_id)

    error_data = []
    duplicates = []

    for i, card_data in enumerate(batch, start=1):
        try:
            with transaction.atomic():
                line = card_data.split('|')
                card_number = line[0]
                hashed_card = generate_card_hash(card_number)

                if CreditCardInformation.objects.filter(unique_card_identifier=hashed_card).exists():
                    duplicates.append(card_data)
                    continue

                encrypted_text = cipher_suite.encrypt(card_data.encode('utf-8'))
                encrypted_text_base64 = base64.urlsafe_b64encode(encrypted_text).decode('utf-8')

                # Extract additional fields
                month, year, name, city, state, zip_code = line[1], line[2], line[4], line[6], line[7], line[8]
                iso_country_code = line[-1].split(':::')[0].strip()
                # Determine the price based on country code
                if iso_country_code.lower() == 'us':
                    price = usprice
                else:
                    price = nonusprice if nonusprice is not None else 7


                get_bin_info = card_number[:6]

                # Default values for BIN-related fields
                bin_number, card_type, level, vendor, bank, country_full_name = 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown'

                try:
                    bin_obj = BIN.objects.get(bin_start=get_bin_info)
                    bin_number = bin_obj.bin_start
                    card_type = bin_obj.bin_card_type
                    level = bin_obj.bin_card_level
                    vendor = bin_obj.bin_card_comptype
                    bank = bin_obj.bin_bank_name
                    country_full_name = bin_obj.bin_country_name
                except BIN.DoesNotExist:
                    error_data.append({'data': card_data, 'error_message': 'BIN not found'})

                # Save CreditCardInformation to the database
                new_card = CreditCardInformation.objects.create(
                    unique_card_identifier=hashed_card,
                    card_info=encrypted_text_base64,
                    card_bin=bin_number,
                    card_expiry_month=month,
                    card_expiry_year=year,
                    card_holder_name=name,
                    card_city=city,
                    card_state=state,
                    card_zip_code=zip_code,
                    card_country=country_full_name,
                    card_brand=vendor,
                    card_type=card_type,
                    card_level=level,
                    card_bank=bank,
                    card_base=category_instance,
                    card_price=price,
                    card_refund_status=refund,
                    uploaded_date=timezone.now(),
                    uploaded_by=seller_instance
                )

                # Increment the total_cards in the Category model
                if new_card:
                    Category.objects.filter(id=base_id).update(uploaded_cards=F('uploaded_cards') + 1)


        except ValidationError:
            error_data.append({'data': card_data, 'error_message': 'Invalid data format.'})
        except IntegrityError:
            duplicates.append(card_data)
        except Exception as e:
            error_data.append({'data': card_data, 'error_message': 'An unexpected error occurred.'})

        # Update progress
        progress_recorder.set_progress(i, total_records)

    return {'errors': error_data, 'duplicates': duplicates}

@shared_task
def delete_base_and_cvv(base_id):
    try:
        base = Category.objects.get(pk=base_id)
        cvv_count = CreditCardInformation.objects.filter(card_base=base_id).delete()
        base.delete()
        return f"Base '{base.name}' and all related {cvv_count} CVVs have been deleted successfully."
    except ObjectDoesNotExist:
        return f"Base with id {base_id} does not exist."
    except Exception as e:
        return f"An error occurred: {str(e)}"
