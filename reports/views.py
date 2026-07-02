from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdminRole
from accounts.models import CustomUser
from products.models import Product, ProductVariant
from orders.models import Order, OrderItem
from payments.models import Payment
import csv
from django.http import HttpResponse


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


class ReportsDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()

        total_revenue = Order.objects.filter(
            payment_status="paid"
        ).aggregate(total=Sum("final_amount"))["total"] or 0

        today_revenue = Order.objects.filter(
            payment_status="paid",
            created_at__date=today
        ).aggregate(total=Sum("final_amount"))["total"] or 0

        data = {
            "total_users": CustomUser.objects.count(),
            "total_products": Product.objects.count(),
            "total_orders": Order.objects.count(),
            "paid_orders": Order.objects.filter(payment_status="paid").count(),
            "pending_orders": Order.objects.filter(order_status="pending").count(),
            "delivered_orders": Order.objects.filter(order_status="delivered").count(),
            "cancelled_orders": Order.objects.filter(order_status="cancelled").count(),
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
        }

        return success_response(
            "Reports dashboard fetched successfully",
            data
        )


class SalesReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        orders = Order.objects.filter(payment_status="paid")

        if start_date and end_date:
            orders = orders.filter(
                created_at__date__range=[start_date, end_date]
            )

        data = {
            "total_sales": orders.count(),
            "total_revenue": orders.aggregate(
                total=Sum("final_amount")
            )["total"] or 0,
            "orders": [
                {
                    "orderid": order.orderid,
                    "customer": order.user.email,
                    "final_amount": order.final_amount,
                    "order_status": order.order_status,
                    "payment_status": order.payment_status,
                    "created_at": order.created_at,
                }
                for order in orders.order_by("-orderid")
            ]
        }

        return success_response(
            "Sales report fetched successfully",
            data
        )


class OrdersReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        data = {
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(order_status="pending").count(),
            "confirmed_orders": Order.objects.filter(order_status="confirmed").count(),
            "packed_orders": Order.objects.filter(order_status="packed").count(),
            "shipped_orders": Order.objects.filter(order_status="shipped").count(),
            "out_for_delivery_orders": Order.objects.filter(order_status="out_for_delivery").count(),
            "delivered_orders": Order.objects.filter(order_status="delivered").count(),
            "cancelled_orders": Order.objects.filter(order_status="cancelled").count(),
        }

        return success_response(
            "Orders report fetched successfully",
            data
        )


class ProductsReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        best_sellers = OrderItem.objects.values(
            "product__productid",
            "product__name"
        ).annotate(
            total_sold=Sum("quantity")
        ).order_by("-total_sold")[:10]

        low_stock = ProductVariant.objects.filter(
            stock__lte=5
        ).values(
            "variantid",
            "product__name",
            "sku",
            "stock"
        )

        out_of_stock = ProductVariant.objects.filter(
            stock=0
        ).values(
            "variantid",
            "product__name",
            "sku",
            "stock"
        )

        data = {
            "total_products": Product.objects.count(),
            "best_selling_products": list(best_sellers),
            "low_stock_products": list(low_stock),
            "out_of_stock_products": list(out_of_stock),
        }

        return success_response(
            "Products report fetched successfully",
            data
        )


class CustomersReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        customers = CustomUser.objects.filter(
            role="customer"
        ).annotate(
            total_orders=Count("orders")
        ).order_by("-total_orders")[:10]

        data = {
            "total_customers": CustomUser.objects.filter(role="customer").count(),
            "top_customers": [
                {
                    "id": customer.id,
                    "email": customer.email,
                    "username": customer.username,
                    "total_orders": customer.total_orders,
                }
                for customer in customers
            ]
        }

        return success_response(
            "Customers report fetched successfully",
            data
        )


class RevenueReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        data = {
            "today_revenue": Order.objects.filter(
                payment_status="paid",
                created_at__date=today
            ).aggregate(total=Sum("final_amount"))["total"] or 0,

            "last_7_days_revenue": Order.objects.filter(
                payment_status="paid",
                created_at__date__gte=last_7_days
            ).aggregate(total=Sum("final_amount"))["total"] or 0,

            "last_30_days_revenue": Order.objects.filter(
                payment_status="paid",
                created_at__date__gte=last_30_days
            ).aggregate(total=Sum("final_amount"))["total"] or 0,

            "total_revenue": Order.objects.filter(
                payment_status="paid"
            ).aggregate(total=Sum("final_amount"))["total"] or 0,
        }

        return success_response(
            "Revenue report fetched successfully",
            data
        )
        
class ExportOrdersCSVView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders_report.csv"'

        writer = csv.writer(response)

        writer.writerow([
            "Order ID",
            "Customer Email",
            "Total Amount",
            "Discount Amount",
            "Final Amount",
            "Order Status",
            "Payment Status",
            "Phone",
            "Created At",
        ])

        orders = Order.objects.all().order_by("-orderid")

        for order in orders:
            writer.writerow([
                order.orderid,
                order.user.email,
                order.total_amount,
                order.discount_amount,
                order.final_amount,
                order.order_status,
                order.payment_status,
                order.phone,
                order.created_at,
            ])

        return response


class ExportProductsCSVView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products_report.csv"'

        writer = csv.writer(response)

        writer.writerow([
            "Product ID",
            "Product Name",
            "SKU",
            "Price",
            "Offer Price",
            "Stock",
            "Status",
            "Created At",
        ])

        products = Product.objects.all().order_by("-productid")

        for product in products:
            writer.writerow([
                product.productid,
                product.name,
                product.sku,
                product.price,
                product.offer_price,
                product.stock,
                product.status,
                product.created_at,
            ])

        return response


class ExportSalesCSVView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sales_report.csv"'

        writer = csv.writer(response)

        writer.writerow([
            "Order ID",
            "Customer Email",
            "Final Amount",
            "Order Status",
            "Payment Status",
            "Created At",
        ])

        orders = Order.objects.filter(
            payment_status="paid"
        ).order_by("-orderid")

        for order in orders:
            writer.writerow([
                order.orderid,
                order.user.email,
                order.final_amount,
                order.order_status,
                order.payment_status,
                order.created_at,
            ])

        return response