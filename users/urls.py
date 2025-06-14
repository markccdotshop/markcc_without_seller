from django.urls import path, include
from . import views

urlpatterns = [
    path('captcha/', include('captcha.urls')),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('change/password/', views.change_password, name='change/password'),
    path('logout/', views.user_logout, name='logout'),
    path('view/user/', views.active_users_view, name='view/user'),
]