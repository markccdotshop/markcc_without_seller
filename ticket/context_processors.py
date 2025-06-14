from .models import Ticket

def pending_ticket_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return {'pending_ticket_count': Ticket.objects.filter(status=1).count()}
    return {'pending_ticket_count': 0}