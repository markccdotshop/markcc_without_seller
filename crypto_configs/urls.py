from django.urls import path
from . import views

urlpatterns = [
    path('', views.cryptocurrency, name='crypto/config'),
    path('upload_address', views.upload_address, name='upload_address'),
    path('fund/received', views.fund_received, name='fund/received'),
]