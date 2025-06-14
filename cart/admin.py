from django.contrib import admin
from .models import Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'credit_card', 'added_date')
    list_filter = ('customer', 'added_date')
    search_fields = ('customer__username', 'credit_card__unique_card_identifier')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(customer=request.user)

admin.site.register(Cart, CartAdmin)
