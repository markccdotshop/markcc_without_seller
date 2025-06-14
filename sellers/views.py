from .decorators import seller_required
from django.shortcuts import render, get_object_or_404
from .models import Seller
from django.db.models import Count, Sum, Q
from orders.models import Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

@seller_required
def seller_dashboard(request):
    try:
        seller = get_object_or_404(Seller, profile=request.user.profile)  # Adjust based on your user-to-seller relation
        
        # Aggregate order data
        orders_aggregated = Order.objects.filter(seller=seller).aggregate(
            total_sales=Sum('card_price'),
            total_orders=Count('id'),
            pending_orders=Count('id', filter=Q(status=Order.OrderStatus.JUST_BOUGHT)),
            approved_orders=Count('id', filter=Q(status=Order.OrderStatus.APPROVED)),
            fifty_code=Count('id', filter=Q(status=Order.OrderStatus.FIFTY_CODE)),
            declined_order=Count('id', filter=Q(status=Order.OrderStatus.DECLINED))
        )
        
        # Fetch recent orders for the seller
        recent_orders = Order.objects.filter(seller=seller).order_by('-order_placed_at')

        paginator = Paginator(recent_orders, 10)  # Show 10 orders per page
        page_number = request.GET.get('page')

        try:
            recent_orders = paginator.page(page_number)
        except PageNotAnInteger:
            recent_orders = paginator.page(1)
        except EmptyPage:
            recent_orders = paginator.page(paginator.num_pages)

        context = {
            'orders_aggregated': orders_aggregated,
            'recent_orders': recent_orders,
        }
        
        return render(request, 'seller/dashboard.html', context)
    except:
        return HttpResponse('Try again later.')