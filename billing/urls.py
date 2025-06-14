from django.urls import path
from . import views

urlpatterns=[
path('', views.billing, name='billing'),
path('getaddress/<str:coin_symbol>/', views.getaddress, name='getaddress'),
path('check/balance/<int:id>/', views.check_balance, name='check/balance'),
path('task-status/<str:task_id>/', views.task_status, name='task_status'),
]