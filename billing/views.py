from django.shortcuts import render, redirect
from billing.models import Billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from crypto_configs.models import Cryptocurrency
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse,HttpResponseForbidden
from .task import check_balance_task 
from celery.result import AsyncResult
from django.http import HttpResponse


@login_required(login_url='login')
def billing(request):
    # Retrieve all billing addresses for the logged-in user, sorted by most recent
    try:
        billing_address = Billing.objects.filter(user=request.user).order_by('-id')

        context = {
            'billing_address': billing_address,
        }
        return render(request, 'billing/billing.html', context)
    except:
        return HttpResponse('Try Again later')

@login_required(login_url='login')
def getaddress(request, coin_symbol):
    try:
        coin_symbol = coin_symbol.upper() #in the html, used small letter for coin name.
        # Verify if the user has already generated three unused addresses for the specified coin
        user_addresses = Billing.objects.filter(user=request.user, coin_symbol=coin_symbol, fund_status=False)
        if user_addresses.count() >= 3:
            messages.error(request, f'You already have three unused addresses for {coin_symbol}. Please use one of them before generating a new one.')
            return redirect(reverse('billing'))  # Redirect the user to the billing page
        
        # get the first unassigned bitcoin address
        
        coin_address = Cryptocurrency.objects.filter(coin_name=coin_symbol, address_status=False).first()

        if coin_address:
            # create new billing object
            billing_address = Billing(user=request.user, address=coin_address, coin_symbol=coin_symbol)
            billing_address.save()

            # mark the bitcoin address as assigned
            coin_address.address_status = True
            coin_address.assigned_to = request.user
            coin_address.assigned_date = timezone.now()
            coin_address.save()

            messages.success(request, f'{coin_symbol} Address generated successfully!')

        else:
            # No coin address availabe in the database
            messages.error(request, 'System is busy now. Try again later.')
        return redirect(reverse('billing'))
    except Exception as e:
        messages.error(request, f'Error generating {coin_symbol} address:')
        return redirect(reverse('billing'))


@login_required(login_url='login')
def check_balance(request, id):
    try:
        if request.method == 'POST':
            billing = Billing.objects.filter(id=id, user=request.user).first()
            if billing and not billing.fund_status:

                task = check_balance_task.delay(billing.id, request.user.id, billing.coin_symbol.lower())

                # Save the task ID in the user's session
                user_tasks = request.session.get('user_tasks', [])
                user_tasks.append(str(task.id))
                request.session['user_tasks'] = user_tasks

                return JsonResponse({'task_id': str(task.id)})
            return JsonResponse({'error': 'Invalid request'}, status=400)
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    except:
        return HttpResponse('Try Again Later')


@login_required(login_url='login')
def task_status(request, task_id):
    try:
        user_tasks = request.session.get('user_tasks', [])

        if task_id not in user_tasks:
            return HttpResponseForbidden("You do not have permission to access this task.")

        task_result = AsyncResult(task_id)
        if task_result.ready():
            return JsonResponse({'status': task_result.status, 'result': task_result.result})
        return JsonResponse({'status': task_result.status})
    except:
        return HttpResponse('Try Again Later')