from django.contrib import admin
from django.urls import include, path, re_path

# admin customization

admin.site.site_header = 'Cvv Shop Dashboard'
admin.site.site_title = 'Cvv Admin'
admin.site.index_title = 'Welcome to Admin Interface'

urlpatterns = [
    # ===== maintenance mode ====
    re_path(r"^maintenance-mode/", include("maintenance_mode.urls")),
    # ===== billing ====
    path('billing/', include('billing.urls')),
    # ===== users ====
    path('auth/', include('users.urls')),
    # ===== home ====
    path('', include('home.urls')),
    # ===== cvv ====
    path('cvv/', include('cvv.urls')),
    # ===== orders ====
    path('orders/', include('orders.urls')),
    # ===== ticket ====
    path('ticket/', include('ticket.urls')),
    # ===== cart ====
    path('cart/', include('cart.urls')),


    # ===== seller ====
    path('seller/', include('sellers.urls')),
    # ===== category ====
    path('seller/categories/', include('category.urls')),
    # ===== bitcoin_config ====
    path('seller/cryptocurrency/', include('crypto_configs.urls')),
    # ===== admin ====
    path('nepal/', admin.site.urls),
]