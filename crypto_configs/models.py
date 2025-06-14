from django.db import models
from django.contrib.auth.models import User

class Cryptocurrency(models.Model):
    COIN_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('LTC', 'Litecoin'),
        ('ETH', 'Ethereum'),
        ('DOGE', 'Dogecoin'),
        ('DASH', 'Dashcoin'),
    ]
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_coins')
    coin_name = models.CharField(choices=COIN_CHOICES, max_length=5)
    address = models.CharField(unique=True, max_length=100)
    address_status = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_coins')
    upload_date = models.DateTimeField(auto_now_add=True)
    assigned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.address

