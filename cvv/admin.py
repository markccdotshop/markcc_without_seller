from django.contrib import admin
from cvv.models import CreditCardInformation

class CvvAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'unique_card_identifier', 'card_info', 'card_bin', 'card_expiry_month',
        'card_expiry_year', 'card_holder_name', 'card_city', 'card_state', 'card_zip_code',
        'card_country', 'card_brand', 'card_type', 'card_level', 'card_bank', 'card_base',
        'card_refund_status', 'card_price', 'card_publish_status', 'uploaded_by',
        'uploaded_date', 'published_date', 'in_cart', 'cart_added_date',
    )

admin.site.register(CreditCardInformation, CvvAdmin)
