from django.shortcuts import render
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from products.models import Product, ProductVariant
from orders.models import Order, OrderItem


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_users = CustomUser.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()

        pending_orders = Order.objects.filter(order_status="pending").count()
        delivered_orders = Order.objects.filter(order_status="delivered").count()
        cancelled_orders = Order.objects.filter(order_status="cancelled").count()

        total_revenue = Order.objects.filter(
            payment_status="paid"
        ).aggregate(
            revenue=Sum("final_amount")
        )["revenue"] or 0

        return success_response(
            "Dashboard summary fetched successfully",
            {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "delivered_orders": delivered_orders,
                "cancelled_orders": cancelled_orders,
                "total_revenue": total_revenue,
            }
        )


class RecentOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.select_related("user").order_by("-orderid")[:10]

        data = []

        for order in orders:
            data.append({
                "orderid": order.orderid,
                "customer": order.user.username,
                "total_amount": order.total_amount,
                "final_amount": order.final_amount,
                "order_status": order.order_status,
                "payment_status": order.payment_status,
                "created_at": order.created_at,
            })

        return success_response(
            "Recent orders fetched successfully",
            data
        )


class LowStockProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        variants = ProductVariant.objects.select_related(
            "product", "color", "size"
        ).filter(stock__lte=5).order_by("stock")

        data = []

        for variant in variants:
            data.append({
                "variantid": variant.variantid,
                "product": variant.product.name,
                "sku": variant.sku,
                "color": variant.color.name if variant.color else None,
                "size": variant.size.name if variant.size else None,
                "stock": variant.stock,
            })

        return success_response(
            "Low stock products fetched successfully",
            data
        )


class TopSellingProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_products = OrderItem.objects.values(
            "product__productid",
            "product__name"
        ).annotate(
            sold_quantity=Sum("quantity"),
            total_sales=Sum("total_price")
        ).order_by("-sold_quantity")[:10]

        return success_response(
            "Top selling products fetched successfully",
            list(top_products)
        )

# Create your views here.
