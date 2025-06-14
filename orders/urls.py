from django.urls import path
from . import views

urlpatterns=[
path('', views.orders, name='orders'),
path('check/cc/<int:id>/', views.check_cc, name='check/cc'),
]