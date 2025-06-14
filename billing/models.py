from django.db import models
from django.contrib.auth.models import User

class Billing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(unique=True, max_length=100, verbose_name="Crypto Address")
    coin_symbol = models.CharField(max_length=5, verbose_name="Coin Symbol")
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, default=0.0)
    usd_amount = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, default=0.0)
    fund_status = models.BooleanField(default=False, verbose_name="Funds Received")
    received_date = models.DateTimeField(null=True, blank=True, verbose_name="Received Date")

    class Meta:
        verbose_name_plural = "Billing Records"
        verbose_name = "Billing Record"

    def __str__(self):
        return self.address
