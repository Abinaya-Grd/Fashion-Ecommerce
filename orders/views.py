from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from coupons.models import Coupon


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
        coupon_code = request.data.get("coupon_code")

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

        total_amount = Decimal("0.00")
        discount_amount = Decimal("0.00")
        coupon = None

        for item in cart_items:
            price = item.price
            total_price = price * item.quantity
            total_amount += total_price

            if item.variant:
                variant = item.variant

                if variant.stock < item.quantity:
                    return error_response(
                        f"Insufficient stock for {item.product.name}"
                    )

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
            except Coupon.DoesNotExist:
                return error_response("Invalid coupon code")

            if not coupon.is_valid_coupon():
                return error_response("Coupon expired, inactive or limit reached")

            if total_amount < coupon.min_order_amount:
                return error_response("Order amount is less than minimum coupon amount")

            if coupon.discount_type == "percentage":
                discount_amount = (total_amount * coupon.discount_value) / 100
            else:
                discount_amount = coupon.discount_value

            if discount_amount > total_amount:
                discount_amount = total_amount

        final_amount = total_amount - discount_amount

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone=phone,
            total_amount=total_amount,
            coupon=coupon,
            discount_amount=discount_amount,
            final_amount=final_amount
        )

        for item in cart_items:
            price = item.price
            total_price = price * item.quantity

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
                variant.stock -= item.quantity
                variant.save()

        if coupon:
            coupon.used_count += 1
            coupon.save()

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
    def delete(self, request, pk):
        try:
             orderid = Order.objects.get(orderid=pk)
            
        except order.DoesNotExist:
             return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        order.delete()
        return success_response("Order deleted successfully")       
   


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
        
             