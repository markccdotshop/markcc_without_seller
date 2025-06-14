from django.urls import path
from . import views

urlpatterns = [
    # CVV-related URLs
    path('', views.cvv, name='cvv'),
    path('search/', views.search, name='search'),
    path('buy/<int:id>/', views.buycc, name='buycc'),

    # Expired cards management URLs
    path('expired/', views.expired, name='expired'),
    path('delete_all_expired/', views.delete_all_expired, name='delete_all_expired'),

    # Seller selection URL (used for AJAX request)
    path('get_bases_for_seller/', views.get_bases_for_seller, name='get_bases_for_seller'),

    path('purchase-status/<str:task_id>/', views.purchase_status, name='purchase_status'),
    
]



