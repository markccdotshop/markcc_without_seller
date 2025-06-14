from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderHistory

# For example, using a cron job to run daily at midnight might look like this:
# 0 0 * * * /path/to/your/virtualenv/bin/python /path/to/your/project/manage.py archive_orders

class Command(BaseCommand):
    help = 'Archives orders older than a month and deletes them from the Order table.'

    def handle(self, *args, **options):
        # Define the age of orders to be archived (e.g., 30 days old)
        threshold_date = timezone.now()

        # Identify orders to be archived
        orders_to_archive = Order.objects.filter(order_placed_at__lte=threshold_date)

        # Copy each order to OrderHistory
        for order in orders_to_archive:
            OrderHistory.objects.create(
                order_id=order.id,
                buyer_username=order.buyer.username if order.buyer else 'Unknown',
                seller_id=order.seller.id if order.seller else -1,
                category_name=order.category.name if order.category else 'Unknown',
                card_price=order.card_price,
                final_status=order.get_status_display(),
            )
            # Optionally, log the archival of each order
            self.stdout.write(self.style.SUCCESS(f'Archived order {order.id}'))

        # Delete the archived orders from Order
        orders_to_archive.delete()

        # Final message
        self.stdout.write(self.style.SUCCESS(f'Successfully archived and deleted orders older than {threshold_date.strftime("%Y-%m-%d")}'))
