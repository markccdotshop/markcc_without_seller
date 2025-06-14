from functools import wraps
import logging
from django.shortcuts import redirect
from django.urls import reverse


logger = logging.getLogger(__name__)

def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the logged-in user is a seller and if the seller is active
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'seller') and request.user.profile.seller.is_active:
            return view_func(request, *args, **kwargs)
        else:
            # Log different scenarios
            if request.user.is_authenticated:
                # If user is logged in but not a seller
                logger.warning(f"Unauthorized access attempt to seller page by user {request.user.username}, IP: {get_client_ip(request)}")
            else:
                # If the user is not logged in (anonymous user)
                logger.warning(f"Unauthorized access attempt to seller page by anonymous user, IP: {get_client_ip(request)}")
            login_url = reverse('login')  # This refers to the 'login' view as named in your 'users.urls'
            redirect_url = f"{login_url}?next={request.path}"
            return redirect(redirect_url)
    return _wrapped_view

def get_client_ip(request):
    """Get the client IP from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
