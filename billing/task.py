from celery import shared_task
from billing.models import Billing
from blockcypher import get_address_full
import requests
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from users.models import Transaction


# API settings
api_key = '$2y$10$4lUKsYuBTSZ2aY5zGGNWj.fWmgrqVNzdHgkLmIHU8/AW6Fr3nfOzW'
password = 'iq918864'
#email mazharul

headers = {
    'Host': 'coinremitter.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-GB,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'close',
    'Referer': '',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

@shared_task
def check_balance_task(billing_id, user_id, coin_symbol):
    try:
        with transaction.atomic():
            try:
                billing = Billing.objects.select_for_update().get(id=billing_id, user_id=user_id, fund_status=False)
            except:
                return "No billing record found."

            address = billing.address
            
            # Get all transactions for the specific coin
            transactions = get_address_full(address, coin_symbol)
            total_received = transactions.get('total_received', 0)

            # Convert received amount to respective units based on the coin
            total_units = convert_to_units(total_received, coin_symbol)

            # Fetch coin USD rate
            check_coin_usd_rate = requests.get('https://coinremitter.com/api/v3/get-coin-rate', headers=headers)
            
            if check_coin_usd_rate.status_code != 200:
                return f"Error fetching {coin_symbol.upper()} price"

            get_coin_usd_rate = check_coin_usd_rate.json()
            coin_usd_price = Decimal(get_coin_usd_rate['data'][coin_symbol.upper()]['price'])

            # Calculate total USD value and apply a 5% deduction
            total_price_in_usd = total_units * coin_usd_price
            with_percentage = total_price_in_usd * Decimal(0.95)

            # Process payment if conditions are met
            if not billing.fund_status:
                if total_units > 0:
                    billing.crypto_amount = total_units
                    billing.usd_amount = with_percentage
                    billing.fund_status = True
                    billing.received_date = timezone.now()
                    billing.save()

                    user = User.objects.select_for_update().get(id=user_id)
                    user.profile.balance += Decimal(with_percentage)
                    user.profile.save()

                    # Log the transaction
                    Transaction.objects.create(
                        user=user,
                        amount=total_price_in_usd,
                        transaction_type='Deposit',
                        description=f"Deposit"
                    )
                    return "Payment Received!"
                else:
                    return "No Funds!"
            else:
                return "Funds from this address have already been deposited!"
    
    except Exception as e:
        return "An error occurred during the task execution."

# Function to convert received amount to respective units based on the coin
def convert_to_units(total_received, coin_symbol):
    if coin_symbol in ['btc', 'ltc', 'dash', 'doge']:
        return Decimal(total_received) / Decimal(100000000)
    elif coin_symbol == 'xmr':
        return Decimal(total_received) / Decimal(1000000000000)
    elif coin_symbol == 'eth':
        return Decimal(total_received) / Decimal(1000000000000000000)
    else:
        raise ValueError("Unsupported coin symbol")
