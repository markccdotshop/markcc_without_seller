from django.db.models import F
from django.db import transaction



def update_user_balance(user, amount, is_refund=False):
    
    with transaction.atomic():
        # Lock the user's profile row for update to prevent race conditions
        user_profile = user.profile.__class__.objects.select_for_update().get(id=user.profile.id)
        
        # Apply the balance update
        if is_refund:
            user_profile.balance = F('balance') + amount
        else:
            user_profile.balance = F('balance') - amount
        
        # Save the update to the database
        user_profile.save()
        
        # Refresh the user's profile to reflect the update
        user.profile.refresh_from_db()