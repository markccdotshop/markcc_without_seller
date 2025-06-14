from django.contrib import admin
from .models import Ticket, Reply



class ReplyInline(admin.StackedInline):
    model = Reply
    extra = 0

class TicketAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]
    list_display = ['id', 'user', 'subject', 'message', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'user__username']

admin.site.register(Ticket, TicketAdmin)
