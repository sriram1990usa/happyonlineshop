from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order
from .invoice_service import generate_invoice_pdf
from notifications.services import NotificationService

@receiver(pre_save, sender=Order)
def order_pre_save_receiver(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Order.objects.get(pk=instance.pk)
            instance._original_payment_status = original.payment_status
        except Order.DoesNotExist:
            instance._original_payment_status = None
    else:
        instance._original_payment_status = None

@receiver(post_save, sender=Order)
def order_notification_receiver(sender, instance, created, **kwargs):
    # If there is no user associated, skip (for anonymous/guest checkout if any)
    if not instance.user:
        return

    # Check if payment status just changed to PAID (or created as PAID)
    original_payment_status = getattr(instance, '_original_payment_status', None)
    payment_transitioned_to_paid = False

    if instance.payment_status == 'PAID':
        if created or (original_payment_status != 'PAID'):
            payment_transitioned_to_paid = True

    if payment_transitioned_to_paid:
        try:
            # Generate invoice PDF
            pdf_data = generate_invoice_pdf(instance)
            
            # Prepare context for rendering
            site_url = getattr(settings, 'SITE_URL', 'https://happyonlineshop.vercel.app')
            context = {
                'user': instance.user,
                'order': instance,
                'site_url': site_url,
            }
            
            # Render HTML and Text content
            html_content = render_to_string('emails/order_paid_email.html', context)
            text_content = render_to_string('emails/order_paid_email.txt', context)
            
            # Send HTML email with attachment
            NotificationService.send_html_email_with_attachment(
                user=instance.user,
                subject=f"Payment Received & Order Confirmed #{instance.order_number}",
                text_content=text_content,
                html_content=html_content,
                attachment_data=pdf_data,
                attachment_name=f"Invoice-{instance.order_number}.pdf",
                attachment_content_type='application/pdf',
                notification_type='ORDER',
                link=f"/orders/detail/{instance.order_number}/"
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending paid order notification for order {instance.order_number}: {e}")

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
