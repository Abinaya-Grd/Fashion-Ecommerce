from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import razorpay
from django.conf import settings
from django.utils import timezone
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

        payment_status = "pending"
        paid_at = None

        if payment_method == "cod":
            payment_status = "pending"

        if payment_method == "razorpay":
            payment_status = "paid"
            paid_at = timezone.now()

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount=order.total_amount,
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
        payments = Payment.objects.filter(order__user=request.user).order_by('-paymentid')
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

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        amount = int(order.total_amount * 100)

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return success_response(
            "Razorpay order created",
            {
                "razorpay_order_id": razorpay_order["id"],
                "amount": amount,
                "key": settings.RAZORPAY_KEY_ID
            }
        )        

class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        order_id = request.data.get("order")

        razorpay_order_id = request.data.get(
            "razorpay_order_id"
        )

        razorpay_payment_id = request.data.get(
            "razorpay_payment_id"
        )

        razorpay_signature = request.data.get(
            "razorpay_signature"
        )

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
            return error_response(
                "Payment verification failed"
            )

        payment = Payment.objects.create(
            order=order,
            payment_method="razorpay",
            transaction_id=razorpay_payment_id,
            amount=order.total_amount,
            payment_status="paid",
            paid_at=timezone.now()
        )

        order.payment_status = "paid"
        order.order_status = "confirmed"
        order.save()

        serializer = PaymentSerializer(payment)

        return success_response(
            "Payment verified successfully",
            serializer.data
        )
        
                