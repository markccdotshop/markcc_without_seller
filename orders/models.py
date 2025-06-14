from django.db import models
from django.contrib.auth import get_user_model
from category.models import Category
from sellers.models import Seller
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        JUST_BOUGHT = '1', _('Bought')
        CHECKING = '2', _('Checking')
        APPROVED = '3', _('Approved')
        DECLINED = '4', _('Declined')
        FIFTY_CODE = '5', _('Fifty Code')
        TIME_OUT = '6', _('Time Out')
        NO_REFUND = '7', _('No Refund')

    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Buyer"))
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Seller"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Category"))
    card_data = models.TextField(verbose_name=_("Card Data"))
    card_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Card Price"))
    status = models.CharField(max_length=2, choices=OrderStatus.choices, default=OrderStatus.JUST_BOUGHT, verbose_name=_("Order Status"))
    order_placed_at = models.DateTimeField(default=now, verbose_name=_("Order Placed At"))
    order_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-order_placed_at']

    def __str__(self):
        return f"Order {self.id} - {self.buyer.username if self.buyer else 'Deleted User'}"

class OrderCheck(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='checks')
    buyandcheck = models.BooleanField(default=False)
    checker_name = models.CharField(max_length=100, default='LuxChecker')  # Example checker name
    auth_message = models.CharField(max_length=255, null=True, blank=True)
    auth_code = models.CharField(max_length=50, null=True, blank=True)
    credits = models.CharField(max_length=100, null=True, blank=True)
    response_raw = models.TextField("Raw Checker Response", blank=True, null=True)  # Store raw response
    checked_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Check for Order {self.order.id} - {self.checked_at.strftime('%Y-%m-%d %H:%M')}"

class OrderHistory(models.Model):
    order_id = models.IntegerField(verbose_name=_("Original Order ID"))
    buyer_username = models.CharField(max_length=150, verbose_name=_("Buyer Username"))
    seller_id = models.IntegerField(verbose_name=_("Seller ID"))
    category_name = models.CharField(max_length=255, verbose_name=_("Category Name"))
    card_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Card Price"))
    final_status = models.CharField(max_length=50, verbose_name=_("Final Status"))
    archived_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Archived At"))

    class Meta:
        verbose_name = _("Order History")
        verbose_name_plural = _("Order Histories")
        ordering = ['-archived_at']

    def __str__(self):
        return f"Archived Order {self.order_id} - {self.buyer_username}"
