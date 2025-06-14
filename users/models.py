from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # User roles
    ROLE_CHOICES = (
        ('regular', 'Regular User'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='regular')
    
    def __str__(self):
        return self.user.username
    

    def is_manager(self):
        return self.role == 'manager'

    def is_regular_user(self):
        return self.role == 'regular'

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)  # e.g., 'deposit', 'purchase', 'refund'
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)  # Optional description of the transaction

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"



