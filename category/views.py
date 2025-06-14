from django.shortcuts import render, redirect
from .forms import CategoryForm, CardUploadForm
from .models import Category
from .task import process_batch
from .task import delete_base_and_cvv
from django.http import JsonResponse
from django.contrib import messages
from sellers.models import Seller
from sellers.decorators import seller_required
from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

# Helper function to build json responses
def build_json_response(message='', status_code=200):
    return JsonResponse({'message': message}, status=status_code)

@seller_required
def category(request):
   
   return HttpResponse('category')


########### Create And View Bases ###########

@seller_required
def create_and_view_categories(request):
    try:
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            
            if form.is_valid():
                # Retrieve the Seller instance for the logged-in user
                seller_instance, created = Seller.objects.get_or_create(profile=request.user.profile)
                Category.objects.create(
                    name=form.cleaned_data['category_name'],
                    quality_indicator=form.cleaned_data['category_ratio'],
                    category_status='unpublished',  # Set status to 'unpublished' by default
                    seller=seller_instance,
                )
                
                messages.success(request, f"Base Created successfully.")
                return redirect('create_view_category')  # Redirect to this view to see the list of categories
        else:
            form = CategoryForm()  # An unbound form for a GET request

        category_list = Category.objects.filter(seller__profile=request.user.profile).order_by('-id')
        

        upload_card_form = CardUploadForm()

        context = {
            'form': form,  # The empty form for a GET request or bound form with data for a POST request
            'upload_card_form':upload_card_form,
            'category_list': category_list,  # The list of categories for viewing
        }

        return render(request, 'category/create_category.html', context)
    except:
        return HttpResponse('Try again later')


########### Change Category Published status for seller###########

@seller_required
def publish_category(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        category.category_status = 'published'
        category.save()
        messages.success(request, f"The category '{category.name}' has been published successfully.")
        return redirect('create_view_category')
    except:
        return HttpResponse('Try again later')

@seller_required
def unpublish_category(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        category.category_status = 'unpublished'
        category.save()
        messages.error(request, f"The category '{category.name}' has been unpublished and is no longer displayed on the CVV shop.")
        return redirect('create_view_category')
    except:
        return HttpResponse('Try again later')


########### Delete Category ###########
@seller_required
def delete_base(request, base_id):
    try:
        if request.method == 'POST':
            # Trigger the asynchronous task
            delete_base_and_cvv.delay(base_id)
            messages.error(request, "The base and related CVVs are being deleted. This may take some time.")
            return redirect('create_view_category')
        else:
            messages.error(request, 'Method not allowed!')
            return redirect('create_view_category')
    except:
        return HttpResponse('Try again later')

########### Upload cards ###########
@seller_required
def upload_cards(request):
    try:
        if request.method == 'POST':
            form = CardUploadForm(request.POST)
            if form.is_valid():
                base_id = form.cleaned_data['base'].id
                refund = form.cleaned_data['refund']
                usprice = form.cleaned_data['usprice']
                nonusprice = form.cleaned_data['nonusprice']
                cards = form.cleaned_data['cards'].strip()

                try:
                    # Retrieve the seller associated with the request user
                    seller = Seller.objects.get(profile__user=request.user)

                    if not base_id:
                        return JsonResponse({'error': 'Empty input! Please select Base name.', 'status': 'error'}, status=400)
                    
                    if not usprice:
                        return JsonResponse({'error': 'Empty input! Please select Price.', 'status': 'error'}, status=400)
                    
                    if not refund:
                        return JsonResponse({'error': 'Empty input! Please select Refund Type.', 'status': 'error'}, status=400)

                    if not cards:
                        return JsonResponse({'error': 'Empty input! Please provide card data.', 'status': 'error'}, status=400)

                    # Split the card data into lines and group them into batches
                    split_new_line = cards.split('\n')
                    batch_size = 50
                    card_batches = [split_new_line[i:i + batch_size] for i in range(0, len(split_new_line), batch_size)]

                    # Process each batch of cards using Celery
                    task_ids = []
                    for batch in card_batches:
                        task = process_batch.delay(seller.id, batch, base_id, refund, usprice, nonusprice)
                        task_ids.append(task.id)

                    if task_ids:
                        return JsonResponse({'message': 'Data uploading started successfully. Processing in background.', 'task_ids': task_ids, 'status': 'success'}, status=200)
                    else:
                        return JsonResponse({'error': 'No tasks were created. Please check your input.', 'status': 'error'}, status=500)

                except Seller.DoesNotExist:
                    return JsonResponse({'error': 'Seller not found. Please ensure you are registered as a seller.', 'status': 'error'}, status=404)
                except Exception as e:
                    # Log the exception for debugging purposes
                    return JsonResponse({'error': 'An unexpected error occurred.', 'status': 'error'}, status=500)
            else:
                # Handle form errors
                return JsonResponse({'errors': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Method not allowed!', 'status': 'error'}, status=405)
    except:
        return HttpResponse('Try again later')

    