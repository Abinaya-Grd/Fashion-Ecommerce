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

            if item.variant and item.variant.stock < item.quantity:
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
                item.variant.stock -= item.quantity
                item.variant.save()

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

    def delete(self, request, pk):
        try:
            order = Order.objects.get(orderid=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        if order.payment_status == "paid":
            return error_response(
                "Paid order cannot be deleted. Please cancel the order instead."
            )

        order.delete()

        return success_response("Order deleted successfully")


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            order = Order.objects.get(orderid=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        if order.order_status in ["shipped", "delivered"]:
            return error_response("Order cannot be cancelled after shipping")

        if order.order_status == "cancelled":
            return error_response("Order already cancelled")

        order.order_status = "cancelled"
        order.save()

        serializer = OrderSerializer(order)

        return success_response(
            "Order cancelled successfully",
            serializer.data
        )
        
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        new_status = request.data.get("order_status")

        allowed_status = [
            "pending",
            "confirmed",
            "packed",
            "shipped",
            "out_for_delivery",
            "delivered",
            "cancelled",
        ]

        if new_status not in allowed_status:
            return error_response("Invalid order status")

        try:
            order = Order.objects.get(orderid=pk)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        order.order_status = new_status

        if new_status == "delivered" and order.payment_status == "pending":
            order.payment_status = "paid"

        order.save()

        serializer = OrderSerializer(order)

        return success_response(
            "Order status updated successfully",
            serializer.data
        )


class OrderTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(orderid=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        tracking_steps = [
            "pending",
            "confirmed",
            "packed",
            "shipped",
            "out_for_delivery",
            "delivered",
        ]

        current_index = tracking_steps.index(order.order_status) if order.order_status in tracking_steps else -1

        tracking = []

        for index, step in enumerate(tracking_steps):
            tracking.append({
                "status": step,
                "completed": index <= current_index,
                "current": index == current_index
            })

        return success_response(
            "Order tracking fetched successfully",
            {
                "order_id": order.orderid,
                "order_status": order.order_status,
                "payment_status": order.payment_status,
                "tracking": tracking
            }
        )
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        new_status = request.data.get("order_status")

        allowed_status = [
            "pending",
            "confirmed",
            "packed",
            "shipped",
            "out_for_delivery",
            "delivered",
            "cancelled",
        ]

        if new_status not in allowed_status:
            return error_response("Invalid order status")

        try:
            order = Order.objects.get(orderid=pk)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        order.order_status = new_status

        if new_status == "delivered" and order.payment_status == "pending":
            order.payment_status = "paid"

        order.save()

        serializer = OrderSerializer(order)

        return success_response(
            "Order status updated successfully",
            serializer.data
        )


class OrderTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(orderid=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        if order.order_status == "cancelled":
            return success_response(
                "Order tracking fetched successfully",
                {
                    "order_id": order.orderid,
                    "order_status": order.order_status,
                    "payment_status": order.payment_status,
                    "tracking": [
                        {
                            "status": "cancelled",
                            "completed": True,
                            "current": True
                        }
                    ]
                }
            )

        tracking_steps = [
            "pending",
            "confirmed",
            "packed",
            "shipped",
            "out_for_delivery",
            "delivered",
        ]

        current_index = tracking_steps.index(order.order_status)

        tracking = []

        for index, step in enumerate(tracking_steps):
            tracking.append({
                "status": step,
                "completed": index <= current_index,
                "current": index == current_index
            })

        return success_response(
            "Order tracking fetched successfully",
            {
                "order_id": order.orderid,
                "order_status": order.order_status,
                "payment_status": order.payment_status,
                "tracking": tracking
            }
        )