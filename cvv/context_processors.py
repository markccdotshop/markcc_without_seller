from .models import CreditCardInformation

def card_count(request):
    if request.user.is_authenticated:
        return {'card_count': CreditCardInformation.objects.filter(card_base__category_status='published', card_base__seller__is_active=True).count()}
    return {'card_count': 0}