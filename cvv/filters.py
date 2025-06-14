from django_filters import FilterSet, CharFilter, ChoiceFilter,ModelChoiceFilter
from .models import CreditCardInformation
from django.db.models import Count
from sellers.models import Seller
from category.models import Category
# Constants for dropdown choices
CVV_BRAND = (
    ('', 'ALL'),
    ('VISA', 'VISA'),
    ('MASTERCARD', 'MASTERCARD'),
    ('AMERICAN EXPRESS', 'AMERICAN EXPRESS'),
    ('DISCOVER', 'DISCOVER'),
)
CVV_REFUND = (
    ('', 'ALL'),
    ('1', 'Refundable'),
    # ('2', 'Buy & Check'),
    ('7', 'No Refund'),
)
CVV_TYPE = (
    ('', 'ALL'),
    ('CREDIT', 'CREDIT'),
    ('DEBIT', 'DEBIT'),
)

class CvvFilter(FilterSet):
    base = ModelChoiceFilter(
        field_name='card_base',
        queryset=Category.objects.filter(
            category_status='published',
            active=True,
        ),
        label='Base',
        empty_label='ALL'
    )
    seller = ModelChoiceFilter(
        field_name='uploaded_by',
        queryset=Seller.objects.filter(
            is_active=True,
        ),
        label='Seller',
        empty_label='ALL'
    )
    bin = CharFilter(field_name='card_bin', lookup_expr='icontains')
    city = CharFilter(field_name='card_city', lookup_expr='icontains')
    state = CharFilter(field_name='card_state', lookup_expr='icontains')
    zip = CharFilter(field_name='card_zip_code', lookup_expr='icontains')
    brand = ChoiceFilter(field_name='card_brand', choices=CVV_BRAND, lookup_expr='icontains', empty_label=None)
    refund = ChoiceFilter(field_name='card_refund_status', choices=CVV_REFUND, lookup_expr='icontains', empty_label=None)
    bank = CharFilter(field_name='card_bank', lookup_expr='icontains')
    typecard = ChoiceFilter(field_name='card_type', choices=CVV_TYPE, lookup_expr='icontains', empty_label=None)
    levelcard = ChoiceFilter(field_name='card_level', lookup_expr='icontains', empty_label='ALL')
    card_country = ChoiceFilter(field_name='card_country', choices=[], lookup_expr='icontains', empty_label='ALL')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically set choices for 'levelcard' based on active sellers
        active_levels = CreditCardInformation.objects.filter(
            card_base__seller__is_active=True
        ).exclude(
            card_level__isnull=True
        ).exclude(
            card_level__exact=''
        ).distinct(
            'card_level'
        ).values_list(
            'card_level', flat=True
        )
        self.filters['levelcard'].extra['choices'] = [(level, level) for level in active_levels]

        # Dynamically set choices for 'card_country' based on active sellers
        country_choices = CreditCardInformation.objects.filter(
            card_base__seller__is_active=True
        ).values(
            'card_country'
        ).annotate(
            bin_count=Count('card_bin')
        ).distinct().values_list(
            'card_country', 'bin_count'
        )
        country_choices = [(country, f"{country} ({bin_count})") for country, bin_count in country_choices if country]
        self.filters['card_country'].extra['choices'] = country_choices



    class Meta:
        model = CreditCardInformation
        fields = ['seller', 'base', 'bin', 'city', 'state', 'zip', 'brand', 'card_country', 'refund', 'bank', 'typecard', 'levelcard']
