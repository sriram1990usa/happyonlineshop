from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from products.models import Product
from orders.models import Order

REVIEW_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
)

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15,
        choices=REVIEW_STATUS_CHOICES,
        default='APPROVED',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.name}: {self.rating} Stars ({self.status})"

    def save(self, *args, **kwargs):
        # Determine verified purchase status
        if not self.is_verified_purchase:
            from orders.models import OrderItem
            has_order = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product
            ).filter(
                models.Q(order__status='DELIVERED') | models.Q(order__payment_status='PAID')
            ).exists()
            self.is_verified_purchase = has_order

        super().save(*args, **kwargs)
        self.update_product_rating_cache()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        self.update_product_rating_cache_for(product)

    def update_product_rating_cache(self):
        self.update_product_rating_cache_for(self.product)

    @staticmethod
    def update_product_rating_cache_for(product):
        approved_reviews = ProductReview.objects.filter(product=product, status='APPROVED')
        count = approved_reviews.count()
        if count > 0:
            avg = approved_reviews.aggregate(Avg('rating'))['rating__avg']
            product.average_rating = round(avg, 2)
            product.review_count = count
        else:
            product.average_rating = 0.00
            product.review_count = 0
        product.save(update_fields=['average_rating', 'review_count'])


from django.utils import timezone

class ReviewImage(models.Model):
    product_review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='reviews/')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for review {self.product_review.id}"


class DeliveryReview(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    body = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=REVIEW_STATUS_CHOICES,
        default='APPROVED',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery Review for Order {self.order.order_number}: {self.rating} Stars ({self.status})"


class ReviewVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_votes')
    product_review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    delivery_review = models.ForeignKey(DeliveryReview, on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    vote_type = models.CharField(
        max_length=10,
        choices=[('HELPFUL', 'Helpful'), ('UNHELPFUL', 'Not Helpful')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product_review'], name='unique_user_product_review_vote', condition=models.Q(product_review__isnull=False)),
            models.UniqueConstraint(fields=['user', 'delivery_review'], name='unique_user_delivery_review_vote', condition=models.Q(delivery_review__isnull=False)),
            models.CheckConstraint(
                condition=(models.Q(product_review__isnull=False) & models.Q(delivery_review__isnull=True)) |
                          (models.Q(product_review__isnull=True) & models.Q(delivery_review__isnull=False)),
                name='check_exactly_one_review_voted'
            )
        ]

    def __str__(self):
        target = f"Product Review {self.product_review_id}" if self.product_review else f"Delivery Review {self.delivery_review_id}"
        return f"{self.user.email} - {self.vote_type} on {target}"


class ReviewReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_reports')
    product_review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    delivery_review = models.ForeignKey(DeliveryReview, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reason = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=[('PENDING', 'Pending'), ('ACTIONED', 'Actioned'), ('DISMISSED', 'Dismissed')],
        default='PENDING',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(product_review__isnull=False) & models.Q(delivery_review__isnull=True)) |
                          (models.Q(product_review__isnull=True) & models.Q(delivery_review__isnull=False)),
                name='check_exactly_one_review_reported'
            )
        ]

    def __str__(self):
        target = f"Product Review {self.product_review_id}" if self.product_review else f"Delivery Review {self.delivery_review_id}"
        return f"Report by {self.user.email} on {target} ({self.status})"


class AdminReply(models.Model):
    product_review = models.OneToOneField(ProductReview, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_reply')
    delivery_review = models.OneToOneField(DeliveryReview, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_reply')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Admin Replies"
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(product_review__isnull=False) & models.Q(delivery_review__isnull=True)) |
                          (models.Q(product_review__isnull=True) & models.Q(delivery_review__isnull=False)),
                name='check_exactly_one_review_replied'
            )
        ]

    def __str__(self):
        target = f"Product Review {self.product_review_id}" if self.product_review else f"Delivery Review {self.delivery_review_id}"
        return f"Reply by admin {self.admin.email} on {target}"
