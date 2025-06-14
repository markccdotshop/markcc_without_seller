from django.urls import path
from .views import cart_detail, add_to_cart, get_cart_count, remove_from_cart, remove_all, buycc

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/', add_to_cart, name='add_to_cart'),
    path('count/', get_cart_count, name='get_cart_count'),
    path('remove/<int:card_id>/', remove_from_cart, name='remove_from_cart'),
    path('remove_all/', remove_all, name='remove_all'),
    path('buycc/', buycc, name='buycc'), 
]
