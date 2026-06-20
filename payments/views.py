from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from orders.models import Order
from .models import Transaction
from decimal import Decimal
import json
import logging
import razorpay

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

            order = None
            if razorpay_order_id:
                order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if not order and order_number:
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
                logger.info(f"Successfully processed Razorpay webhook payment for Order {order.order_number}")
                return JsonResponse({'status': 'success', 'message': 'Payment processed'})
            else:
                logger.warning(f"Order not found for Razorpay Webhook (order_id: {razorpay_order_id}, order_number: {order_number})")
                return JsonResponse({'error': 'Order not found'}, status=404)

        return JsonResponse({'status': 'ignored'})


@method_decorator(login_required, name='dispatch')
class RazorpayCheckoutView(View):
    template_name = 'payments/razorpay_checkout.html'

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Razorpay Keys
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET
        
        is_mock = True
        razorpay_order_id = order.razorpay_order_id

        if key_id and key_secret:
            try:
                client = razorpay.Client(auth=(key_id, key_secret))
                amount_paise = int(order.total * 100)
                
                # Check if we already created a real Razorpay Order
                if not razorpay_order_id or razorpay_order_id.startswith('mock_'):
                    razorpay_order = client.order.create({
                        'amount': amount_paise,
                        'currency': 'INR',
                        'receipt': order.order_number,
                    })
                    razorpay_order_id = razorpay_order['id']
                    order.razorpay_order_id = razorpay_order_id
                    order.save()
                is_mock = False
            except Exception as e:
                logger.error(f"Error creating Razorpay order: {e}")
                # Fallback to mock mode if credentials fail/timeout
                is_mock = True

        if is_mock and (not razorpay_order_id or not razorpay_order_id.startswith('mock_')):
            razorpay_order_id = f"mock_order_{order.order_number}"
            order.razorpay_order_id = razorpay_order_id
            order.save()

        context = {
            'order': order,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_key_id': key_id or 'mock_key_id_12345',
            'amount_paise': int(order.total * 100),
            'is_mock': is_mock,
        }
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayVerifyView(View):
    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception:
            return JsonResponse({'error': 'Invalid request body'}, status=400)

        payment_id = data.get('razorpay_payment_id')
        rzp_order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        is_mock_payment = data.get('is_mock') == 'true' or data.get('is_mock') is True or (rzp_order_id and rzp_order_id.startswith('mock_'))

        if not payment_id or not rzp_order_id:
            return JsonResponse({'error': 'Missing payment credentials'}, status=400)

        # Retrieve order
        order = Order.objects.filter(razorpay_order_id=rzp_order_id).first()
        if not order:
            # Fallback to matching by mock order ID format
            if rzp_order_id.startswith('mock_order_'):
                order_number = rzp_order_id.replace('mock_order_', '')
                order = Order.objects.filter(order_number=order_number).first()

        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)

        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET

        if not is_mock_payment and key_id and key_secret:
            try:
                client = razorpay.Client(auth=(key_id, key_secret))
                client.utility.verify_payment_signature({
                    'razorpay_order_id': rzp_order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
                # Signature matches
            except Exception as e:
                logger.error(f"Razorpay verification failed: {e}")
                order.payment_status = 'FAILED'
                order.save()
                return JsonResponse({'error': 'Signature verification failed'}, status=400)
        else:
            # Simulated payment verification
            logger.info("Simulated payment success verified.")

        # Update order & payment record
        order.payment_status = 'PAID'
        order.status = 'CONFIRMED'
        order.save()

        # Record transaction
        Transaction.objects.update_or_create(
            transaction_id=payment_id,
            defaults={
                'order': order,
                'gateway': 'RAZORPAY',
                'amount': order.total,
                'status': 'SUCCESS',
                'raw_response': data
            }
        )

        redirect_url = reverse('orders:confirmation', kwargs={'order_number': order.order_number})
        return JsonResponse({
            'status': 'success',
            'message': 'Payment verified successfully.',
            'redirect_url': redirect_url
        })
