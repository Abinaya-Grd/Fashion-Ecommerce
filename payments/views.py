import razorpay

from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message
    }, status=status_code)


def get_payable_amount(order):
    if order.final_amount and order.final_amount > 0:
        return order.final_amount
    return order.total_amount


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order")
        payment_method = request.data.get("payment_method")
        transaction_id = request.data.get("transaction_id")

        try:
            order = Order.objects.get(orderid=order_id, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        if Payment.objects.filter(order=order).exists():
            return error_response("Payment already exists for this order")

        amount = get_payable_amount(order)

        if amount <= 0:
            return error_response("Invalid payment amount")

        payment_status = "pending"
        paid_at = None

        if payment_method == "cod":
            payment_status = "pending"

        elif payment_method == "razorpay":
            payment_status = "paid"
            paid_at = timezone.now()

        else:
            return error_response("Invalid payment method")

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount=amount,
            payment_status=payment_status,
            paid_at=paid_at
        )

        order.payment_status = payment_status
        order.order_status = "confirmed"
        order.save()

        serializer = PaymentSerializer(payment)

        return success_response(
            "Payment created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class MyPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(
            order__user=request.user
        ).order_by('-paymentid')

        serializer = PaymentSerializer(payments, many=True)

        return success_response(
            "Payments fetched successfully",
            serializer.data
        )


class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order")

        try:
            order = Order.objects.get(
                orderid=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return error_response(
                "Order not found",
                status.HTTP_404_NOT_FOUND
            )

        if Payment.objects.filter(order=order, payment_status="paid").exists():
            return error_response("Payment already completed for this order")

        amount = get_payable_amount(order)

        if amount <= 0:
            return error_response("Invalid order amount")

        razorpay_amount = int(amount * 100)

        if razorpay_amount < 100:
            return error_response("Minimum Razorpay amount should be ₹1")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:
            razorpay_order = client.order.create({
                "amount": razorpay_amount,
                "currency": "INR",
                "payment_capture": 1
            })
        except Exception as e:
            return error_response(str(e))

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "payment_method": "razorpay",
                "razorpay_order_id": razorpay_order["id"],
                "amount": amount,
                "payment_status": "pending"
            }
        )

        if not created:
            payment.payment_method = "razorpay"
            payment.razorpay_order_id = razorpay_order["id"]
            payment.amount = amount
            payment.payment_status = "pending"
            payment.save()

        return success_response(
            "Razorpay order created",
            {
                "razorpay_order_id": razorpay_order["id"],
                "amount": razorpay_amount,
                "key": settings.RAZORPAY_KEY_ID
            }
        )


class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:
            order = Order.objects.get(
                orderid=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return error_response(
                "Order not found",
                status.HTTP_404_NOT_FOUND
            )

        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            return error_response("Razorpay payment details are required")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
        except Exception:
            return error_response("Payment verification failed")

        amount = get_payable_amount(order)

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "payment_method": "razorpay",
                "razorpay_order_id": razorpay_order_id,
                "transaction_id": razorpay_payment_id,
                "amount": amount,
                "payment_status": "paid",
                "paid_at": timezone.now()
            }
        )

        if not created:
            payment.payment_method = "razorpay"
            payment.razorpay_order_id = razorpay_order_id
            payment.transaction_id = razorpay_payment_id
            payment.amount = amount
            payment.payment_status = "paid"
            payment.paid_at = timezone.now()
            payment.save()

        order.payment_status = "paid"
        order.order_status = "confirmed"
        order.save()

        serializer = PaymentSerializer(payment)

        return success_response(
            "Payment verified successfully",
            serializer.data
        )