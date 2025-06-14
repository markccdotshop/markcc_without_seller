from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category
from sellers.models import Seller

class SellerStoreNameFilter(admin.SimpleListFilter):
    title = _('seller store name')
    parameter_name = 'seller_store_name'

    def lookups(self, request, model_admin):
        sellers = Seller.objects.all()
        return [(seller.id, seller.seller_store_name) for seller in sellers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(seller__id=self.value())
        return queryset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_seller', 'active', 'active_status', 'category_status', 'quality_indicator_display', 'cards_count', 'created_date', 'published_date')
    list_filter = ('active', 'category_status', SellerStoreNameFilter, 'created_date', 'published_date')
    search_fields = ('name', 'seller__seller_store_name')  # Ensure your Seller model has a 'seller_store_name' field
    date_hierarchy = 'created_date'
    actions = ['make_published', 'make_unpublished']
    list_editable = ('active', 'category_status')
    list_per_page = 25

    def display_seller(self, obj):
        return obj.seller.seller_store_name
    display_seller.short_description = 'Seller Store Name'
    
    def active_status(self, obj):
        return "Yes" if obj.active else "No"
    active_status.short_description = "Is Active?"
    
    def quality_indicator_display(self, obj):
        return obj.quality_indicator if obj.quality_indicator else "N/A"
    quality_indicator_display.short_description = "Quality Indicator"
    
    def cards_count(self, obj):
        return format_html(
            "<b>Available:</b> {}<br>"
            "<b>Uploaded:</b> {}<br>"
            "<b>Sold:</b> {}<br>"
            "<b>Deleted:</b> {}",
            obj.cards_available, obj.uploaded_cards, obj.sold_cards, obj.deleted_cards
        )
    cards_count.short_description = 'Cards Info'

    @admin.action(description='Mark selected categories as published')
    def make_published(self, request, queryset):
        queryset.update(category_status='published')

    @admin.action(description='Mark selected categories as unpublished')
    def make_unpublished(self, request, queryset):
        queryset.update(category_status='unpublished')

