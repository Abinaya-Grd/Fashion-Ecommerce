from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from products.models import ProductVariant


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


class CreateOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        shipping_address = request.data.get("shipping_address")
        phone = request.data.get("phone")

        if not shipping_address:
            return error_response("Shipping address is required")

        if not phone:
            return error_response("Phone number is required")

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return error_response("Cart not found")

        cart_items = cart.items.all()

        if not cart_items.exists():
            return error_response("Cart is empty")

        total_amount = 0

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone=phone,
            total_amount=0
        )

        for item in cart_items:
            price = item.price
            total_price = price * item.quantity
            total_amount += total_price

            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=price,
                total_price=total_price
            )

            if item.variant:
                variant = item.variant

                if variant.stock < item.quantity:
                    return error_response(
                        f"Insufficient stock for {item.product.name}"
                    )

                variant.stock -= item.quantity
                variant.save()

        order.total_amount = total_amount
        order.save()

        cart_items.delete()

        serializer = OrderSerializer(order)

        return success_response(
            "Order created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-orderid')
        serializer = OrderSerializer(orders, many=True)

        return success_response(
            "Orders fetched successfully",
            serializer.data
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(orderid=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)

        return success_response(
            "Order fetched successfully",
            serializer.data
        )