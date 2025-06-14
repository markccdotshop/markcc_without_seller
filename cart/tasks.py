from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CreditCardInformation

@shared_task
def clear_expired_cart_items():
    expiration_time = 10  # 1 minute for this example, adjust as needed
    expired_time = timezone.now() - timedelta(minutes=expiration_time)

    # Query for expired cart items
    expired_carts = Cart.objects.filter(added_date__lt=expired_time).select_related('credit_card')
    for cart_item in expired_carts:
        # Update the related CreditCardInformation entry
        if cart_item.credit_card.in_cart:
            cart_item.credit_card.in_cart = False
            cart_item.credit_card.cart_added_date = None
            cart_item.credit_card.save()
        
        # Delete the cart item
        cart_item.delete()

    # Optionally, handle any CreditCardInformation entries that are marked as in_cart but not linked to a cart item
    orphaned_cc = CreditCardInformation.objects.filter(in_cart=True, cart_added_date__lt=expired_time).exclude(cart_items__isnull=False)
    for cc in orphaned_cc:
        cc.in_cart = False
        cc.cart_added_date = None
        cc.save()
