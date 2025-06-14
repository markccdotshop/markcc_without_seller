from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart
from cvv.models import CreditCardInformation
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from orders.models import Order, OrderCheck
from django.db import transaction
from django.contrib import messages
from core_services.balance_services import update_user_balance
from core_services.decryption_services import decrypt_card_info
from core_services.check_services import check_card
from users.models import Transaction
from django.utils.html import escape

# Helper function to build json responses
def build_json_response(status="error", message="", status_code=400, data=None):
    response = {
        'status': escape(status),
        'message': escape(message)
    }
    if data is not None:
        response.update(data)
    return JsonResponse(response, status=status_code)

@login_required
def add_to_cart(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    MAX_CART_ITEMS = 10  # Maximum number of items allowed in the cart
    cart_items_count = Cart.objects.filter(customer=request.user).count()
    card_ids = request.POST.getlist('card_ids[]')
    items_added, unavailable_items, over_limit_items = 0, 0, 0
    unavailable_card_ids, over_limit_card_ids = [], []

    for card_id in card_ids:
        if items_added + cart_items_count >= MAX_CART_ITEMS:
            over_limit_items += 1
            over_limit_card_ids.append(card_id)
            continue

        try:
            card = CreditCardInformation.objects.get(id=card_id)
            if not card.in_cart:
                _, created = Cart.objects.get_or_create(customer=request.user, credit_card=card)
                if created:
                    card.in_cart = True
                    card.cart_added_date = timezone.now()
                    card.save()
                    items_added += 1
            else:
                unavailable_items += 1
                unavailable_card_ids.append(card_id)
        except CreditCardInformation.DoesNotExist:
            unavailable_items += 1
            unavailable_card_ids.append(card_id)

    cart_count = Cart.objects.filter(customer=request.user).count()

    message_parts = []
    if items_added:
        message_parts.append(f"{items_added} item{'s' if items_added > 1 else ''} added to cart")
    if unavailable_items:
        message_parts.append(f"{unavailable_items} item{'s' if unavailable_items > 1 else ''} unavailable")

    message = ', '.join(message_parts) or 'No changes made to the cart'

    return JsonResponse({
        'status': 'success' if items_added > 0 else 'error',
        'message': message,
        'cart_count': cart_count,
        'unavailable_ids': unavailable_card_ids,
        'over_limit_ids': over_limit_card_ids
    })

@login_required
def cart_detail(request):
    try:
        cart_items = Cart.objects.filter(customer=request.user)
        
        # Calculate the total price of all items in the cart
        if cart_items.exists():
            cart_total = sum(item.credit_card.card_price for item in cart_items)
            return render(request, 'cart/detail.html', {'cart_items': cart_items, 'cart_total': cart_total})
        else:
            return render(request, 'cart/detail.html')
    except Exception as e:
        messages.error(request, "We encountered an error while fetching your cart items. Please try again later.")
        return render(request, 'cart/detail.html')

@login_required
def get_cart_count(request):
    try:
        cart_count = Cart.objects.filter(customer=request.user).count()
        return JsonResponse({'cart_count': cart_count})
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred while fetching the cart count.', 'cart_count': 0}, status=500)

@login_required
def remove_from_cart(request, card_id):
    try:
        # Ensure the cart item exists and belongs to the current user, then remove it
        cart_item = Cart.objects.get(credit_card__id=card_id, customer=request.user)
        cart_item.delete()

        # Update the CreditCardInformation instance
        card = CreditCardInformation.objects.get(id=card_id)
        card.in_cart = False
        card.cart_added_date = None
        card.save()

        # messages.success(request, "Item successfully removed from your cart.")
    except Cart.DoesNotExist:
        # If the cart item doesn't exist, log the error and inform the user
        messages.error(request, "The item could not be found in your cart.")
    except CreditCardInformation.DoesNotExist:
        # Handle the case where the card does not exist
        messages.error(request, "The specified card could not be found.")
    except Exception as e:
        # General exception handling for unexpected errors
        messages.error(request, "There was an error removing the item from your cart. Please try again.")
    return redirect('cart_detail')

@login_required
def remove_all(request):
    try:
        # Get all cart items for the user
        user_cart_items = Cart.objects.filter(customer=request.user)

        # Begin a transaction to ensure atomicity
        with transaction.atomic():
            # Update the in_cart status and cart_added_date of the associated credit cards
            for item in user_cart_items:
                credit_card = item.credit_card
                credit_card.in_cart = False
                credit_card.cart_added_date = None
                credit_card.save()

            # Remove all items from the user's cart
            user_cart_items.delete()

        messages.success(request, "All items have been successfully removed from your cart.")
    except Exception as e:
        messages.error(request, "An error occurred while trying to remove all items from your cart. Please try again.")
    return redirect('cart_detail')

@login_required(login_url='login')
def buycc(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'message': 'Method not allowed!'}, status=405)

    card_ids = request.POST.getlist('card_ids[]')
    total_price = Decimal('0.00')
    order_ids_for_async_check = []
    purchased_cards_info = []
    skipped_cards = []
    unavailable_or_removed_cards = []

    with transaction.atomic():
        for card_id in card_ids:
            try:
                card = get_object_or_404(CreditCardInformation, id=card_id, in_cart=True)  # Ensure the card is in cart
                card_price = card.card_price
                if request.user.profile.balance >= card_price:
                    # Update balances and delete the card from availability
                    update_user_balance(user=request.user, amount=card_price, is_refund=False)

                    # Log the transaction
                    Transaction.objects.create(
                        user=request.user,
                        amount=card_price,
                        transaction_type='Purchase',
                        description=f"Charged For {card.id} Purchase"
                    )

                    # Decrypt card information
                    decrypted_card_info = decrypt_card_info(card.card_info)

                    # Create order before deleting the card
                    order = Order.objects.create(
                        card_data=decrypted_card_info,
                        card_price=card_price,
                        buyer=request.user,
                        seller=card.uploaded_by,
                        category=card.card_base,
                        status=card.card_refund_status,
                    )
                    total_price += card_price  # Accumulate the total price of purchased cards
                    # Handle Buy & Check scenario
                    if card.card_refund_status == CreditCardInformation.REFUND_WITHOUT_CHECK_TIME:
                        order_ids_for_async_check.append(order.id)
                        # If Buy & Check, initiate async check And Before calling check_card.delay, record the check attempt
                        OrderCheck.objects.create(order=order, buyandcheck=True, checker_name='LuxChecker')
                        
                    card.delete()  # Remove the card from being available for purchase
                    purchased_cards_info.append({'id': card.id, 'price': card.card_price})
                else:
                    # Skip if insufficient balance
                    skipped_cards.append(card_id)
            except CreditCardInformation.DoesNotExist:
                unavailable_or_removed_cards.append(card_id)

    # Trigger asynchronous task if applicable
    if order_ids_for_async_check:
        # send card to check
        check_card.delay(request.user.id, order_ids_for_async_check)
        
    message, status = construct_purchase_message(purchased_cards_info, skipped_cards, unavailable_or_removed_cards)
    return JsonResponse({'message': message, 'status': status, 'total_price': str(total_price), 'new_balance': str(request.user.profile.balance)}, status=200)

def construct_purchase_message(purchased, skipped, unavailable):
    messages = []
    status = 'success'  # Default status
    if purchased:
        messages.append(f"Successfully purchased {len(purchased)} cards totaling ${sum(item['price'] for item in purchased):.2f}.")
    if unavailable:
        messages.append(f"{len(unavailable)} cards were no longer available or were removed from the cart.")
        status = 'error'
    if skipped:
        messages.append(f"Skipped {len(skipped)} cards due to insufficient balance.")
        status = 'error'
    return " ".join(messages), status


