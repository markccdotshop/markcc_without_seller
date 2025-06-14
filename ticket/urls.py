from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket, name='ticket'),
    path('create_ticket/', views.create_ticket, name='create_ticket'), 
]