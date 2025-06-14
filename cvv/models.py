from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from category.models import Category
from sellers.models import Seller
class CreditCardInformation(models.Model):
    PUBLISHED = 'published'
    UNPUBLISHED = 'unpublished'

    STATUS_CHOICES = [
        (PUBLISHED, 'Published'),
        (UNPUBLISHED, 'Unpublished'),
    ]

    REFUND_WITH_CHECK_TIME = 1
    REFUND_WITHOUT_CHECK_TIME = 2
    NO_REFUND = 7

    REFUND_CHOICES = (
        (REFUND_WITH_CHECK_TIME, 'With CheckTime'),
        (REFUND_WITHOUT_CHECK_TIME, 'Buy & Check'),
        (NO_REFUND, 'No Refund'),
    )

    unique_card_identifier = models.CharField(unique=True, max_length=100, verbose_name="Unique Card Identifier")
    card_info = models.CharField(max_length=500, null=False, blank=False, verbose_name="Card Information")
    card_bin = models.CharField(max_length=50, null=False, blank=False, verbose_name="Card BIN")
    card_expiry_month = models.IntegerField(null=False, blank=False, verbose_name="Card Expiry Month")
    card_expiry_year = models.IntegerField(null=False, blank=False, verbose_name="Card Expiry Year")
    card_holder_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card Holder Name")
    card_city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card City")
    card_state = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card State")
    card_zip_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card ZIP Code")
    card_country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Card Country")
    card_brand = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card Brand")
    card_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card Type")
    card_level = models.CharField(max_length=50, null=True, blank=True, verbose_name="Card Level")
    card_bank = models.CharField(max_length=200, null=True, blank=True, verbose_name="Card Bank")
    card_base = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Base Name')
    card_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Card Price")
    card_publish_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=UNPUBLISHED, verbose_name="Card Published Status")
    card_category_published = models.BooleanField(default=False)
    card_refund_status = models.PositiveSmallIntegerField(choices=REFUND_CHOICES, default=REFUND_WITH_CHECK_TIME, verbose_name="Refund Status")
    uploaded_by = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='uploaded_cards', verbose_name="Uploaded By")
    uploaded_date = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded Date")
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="Published Date")
    # cart
    in_cart = models.BooleanField(default=False)
    cart_added_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Credit Card Information"
        verbose_name_plural = "Credit Card Information"
    
    def __str__(self):
        return f"Card - {self.unique_card_identifier} - Uploaded By: {self.uploaded_by}"
        
    def clean(self):
        card_month_str = str(self.card_expiry_month).lstrip('0')  # Remove leading zeros if any
        if not (card_month_str.isdigit() and 1 <= int(card_month_str) <= 12):
            raise ValidationError("Month should be between 01 and 12.")
        if self.card_expiry_year < 2023:  # Assuming we're in 2023
            raise ValidationError("Year should be 2023 or later.")
