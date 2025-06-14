from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse,HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order
from django.utils.html import escape
import logging
from .order_check_service import process_order_check

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Helper function to build json responses
def build_json_response(status="Error", message="", status_code=400, data=None):
    response = {
        'status': escape(status),
        'message': escape(message)
    }
    if data is not None:
        response.update(data)
    return JsonResponse(response, status=status_code)



@login_required(login_url='login')
def orders(request):
    try:
        get_cc_history = Order.objects.filter(buyer=request.user).select_related(
            'category', 'seller'
        ).order_by('-order_placed_at')
        

        paginator = Paginator(get_cc_history, 10)  # Show 10 orders per page
        page_number = request.GET.get('page')

        try:
            cc_info = paginator.page(page_number)
        except PageNotAnInteger:
            cc_info = paginator.page(1)
        except EmptyPage:
            cc_info = paginator.page(paginator.num_pages)

        return render(request, 'order/orders.html', {'cc_info': cc_info})

    except Exception as e:
        # Redirect or show an error message
        return HttpResponse('try again later!') #we must be create a error page here for error redirection

@login_required(login_url='login')
def check_cc(request, id):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return build_json_response(message='Method not allowed!', status_code=405)

    try:
        checker_price = Decimal('0.5')

        # Retrieve the order, ensuring it belongs to the user, is refundable, and has not been checked or finalised
        order = get_object_or_404(
            Order,
            buyer=request.user,
            id=id,
            status=Order.OrderStatus.JUST_BOUGHT,  # Assuming "JUST_BOUGHT = 1" signifies refundable
        )

        # Calculate the time elapsed since the purchase
        duration = timezone.now() - order.order_placed_at
        if duration.total_seconds() > 300:  # 5 minutes in seconds
            order.status = Order.OrderStatus.TIME_OUT # Assuming "TIME_OUT = 6" signifies time's up
            order.save()
            return build_json_response(status="TimesUp", message='Time’s up', status_code=200)

        # Check if the user has sufficient balance
        if request.user.profile.balance < checker_price:
            return build_json_response(status="LowFunds", message='Insufficient funds.', status_code=200)
        
        task = process_order_check.delay(user_id=request.user.id, order_id=order.id)
        return build_json_response(status="Success", message='Checking...', status_code=200, data={'new_balance': str(request.user.profile.balance)})    
    except Exception as e:
        logger.error(f'Error on card checking for Order ID {id}: {e}', exc_info=True)
        return build_json_response(status="Error", message='An unexpected error occurred.', status_code=500)
