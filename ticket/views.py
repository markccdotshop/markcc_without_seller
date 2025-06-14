from django.shortcuts import render, redirect
from .models import Ticket
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required(login_url='login')
def ticket(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-id')
    
    for t in tickets:
        t.admin_reply = t.replies.filter(admin_reply__isnull=False).last()
    
    return render(request, 'ticket/ticket.html', {'tickets': tickets})


@login_required(login_url='login')
def create_ticket(request):
    try:
        user = request.user
        open_tickets_count = Ticket.objects.filter(user=user, replies__admin_reply__isnull=True).count()

        if open_tickets_count >= 5:
            messages.error(request, 'You have reached the maximum limit of open tickets.')
            return redirect(reverse('ticket'))
            
        if request.method == 'POST':
            subject = request.POST.get('subject')
            if subject == '':
                messages.error(request, 'Enter Subject!')
                return redirect(reverse('ticket'))
            if len(subject) > 200:
                messages.error(request, 'subject must be 200 characters or less.')
                return redirect(reverse('ticket'))

            
            message = request.POST.get('message')
            if message == '':
                messages.error(request, 'Enter message!')
                return redirect(reverse('ticket'))
            
            if len(message) > 500:
                messages.error(request, 'Message must be 500 characters or less.')
                return redirect(reverse('ticket'))
            
            user = request.user

            if subject and message:
                ticket = Ticket.objects.create(user=user, subject=subject, message=message)
                messages.success(request, 'Ticket created successfully!')
                return redirect(reverse('ticket'))
        else:
            messages.error(request, 'Something wrong!')
            return redirect(reverse('ticket'))
    except Exception as e:
        logger.warning(f'Invalid ticket creation attempt on ticket create: {e}', exc_info=True)
        messages.error(request, f'Something wrong: {str(e)}')
        return redirect(reverse('ticket'))
