import logging
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_notification(user, notification_type, title, message, link=None):
        """
        Creates an in-app Notification and logs an email/SMS dispatch.
        """
        # 1. Create in-app notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
        
        # 2. Simulate email dispatch
        if getattr(user, 'email', None):
            logger.info(
                f"[SIMULATION] Email Sent to {user.email}:\n"
                f"From: {settings.DEFAULT_FROM_EMAIL}\n"
                f"Subject: {title}\n"
                f"Body: {message}\n"
            )
            # We also write to standard django console email backend if configured, which it is
            from django.core.mail import send_mail
            try:
                send_mail(
                    subject=title,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send console email: {e}")

        # 3. Simulate SMS dispatch
        profile = getattr(user, 'profile', None)
        phone = getattr(profile, 'phone_number', None) if profile else None
        if phone:
            logger.info(
                f"[SIMULATION] SMS Sent to {phone}:\n"
                f"Message: {message}\n"
            )
            # This makes the SMS provider integration highly extensible.
            # You can easily swap this logic with a real Twilio or SMS gateway client here.
            
        return notification
