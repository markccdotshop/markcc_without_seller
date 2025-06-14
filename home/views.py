from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from category.models import Category
from django.contrib.auth.decorators import login_required
from itertools import groupby
from django.http import HttpResponse

@login_required(login_url='login')
def home(request):
    try:
        product_updates = Category.objects.filter(active=True, category_status='published', seller__is_active=True).order_by('-published_date')

        # Paginator setup
        paginator = Paginator(product_updates, 90)  # Show 20 updates per page
        page_number = request.GET.get('page')
        try:
            product_updates_page = paginator.page(page_number)
        except PageNotAnInteger:
            product_updates_page = paginator.page(1)
        except EmptyPage:
            product_updates_page = paginator.page(paginator.num_pages)

        # Group by date after pagination
        product_updates_grouped = []
        for date, items in groupby(product_updates_page, key=lambda x: x.published_date):
            product_updates_grouped.append((date, list(items)))

        context = {
            'product_updates_page': product_updates_page,
            'product_updates_grouped': product_updates_grouped,
        }

        return render(request, 'index.html', context)
    except:
        return HttpResponse('Try again later!')



@login_required(login_url='login')
def faq(request):
    return render(request,'faq/faq.html')
