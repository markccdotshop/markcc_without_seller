from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

def get_active_users():
    # Get current active sessions
    session_keys = Session.objects.filter(expire_date__gte=timezone.now()).values_list('session_key', flat=True)
    
    # Get session objects from session keys
    active_sessions = Session.objects.filter(session_key__in=session_keys)
    
    # Get user ids from session data
    user_ids = [session.get_decoded().get('_auth_user_id') for session in active_sessions if session.get_decoded().get('_auth_user_id')]

    # Get user objects using the list of user ids
    return User.objects.filter(id__in=user_ids).distinct()
