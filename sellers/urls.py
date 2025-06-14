from django.urls import path
from . import views

urlpatterns = [
    path('', views.seller_dashboard, name='seller'),

]
