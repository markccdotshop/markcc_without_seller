from django.urls import path,include
from . import views

urlpatterns=[
path('', views.category, name='category'),
path('create/view/', views.create_and_view_categories, name='create_view_category'),
path('delete-base/<int:base_id>/', views.delete_base, name='delete_base'),

path('upload/cards/', views.upload_cards, name='upload_cards'),
path('celery-progress/', include('celery_progress.urls')),

path('category/publish/<int:category_id>/', views.publish_category, name='publish_category'),
path('category/unpublish/<int:category_id>/', views.unpublish_category, name='unpublish_category'),
]