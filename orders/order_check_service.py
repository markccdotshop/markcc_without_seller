from core_services.check_services import check_card
from users.models import Transaction
from decimal import Decimal
from celery import shared_task
from .models import Order, OrderCheck  
from core_services.balance_services import update_user_balance
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging
logger = logging.getLogger(__name__)

@shared_task
def process_order_check(user_id, order_id):
    checker_price = Decimal('0.5')
    
    # Retrieve user and order instances using their IDs
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)
    
    try:
        order = get_object_or_404(
            Order,
            buyer=user,
            id=order_id,
            status=Order.OrderStatus.JUST_BOUGHT,  # Assuming "JUST_BOUGHT = 1" signifies refundable
        )
        # Update the order status to CHECKING
        order.status = Order.OrderStatus.CHECKING
        order.save()

        with transaction.atomic():
            # Deduct checker price from user balance
            update_user_balance(user, amount=checker_price, is_refund=False)  # Assuming update_user_balance handles negative amounts for deductions
            
            # Record the check attempt
            OrderCheck.objects.create(order=order, checker_name='LuxChecker')
            

            # Log the transaction
            Transaction.objects.create(
                user=user,
                amount=-checker_price,  # Assuming this should be negative to indicate a deduction
                transaction_type='Checker Price',
                description=f"Order ID {order_id} Charged checker price"
            )
            
            # Asynchronously process the card check
            check_card.delay(user.id, [order_id])  # Ensure check_card task is expecting IDs or update accordingly
    except Exception as e:
        logger.error(f'Error processing order check for Order ID {order_id}: {e}', exc_info=True)