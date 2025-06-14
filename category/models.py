from django.db import models
from sellers.models import Seller

class Category(models.Model):
    CATEGORY_STATUS_CHOICES = [
        ('published', 'Published'),
        ('unpublished', 'Unpublished'),
    ]

    name = models.CharField(max_length=100)
    quality_indicator = models.CharField(max_length=3, null=True, blank=True, help_text="Indicator of the category's item quality or validity.")
    cards_available = models.IntegerField(default=0)
    uploaded_cards = models.IntegerField(default=0)
    sold_cards = models.IntegerField(default=0)
    deleted_cards = models.IntegerField(default=0)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name="Seller")
    active = models.BooleanField(default=False)
    category_status = models.CharField(max_length=12, choices=CATEGORY_STATUS_CHOICES, default='unpublished')
    created_date = models.DateField(auto_now_add=True)
    published_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def is_published(self):
        """A property to quickly check if a category is published."""
        return self.category_status == 'published'
