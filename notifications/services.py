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

    @staticmethod
    def send_html_email_with_attachment(user, subject, text_content, html_content, attachment_data=None, attachment_name=None, attachment_content_type=None, notification_type='ORDER', link=None):
        """
        Sends a rich HTML email to the user with an optional file attachment (like invoice PDF).
        Also creates an in-app Notification.
        """
        # 1. Create in-app notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=subject,
            message=text_content,
            link=link
        )

        # 2. Send email
        if getattr(user, 'email', None):
            from django.core.mail import EmailMultiAlternatives
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                if html_content:
                    email.attach_alternative(html_content, "text/html")
                
                if attachment_data and attachment_name:
                    content_type = attachment_content_type or 'application/pdf'
                    email.attach(attachment_name, attachment_data, content_type)
                
                email.send(fail_silently=False)
                logger.info(f"Email sent successfully to {user.email} with subject: {subject}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {e}")
                
        return notification

