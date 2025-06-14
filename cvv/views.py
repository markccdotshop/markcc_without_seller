from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CreditCardInformation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import CvvFilter
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from category.models import Category
from sellers.models import Seller
from django.db.models import Q
from django.db import IntegrityError
from core_services.process_purchase_task import process_purchase_task
from django.utils.html import escape
from celery.result import AsyncResult
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Helper function to build json responses
def build_json_response(status="Error", message="", status_code=400, data=None):
    response = {
        'status': escape(status),
        'message': escape(message)
    }
    if data is not None:
        response.update({'data': data})
    return JsonResponse(response, status=status_code)

# logger.warning(f'An unexpected error occurred in get_bases_for_seller: {e}', exc_info=True)

@login_required(login_url='login')
def cvv(request):
    try:
        # Retrieve CVV list excluding those in carts and filtering for published bases
        cvv_list = CreditCardInformation.objects.filter(
            in_cart=False, 
            card_base__category_status='published', # Ensure the category is published by seller
            card_base__active=True, # Ensure the category is activated by the administrator
            card_base__seller__is_active=True  # Ensure the seller is active
        ).order_by('-id')

        
        # Apply filters based on the request
        cvv_filter = CvvFilter(request.GET, queryset=cvv_list)
        filtered_cvv = cvv_filter.qs

        # Paginate the filtered CVV list
        paginator = Paginator(filtered_cvv, 10)  # Show 10 CVVs per page
        page = request.GET.get('page', 1)

        try:
            cards = paginator.page(page)
        except PageNotAnInteger:
            cards = paginator.page(1)
        except EmptyPage:
            cards = paginator.page(paginator.num_pages)

        # Get all active published bases
        published_bases = Category.objects.filter(
            category_status='published',
            active=True,
            seller__is_active=True
        )


        # Prepare the context for rendering
        context = {
            'filter': cvv_filter,
            'cards': cards,
            'bases': published_bases,
        }

        # Handle reset filter action
        if 'reset' in request.GET:
            return redirect('cvv')

        # Render the CVV page with the context
        return render(request, 'cvv/cvv.html', context)

    except Exception as e:
        messages.error(request, "An error occurred while loading the page.")
        return redirect('cvv')




@login_required(login_url='login')
def search(request):
    try:
        # Retrieve CVV list excluding those in carts and filtering for published bases
        cvv_list = CreditCardInformation.objects.filter(
            in_cart=False, 
            card_base__category_status='published', # Ensure the category is published by seller
            card_base__active=True, # Ensure the category is activated by the administrator
            card_base__seller__is_active=True  # Ensure the seller is active
        ).order_by('-id')

        
        # Apply filters based on the request
        cvv_filter = CvvFilter(request.GET, queryset=cvv_list)
        filtered_cvv = cvv_filter.qs

        # Paginate the filtered CVV list
        paginator = Paginator(filtered_cvv, 10)  # Show 10 CVVs per page
        page = request.GET.get('page', 1)

        try:
            cards = paginator.page(page)
        except PageNotAnInteger:
            cards = paginator.page(1)
        except EmptyPage:
            cards = paginator.page(paginator.num_pages)

        # Get all active published bases
        published_bases = Category.objects.filter(
            category_status='published',
            active=True,
            seller__is_active=True
        )


        # Prepare the context for rendering
        context = {
            'filter': cvv_filter,
            'cards': cards,
            'bases': published_bases,
        }

        # Handle reset filter action
        if 'reset' in request.GET:
            return redirect('cvv')

        # Render the CVV page with the context
        return render(request, 'cvv/search.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred while loading the page. {e}")
        return redirect('cvv')



@login_required(login_url='login')
def get_bases_for_seller(request):
    seller_id = request.GET.get('seller_id', '').strip()
    
    # Validate that seller_id is a valid integer
    try:
        seller_id = int(seller_id)
    except ValueError as e:  # Catch the exception as 'e'
        logger.warning(f'Invalid seller_id received in get_bases_for_seller: {e}', exc_info=False)
        return JsonResponse({'error': 'Select Seller.'}, status=400)
    
    # Ensuring seller_id is positive
    if seller_id <= 0:
        return JsonResponse({'error': 'Invalid seller ID.'}, status=400)

    try:
        # Using 'Q' object for complex querying if needed in the future
        bases = Category.objects.filter(
            Q(seller__id=seller_id) & 
            Q(category_status='published') & 
            Q(active=True)).values('id', 'name', 'quality_indicator')
        
        if not bases:
            return JsonResponse({'message': 'No bases found for this seller.'}, status=404)
        
        bases_data = [
            {
                'id': base['id'],
                'display': f"{base['name']}--{base['quality_indicator']}%" if base['quality_indicator'] else f"{base['name']}--N/A"
            }
            for base in bases
        ]
        return JsonResponse(bases_data, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'This seller does not exist or has no bases.'}, status=404)
    except Exception as e:
        # Logging the exception can be done here
        logger.warning(f'An unexpected error occurred in get_bases_for_seller: {e}', exc_info=True)
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)



@login_required(login_url='login')
def buycc(request, id):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return build_json_response(message='Method not allowed!', status_code=405)
    
    try:
        card_exists = CreditCardInformation.objects.get(id=id, in_cart=False)
    
        if not card_exists:
            return JsonResponse({'message': 'Card not available!'}, status=404)

        if request.user.profile.balance < card_exists.card_price:
            return build_json_response(message='Insufficient balance.', status_code=200)
        
        task = process_purchase_task.delay(user_id=request.user.id, card_id=id)
        # Store task ID in session for later status checks
        user_tasks = request.session.get('user_tasks', [])
        user_tasks.append(task.id)
        request.session['user_tasks'] = user_tasks
        request.session.modified = True
        return JsonResponse({'message': 'Your purchase is being processed', 'taskId': task.id}, status=202)
    
    except CreditCardInformation.DoesNotExist:
        return build_json_response(message='Card not available!', status_code=404)
    except IntegrityError:
        logger.exception('Integrity error occurred in cvv buy')
        return build_json_response(message='Transaction failed due to a conflict.', status_code=409)
    except Exception as e:
        logger.exception('An unexpected error occurred in cvv buy')
        return build_json_response(message='An unexpected error occurred.', status_code=500)


@login_required(login_url='login')
def purchase_status(request, task_id):
    try:
        user_tasks = request.session.get('user_tasks', [])
        
        if task_id not in user_tasks:
            return JsonResponse({'message': "You do not have permission to access this task."}, status=403)
        
        task_result = AsyncResult(task_id)
        if task_result.ready():
            result = task_result.get()
            if result is not None:
                order_status = result.get('order_status', 'Unknown status')
                card_data = result.get('card_data', '')
                new_balance = result.get('new_balance', 'Unknown balance')
                return JsonResponse({
                    'status': 'success',
                    'data': {'order_status': order_status, 'card_data': card_data, 'new_balance': new_balance}
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Task completed but no result was returned.'}, status=204)
        else:
            return JsonResponse({'status': 'processing'}, status=202)
    except Exception as e:
        logger.error(f'Error checking purchase status: {e}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request.'}, status=500)

@staff_member_required
def expired(request):
    try:
        total_cvv = None
        total_count = None

        if request.method == 'POST':
            month = request.POST.get('month')
            year = request.POST.get('year')

            if month == '':
                messages.info(request, 'Enter Month')
                return redirect('')
            if year == '':
                messages.info(request, 'Enter Year')
                return redirect('')

            total_cvv = CreditCardInformation.objects.filter(card_expiry_month=month, card_expiry_year=year).all()
            total_count = CreditCardInformation.objects.filter(card_expiry_month=month, card_expiry_year=year).all().count()
            

        return render(request, 'category/expired.html', {'total_cvv': total_cvv,'total_count':total_count})
    except:
       return redirect('/cvv/expired/')
@staff_member_required
def delete_all_expired(request):
    try:
        if request.method == 'POST':
            card_ids = request.POST.get('card_ids')
            card_ids_list = card_ids.split(',') if card_ids else []
            
            # Delete the expired cards based on their IDs
            CreditCardInformation.objects.filter(id__in=card_ids_list).delete()
        
        # Redirect to the 'expired' page
        messages.success(request, 'Expired Card Deleted')
        return redirect('expired')
    except:
        return redirect('/cvv/expired/')

#deleting expired card