from django.shortcuts import redirect, render
from .models import Cryptocurrency
from django.utils import timezone
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from billing.models import Billing
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

@staff_member_required 
def cryptocurrency(request):
    try:
        crypto_address = Cryptocurrency.objects.all().order_by('-address_status')
        
        paginator = Paginator(crypto_address, 10)  # Show 10 address per page
        page_number = request.GET.get('page')

        try:
            crypto_address = paginator.page(page_number)
        except PageNotAnInteger:
            crypto_address = paginator.page(1)
        except EmptyPage:
            crypto_address = paginator.page(paginator.num_pages)

        return render(request, 'seller/cryptocurrency/crypto.html', {'crypto_address': crypto_address})

    except Exception as e:
        return HttpResponse('try again later!') #we must be create a error page here for error redirection


@staff_member_required
def upload_address(request):
    if request.method == 'POST':
        coin_name = request.POST.get('coin_name')
        if not coin_name:
            messages.error(request, 'Select a coin!')
            return redirect('crypto/config')

        try:
            duplicate_addresses = []
            addresses_uploaded = 0

            bulk_addresses = request.POST.get('bulk_addresses')
            if bulk_addresses:
                addresses = bulk_addresses.strip().split("\n")
                for address in addresses:
                    address = address.strip()
                    if Cryptocurrency.objects.filter(address=address, coin_name=coin_name).exists():
                        duplicate_addresses.append(address)
                    else:
                        coin = Cryptocurrency(
                            uploaded_by=request.user,
                            coin_name=coin_name,
                            address=address,
                            upload_date=timezone.now()
                        )
                        coin.save()
                        addresses_uploaded += 1
            else:
                messages.error(request, 'Enter Address!')
                return redirect('crypto/config')


            if addresses_uploaded > 0:
                messages.success(request, f'{addresses_uploaded} addresses uploaded!')
            if duplicate_addresses:
                messages.error(request, f'Duplicate addresses: {", ".join(duplicate_addresses)}')

            return redirect('crypto/config')

        except Exception as e:
            messages.error(request, f'Error uploading: {e}')
            return redirect('crypto/config')

    else:
        messages.error(request, 'Invalid Request!')
        return redirect('crypto/config')


@staff_member_required 
def fund_received(request):
    try:
        received_address = Billing.objects.filter(fund_status=True).order_by('-id')
        

        paginator = Paginator(received_address, 10)  # Show 10 address per page
        page_number = request.GET.get('page')

        try:
            received_address = paginator.page(page_number)
        except PageNotAnInteger:
            received_address = paginator.page(1)
        except EmptyPage:
            received_address = paginator.page(paginator.num_pages)

        return render(request, 'seller/cryptocurrency/received_address.html', {'received_address': received_address})

    except Exception as e:
        return HttpResponse('try again later!') #we must be create a error page here for error redirection
        