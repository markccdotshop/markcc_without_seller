from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Transaction

# Inline admin for Profile to be edited within User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Inline admin for Transactions to be edited within User
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1
    verbose_name_plural = 'Transactions'

# Custom UserAdmin to include the inlines for Profile and Transactions
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, TransactionInline,)
    list_display = ('id', 'username', 'is_staff', 'is_active', 'get_balance', 'get_role')
    list_select_related = ('profile',)

    # Add custom filters to the admin panel
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)

    # Set a default ordering of users by descending ID so newest users first
    ordering = ('-id',)

    # Define which fields to use for the search functionality
    search_fields = BaseUserAdmin.search_fields + ('profile__role',)

    # Method to display balance from Profile
    def get_balance(self, obj):
        return obj.profile.balance
    get_balance.short_description = 'Balance'

    # Method to display role from Profile
    def get_role(self, obj):
        return obj.profile.role
    get_role.short_description = 'Role'

    # Customize the queryset to optimize database access
    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related('profile')
        return queryset

# Unregister the original UserAdmin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register Profile Admin if needed separately (optional if you have Profile inline)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'role')
    search_fields = ('user__username', 'user__email', 'role')

admin.site.register(Profile, ProfileAdmin)

# Register Transaction Admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'timestamp', 'description')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'amount')
    ordering = ('-timestamp',)

admin.site.register(Transaction, TransactionAdmin)
