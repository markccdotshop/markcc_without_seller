from django.contrib import admin
from billing.models import Billing

class BillingAdmin(admin.ModelAdmin):
	list_display=('id','user','address','coin_symbol','crypto_amount','usd_amount','fund_status','received_date')

admin.site.register(Billing,BillingAdmin)
