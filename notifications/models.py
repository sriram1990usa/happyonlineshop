from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPES = (
        ('ORDER', 'Order Updates'),
        ('SHIPPING', 'Shipping Updates'),
        ('OFFER', 'Promotions & Offers'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=15, choices=TYPES, default='ORDER')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True) # relative URL redirect
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title} (Read: {self.is_read})"
