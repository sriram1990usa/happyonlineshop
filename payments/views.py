from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from orders.models import Order
from .models import Transaction
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        event_type = payload.get('type')
        logger.info(f"Stripe Webhook event received: {event_type}")

        # In standard setup, verify Stripe signature here. 
        # For mock/local development, we simulate success on checkout.session.completed or payment_intent.succeeded
        if event_type in ['checkout.session.completed', 'payment_intent.succeeded']:
            data_obj = payload.get('data', {}).get('object', {})
            
            # Fetch order number from metadata or client_reference_id
            metadata = data_obj.get('metadata', {})
            order_number = metadata.get('order_number') or data_obj.get('client_reference_id')
            
            if not order_number:
                # Fallback: check if we can query by description containing order number
                description = data_obj.get('description', '')
                if 'ORD-' in description:
                    # extract ORD-XXXXXXXXXXXX
                    start_idx = description.find('ORD-')
                    order_number = description[start_idx:start_idx+16]

            if order_number:
                order = Order.objects.filter(order_number=order_number).first()
                if order:
                    order.payment_status = 'PAID'
                    order.status = 'CONFIRMED'
                    order.save()

                    # Record transaction
                    transaction_id = data_obj.get('id', 'mock_stripe_tx_' + order_number)
                    amount_total = Decimal(str(data_obj.get('amount_total', 0))) / Decimal('100.00') if 'amount_total' in data_obj else order.total

                    Transaction.objects.update_or_create(
                        transaction_id=transaction_id,
                        defaults={
                            'order': order,
                            'gateway': 'STRIPE',
                            'amount': amount_total,
                            'status': 'SUCCESS',
                            'raw_response': payload
                        }
                    )
                    logger.info(f"Successfully processed Stripe payment for Order {order_number}")
                    return JsonResponse({'status': 'success', 'message': 'Payment processed'})
                else:
                    logger.warning(f"Order {order_number} not found for Stripe Webhook")
                    return JsonResponse({'error': 'Order not found'}, status=404)

        return JsonResponse({'status': 'ignored'})


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        event = payload.get('event')
        logger.info(f"Razorpay Webhook event received: {event}")

        # In standard setup, verify Razorpay signature here.
        if event in ['payment.captured', 'order.paid']:
            payment_entity = {}
            if 'payment' in payload.get('payload', {}):
                payment_entity = payload['payload']['payment']['entity']
            elif 'payment_link' in payload.get('payload', {}):
                payment_entity = payload['payload']['payment_link']['entity']
            
            razorpay_order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id', 'mock_rzp_pay_' + str(payment_entity.get('amount', 0)))
            amount = Decimal(str(payment_entity.get('amount', 0))) / Decimal('100.00')

            # We can associate order by checking notes or order description
            notes = payment_entity.get('notes', {})
            order_number = notes.get('order_number')

            if not order_number and razorpay_order_id:
                # We can try to search by tracking_number/notes or just match description
                description = payment_entity.get('description', '')
                if 'ORD-' in description:
                    start_idx = description.find('ORD-')
                    order_number = description[start_idx:start_idx+16]

            if order_number:
                order = Order.objects.filter(order_number=order_number).first()
                if order:
                    order.payment_status = 'PAID'
                    order.status = 'CONFIRMED'
                    order.save()

                    Transaction.objects.update_or_create(
                        transaction_id=payment_id,
                        defaults={
                            'order': order,
                            'gateway': 'RAZORPAY',
                            'amount': amount if amount > 0 else order.total,
                            'status': 'SUCCESS',
                            'raw_response': payload
                        }
                    )
                    logger.info(f"Successfully processed Razorpay payment for Order {order_number}")
                    return JsonResponse({'status': 'success', 'message': 'Payment processed'})
                else:
                    logger.warning(f"Order {order_number} not found for Razorpay Webhook")
                    return JsonResponse({'error': 'Order not found'}, status=404)

        return JsonResponse({'status': 'ignored'})
