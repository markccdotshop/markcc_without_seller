from orders.models import Order,OrderCheck
from cvv.models import CreditCardInformation
from core_services.check_services import check_card
from django.db.models import Q
from django.db import transaction
from users.models import Transaction
from core_services.balance_services import update_user_balance
from core_services.decryption_services import decrypt_card_info
from celery import shared_task

@shared_task
def process_purchase_task(user_id, card_id):
    from django.contrib.auth import get_user_model  # Import here to avoid circular imports

    User = get_user_model()
    user = User.objects.get(id=user_id)

    card = CreditCardInformation.objects.get(id=card_id)

    with transaction.atomic():
        # Deduct card price from user balance
        card_price = card.card_price
        update_user_balance(user, amount=card_price, is_refund=False)

        # Log the transaction
        Transaction.objects.create(
            user=user,
            amount=card_price,
            transaction_type='Purchase',
            description=f"Card Id: {card.id} Charge For Purchased Item"
        )

        # Decrypt card information for order creation
        decrypted_card_info = decrypt_card_info(card.card_info)


        # Create order before deleting the card
        order = Order.objects.create(
            card_data=decrypted_card_info,
            card_price=card_price,
            buyer=user,
            seller=card.uploaded_by,
            category=card.card_base,
            status=card.card_refund_status,
        )

        # Handle Buy & Check scenario
        if card.card_refund_status == CreditCardInformation.REFUND_WITHOUT_CHECK_TIME:
            # If Buy & Check, initiate async check And Before calling check_card.delay, record the check attempt
            OrderCheck.objects.create(order=order, buyandcheck=True, checker_name='LuxChecker')
            
            # send card to check
            check_card.delay(user.id, [order.id])

        # Delete the card for all statuses, including Buy & Check and others, to avoid keeping sold cards
        card.delete()
        return {'order_status': 'Ready', 'card_data': order.card_data, 'new_balance': user.profile.balance}
        
