from django.db import transaction
from celery import shared_task
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import F
from orders.models import Order, OrderCheck
from .checkers.lux_checker import LuxChecker
from django.core.exceptions import ObjectDoesNotExist
from .balance_services import update_user_balance
from users.models import Transaction
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def check_card(user_id, order_ids: list):
    for order_id in order_ids:
        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(id=user_id)
                order = Order.objects.select_for_update().get(id=order_id, buyer=user,status=Order.OrderStatus.CHECKING)
                card_data_str = order.card_data
                
                checker = LuxChecker(card_data_str)
                checker_response = checker.check()

                # checker_response = {'result': 0, 'auth_message': 'Success', 'auth_code': '100', 'credits': '1'}


                # Extracting data from the response
                result = checker_response.get('result')
                auth_message = checker_response.get('auth_message', '')
                auth_code = checker_response.get('auth_code', '')
                credits = checker_response.get('credits', '')

                try:
                    order_check = OrderCheck.objects.filter(order=order).latest('checked_at')
                except ObjectDoesNotExist:
                    return  'No order found'
                

                order_check.checker_name = 'LuxChecker'
                order_check.auth_message = auth_message
                order_check.auth_code = auth_code
                order_check.credits = credits
                order_check.response_raw = str(checker_response)
                order_check.save()


                if result == 0 and auth_code in ['51', '10', '57', '63', '58', '59']:

                    # Step 1: Calculate the refund amount (50% of the order card price)
                    refund_amount = order.card_price * Decimal('0.5')

                    # Deduct checker price from user balance and update order status
                    update_user_balance(user, refund_amount, is_refund=True)
                    
                    # Update the order with the appropriate status
                    order.status = Order.OrderStatus.FIFTY_CODE
                    order.save()

                    # Log the transaction
                    Transaction.objects.create(
                        user=user,
                        amount=refund_amount,
                        transaction_type='Refund',
                        description=f"Order ID {order_id} Refunded half card price without chekcer price"
                    )

                elif result == 1:
                    order.status = Order.OrderStatus.APPROVED
                    order.save()

                    # Log the transaction
                    Transaction.objects.create(
                        user=user,
                        amount=0,
                        transaction_type='Approved',
                        description=f"Order ID {order_id} Card checked And approved."
                    )

                elif result == 0: #Card Declined
                    # Calculate the total refund amount (if the order price and checker price are to be refunded)
                    
                    if OrderCheck.objects.filter(order=order,buyandcheck=True):
                        refund_card_and_checker_price = order.card_price
                    else:
                        refund_card_and_checker_price = order.card_price + Decimal('0.5')

                    # Safely update the user's balance to reflect the refund
                    update_user_balance(user, refund_card_and_checker_price, is_refund=True)

                    # Update the order with the Declined status
                    order.status = Order.OrderStatus.DECLINED
                    order.save()

                    # Log the transaction
                    Transaction.objects.create(
                        user=user,
                        amount=refund_card_and_checker_price,
                        transaction_type='Refund',
                        description=f"Refunded for declined card, Order ID {order_id} maybe with or without chekcer fee. because of card type."
                    )
                else:
                    return "Failed to check order"
                order.save()
        except User.DoesNotExist:
            return "User ID does not exist."
        except Order.DoesNotExist:
            return "Order ID does not exist."
        except ValueError as e:
            return "Error."
        except Exception as e:
            logger.warning(f'An unexpected error occurred in card checking: {e}', exc_info=True)
            return "Unexpected error."
