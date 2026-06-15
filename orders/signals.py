from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.services import NotificationService

@receiver(post_save, sender=Order)
def order_notification_receiver(sender, instance, created, **kwargs):
    # If there is no user associated, skip (for anonymous/guest checkout if any)
    if not instance.user:
        return

    if created:
        NotificationService.send_notification(
            user=instance.user,
            notification_type='ORDER',
            title=f"Order #{instance.order_number} Placed!",
            message=f"Thank you for shopping with us! Your order for a total of ₹{instance.total} has been received and is being processed.",
            link=f"/orders/detail/{instance.order_number}/"
        )
    else:
        # Send update notification
        status_display = instance.get_status_display()
        # Custom message based on status
        if instance.status == 'SHIPPED':
            msg = f"Good news! Your order #{instance.order_number} has been shipped. Tracking number: {instance.tracking_number or 'Not Available'}"
            n_type = 'SHIPPING'
        elif instance.status == 'OUT_FOR_DELIVERY':
            msg = f"Your order #{instance.order_number} is out for delivery today!"
            n_type = 'SHIPPING'
        elif instance.status == 'DELIVERED':
            msg = f"Your order #{instance.order_number} has been successfully delivered. We hope you enjoy your purchase!"
            n_type = 'ORDER'
        else:
            msg = f"The status of your order #{instance.order_number} has been updated to '{status_display}'."
            n_type = 'ORDER'

        NotificationService.send_notification(
            user=instance.user,
            notification_type=n_type,
            title=f"Order #{instance.order_number} status: {status_display}",
            message=msg,
            link=f"/orders/detail/{instance.order_number}/"
        )
