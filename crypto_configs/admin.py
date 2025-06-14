from django.contrib import admin
from crypto_configs.models import Cryptocurrency

class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_by', 'coin_name', 'address', 'address_status', 'assigned_to', 'upload_date', 'assigned_date')

admin.site.register(Cryptocurrency, CryptocurrencyAdmin)