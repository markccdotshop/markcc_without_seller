from django.db import models
from django.contrib.auth.models import User
from cvv.models import CreditCardInformation

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    credit_card = models.ForeignKey(CreditCardInformation, on_delete=models.CASCADE, related_name='cart_items')
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'credit_card')

    def __str__(self):
        return f"Cart item for {self.customer.username} - Card: {self.credit_card.unique_card_identifier}"

