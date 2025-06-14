from django.contrib import admin
from .models import Order, OrderCheck, OrderHistory
from django.utils.translation import gettext_lazy as _

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'category', 'card_price', 'status', 'order_placed_at', 'order_updated_at')
    list_filter = ('status', 'seller__seller_store_name', 'buyer__username', 'category__name', 'order_placed_at')
    search_fields = ('id', 'buyer__username', 'seller__seller_store_name', 'category__name', 'card_data')
    list_editable = ('status',)
    date_hierarchy = 'order_placed_at'
    ordering = ('-order_placed_at',)
    raw_id_fields = ('buyer', 'seller', 'category')
    actions = ['mark_as_just_bought', 'mark_as_checking', 'mark_as_approved', 'mark_as_declined', 'mark_as_fifty_code', 'mark_as_no_refund', 'mark_as_time_out']

    # Define additional actions if needed, similar to the provided ones, for handling other statuses

@admin.register(OrderCheck)
class OrderCheckAdmin(admin.ModelAdmin):
    list_display = ('order', 'auth_message', 'auth_code', 'credits', 'checked_at')
    list_filter = ('checked_at', 'order__status')
    search_fields = ('order__id', 'auth_code', 'auth_message')
    date_hierarchy = 'checked_at'
    ordering = ('-checked_at',)
    raw_id_fields = ('order',)

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new checks through admin for data integrity

    def has_delete_permission(self, request, obj=None):
        return False  # Preserve historical check data by preventing deletion

@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer_username', 'seller_id', 'category_name', 'card_price', 'final_status', 'archived_at')
    list_filter = ('final_status', 'archived_at')
    search_fields = ('order_id', 'buyer_username', 'seller_id', 'category_name')
    date_hierarchy = 'archived_at'
    ordering = ('-archived_at',)

    def has_add_permission(self, request, obj=None):
        return False  # Prevent manual addition to preserve archival integrity

    def has_change_permission(self, request, obj=None):
        return False  # Prevent modifications to archived records

    def has_delete_permission(self, request, obj=None):
        return True  # Consider allowing deletion if necessary, or set to False to preserve all history
