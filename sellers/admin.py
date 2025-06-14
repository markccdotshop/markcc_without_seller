from django.contrib import admin
from django.db.models import Sum
from .models import Seller, SellerSellsHistory, SellerTransactionHistory

class SellerSellsHistoryInline(admin.TabularInline):
    model = SellerSellsHistory
    extra = 1
    readonly_fields = ('item_type', 'item_price', 'order_placed_at')

class SellerTransactionHistoryInline(admin.TabularInline):
    model = SellerTransactionHistory
    extra = 1
    readonly_fields = ('transaction_type', 'amount', 'transaction_status', 'transaction_created_timestamp', 'transaction_approval_timestamp', 'withdrawal_currency_type')

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('profile', 'seller_store_name', 'seller_commission_rate', 'seller_rating', 'contact_methods', 'is_active', 'total_sales_amount', 'total_transactions_amount')
    inlines = [SellerSellsHistoryInline, SellerTransactionHistoryInline]

    def total_sales_amount(self, obj):
        return obj.sell_history.aggregate(total=Sum('item_price'))['total'] or 0
    total_sales_amount.short_description = 'Total Sales'

    def total_transactions_amount(self, obj):
        return obj.transactions.aggregate(total=Sum('amount'))['total'] or 0
    total_transactions_amount.short_description = 'Total Transactions'

@admin.register(SellerSellsHistory)
class SellerSellsHistoryAdmin(admin.ModelAdmin):
    list_display = ('seller', 'item_type', 'item_price', 'order_placed_at')
    list_filter = ('item_type',)
    search_fields = ('seller__seller_store_name',)

@admin.register(SellerTransactionHistory)
class SellerTransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('seller', 'transaction_type', 'amount', 'transaction_status', 'transaction_created_timestamp', 'transaction_approval_timestamp', 'withdrawal_currency_type')
    list_filter = ('transaction_type', 'transaction_status', 'withdrawal_currency_type')
    search_fields = ('seller__seller_store_name',)
