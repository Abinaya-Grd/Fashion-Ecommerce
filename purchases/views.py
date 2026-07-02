from django.shortcuts import render

from decimal import Decimal
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdminRole
from .models import Purchase, PurchaseItem
from .serializers import PurchaseSerializer
from inventory.models import Inventory, StockTransaction


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


class PurchaseListCreateView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        purchases = Purchase.objects.all().order_by("-purchaseid")
        serializer = PurchaseSerializer(purchases, many=True)

        return success_response(
            "Purchases fetched successfully",
            serializer.data
        )

    @transaction.atomic
    def post(self, request):
        supplier = request.data.get("supplier")
        invoice_number = request.data.get("invoice_number")
        purchase_date = request.data.get("purchase_date")
        remarks = request.data.get("remarks")
        items = request.data.get("items", [])

        if not supplier:
            return error_response("Supplier is required")

        if not invoice_number:
            return error_response("Invoice number is required")

        if not purchase_date:
            return error_response("Purchase date is required")

        if not items:
            return error_response("Purchase items are required")

        total_amount = Decimal("0.00")

        purchase = Purchase.objects.create(
            supplier_id=supplier,
            invoice_number=invoice_number,
            purchase_date=purchase_date,
            total_amount=0,
            remarks=remarks,
            status="pending"
        )

        for item in items:
            variant = item.get("variant")
            quantity = int(item.get("quantity", 0))
            cost_price = Decimal(str(item.get("cost_price", 0)))

            if quantity <= 0:
                return error_response("Quantity must be greater than 0")

            if cost_price <= 0:
                return error_response("Cost price must be greater than 0")

            total_price = quantity * cost_price
            total_amount += total_price

            PurchaseItem.objects.create(
                purchase=purchase,
                variant_id=variant,
                quantity=quantity,
                cost_price=cost_price,
                total_price=total_price
            )

        purchase.total_amount = total_amount
        purchase.save()

        serializer = PurchaseSerializer(purchase)

        return success_response(
            "Purchase created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class PurchaseDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        try:
            return Purchase.objects.get(purchaseid=pk)
        except Purchase.DoesNotExist:
            return None

    def get(self, request, pk):
        purchase = self.get_object(pk)

        if not purchase:
            return error_response("Purchase not found", status.HTTP_404_NOT_FOUND)

        serializer = PurchaseSerializer(purchase)

        return success_response(
            "Purchase fetched successfully",
            serializer.data
        )

    def delete(self, request, pk):
        purchase = self.get_object(pk)

        if not purchase:
            return error_response("Purchase not found", status.HTTP_404_NOT_FOUND)

        if purchase.status == "received":
            return error_response("Received purchase cannot be deleted")

        purchase.delete()

        return success_response("Purchase deleted successfully")


class ReceivePurchaseView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def put(self, request, pk):
        try:
            purchase = Purchase.objects.get(purchaseid=pk)
        except Purchase.DoesNotExist:
            return error_response("Purchase not found", status.HTTP_404_NOT_FOUND)

        if purchase.status == "received":
            return error_response("Purchase already received")

        if purchase.status == "cancelled":
            return error_response("Cancelled purchase cannot be received")

        for item in purchase.items.all():
            inventory, created = Inventory.objects.get_or_create(
                variant=item.variant,
                defaults={
                    "available_stock": item.variant.stock,
                    "reserved_stock": 0,
                    "damaged_stock": 0,
                    "reorder_level": 10
                }
            )

            inventory.available_stock += item.quantity
            inventory.save()

            item.variant.stock = inventory.available_stock
            item.variant.is_in_stock = item.variant.stock > 0
            item.variant.save()

            StockTransaction.objects.create(
                inventory=inventory,
                transaction_type="stock_in",
                quantity=item.quantity,
                remarks=f"Stock received from purchase #{purchase.purchaseid}",
                created_by=request.user
            )

        purchase.status = "received"
        purchase.save()

        serializer = PurchaseSerializer(purchase)

        return success_response(
            "Purchase received and inventory updated successfully",
            serializer.data
        )


class UpdatePurchaseStatusView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        new_status = request.data.get("status")

        allowed_status = ["pending", "ordered", "received", "cancelled"]

        if new_status not in allowed_status:
            return error_response("Invalid purchase status")

        try:
            purchase = Purchase.objects.get(purchaseid=pk)
        except Purchase.DoesNotExist:
            return error_response("Purchase not found", status.HTTP_404_NOT_FOUND)

        if purchase.status == "received":
            return error_response("Received purchase status cannot be changed")

        if new_status == "received":
            return error_response("Use receive purchase API to receive stock")

        purchase.status = new_status
        purchase.save()

        serializer = PurchaseSerializer(purchase)

        return success_response(
            "Purchase status updated successfully",
            serializer.data
        )