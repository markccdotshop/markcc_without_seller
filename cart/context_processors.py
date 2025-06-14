
from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        return {'cart_count': Cart.objects.filter(customer=request.user).count()}
    return {'cart_count': 0}

