from django.db import models
from orders.models import Order

class Transaction(models.Model):
    GATEWAYS = (
        ('STRIPE', 'Stripe'),
        ('RAZORPAY', 'Razorpay'),
        ('COD', 'Cash On Delivery'),
    )
    STATUSES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    gateway = models.CharField(max_length=15, choices=GATEWAYS)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUSES, default='SUCCESS')
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} Transaction {self.transaction_id} for Order {self.order.order_number}"
