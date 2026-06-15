from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'gateway', 'amount', 'status', 'created_at']
    list_filter = ['gateway', 'status', 'created_at']
    search_fields = ['transaction_id', 'order__order_number']
