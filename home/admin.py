from django.contrib import admin
from .models import ShopAnnouncement, ProductUpdateAnnouncement

class ShopAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'is_active')
    list_filter = ('created_at', 'is_active')
    search_fields = ('title', 'content')

class ProductUpdateAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'updated_at', 'is_active')
    list_filter = ('category', 'updated_at', 'is_active')
    search_fields = ('title', 'description')

admin.site.register(ShopAnnouncement, ShopAnnouncementAdmin)
admin.site.register(ProductUpdateAnnouncement, ProductUpdateAnnouncementAdmin)
