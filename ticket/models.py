from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinLengthValidator
from django.core.exceptions import PermissionDenied



class Ticket(models.Model):
    STATUS_CHOICES = (
        (1, 'Pending'),
        (2, 'Closed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, validators=[MinLengthValidator(1)])
    message = models.TextField(max_length=500, validators=[MinLengthValidator(1)])
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)


    def get_status_text(self):
        return dict(Ticket.STATUS_CHOICES).get(self.status, "Unknown")

    def get_status_class(self):
        if self.status == 1:
            return "status-pending"
        elif self.status == 2:
            return "status-closed"
        else:
            return "status-unknown"

class Reply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    admin_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.ticket.status == 2 and not self.ticket.user.groups.filter(name='Admin').exists():
            raise PermissionDenied('Only admins can add replies to open tickets')
        super().save(*args, **kwargs)


