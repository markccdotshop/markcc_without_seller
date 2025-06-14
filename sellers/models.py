from django.db import models
from users.models import Profile


class Seller(models.Model):
    ICQ = 'ICQ'
    JABBER = 'JABBER'
    TELEGRAM = 'TELEGRAM'
    
    CONTACT_METHODS = [
        (ICQ, 'ICQ'),
        (JABBER, 'JABBER'),
        (TELEGRAM, 'TELEGRAM'),
    ]

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='seller')
    seller_store_name = models.CharField(max_length=100, unique=True)
    seller_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    contact_methods = models.CharField(max_length=20, choices=CONTACT_METHODS) 
    contact_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.profile} - {self.seller_store_name}"



class SellerSellsHistory(models.Model):

    CARD_DUMPS = 'CARD_DUMPS'
    CARD_CVV = 'CARD_CVV'
    CARDING_METHOD = 'CARDING_METHOD'
    SSN = 'SSN'
    CARD_SCAN_DESIGNER = 'CARD_SCAN_DESIGNER'
    
    ITEM_TYPE_CHOICES = [
        (CARD_DUMPS, 'DUMPS'),
        (CARD_CVV, 'CVV'),
        (CARDING_METHOD, 'METHOD'),
        (SSN, 'SSN'),
        (CARD_SCAN_DESIGNER, 'CARD SCAN'),
    ]

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='sell_history')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES) 
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_placed_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.seller.profile.user.username} - Sales: {self.item_type}"



class SellerTransactionHistory(models.Model):
    BTC = 'btc'
    LTC = 'ltc'
    DOGE = 'doge'
    CURRENCY_TYPE_CHOICES = [
        (BTC, 'Bitcoin'),
        (LTC, 'Litecoin'),
        (DOGE, 'Dogecoin'),
    ]

    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSACTION_TYPE_CHOICES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]

    TRANSACTION_PENDING = 'pending'
    TRANSACTION_APPROVED = 'approved'
    TRANSACTION_DECLINED = 'declined'
    TRANSACTION_STATUS_CHOICES = [
        (TRANSACTION_PENDING, 'Pending'),
        (TRANSACTION_APPROVED, 'Approved'),
        (TRANSACTION_DECLINED, 'Declined'),
    ]

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default=TRANSACTION_PENDING)
    seller_current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    seller_previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transaction_created_timestamp = models.DateTimeField(auto_now_add=True)
    transaction_approval_timestamp = models.DateTimeField(null=True, blank=True)
    withdrawal_currency_type = models.CharField(max_length=10, choices=CURRENCY_TYPE_CHOICES, default=BTC)

    def __str__(self):
        return f"{self.seller.profile.user.username} - {self.transaction_type}: {self.amount}"
