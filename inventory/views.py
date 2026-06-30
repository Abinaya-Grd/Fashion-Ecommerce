from django.db import transaction
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from products.models import ProductVariant
from accounts.permissions import IsAdminRole
from .models import Inventory, StockTransaction
from .serializers import InventorySerializer, StockTransactionSerializer


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


class InventoryListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        inventory = Inventory.objects.select_related(
            "variant",
            "variant__product"
        ).order_by("-inventoryid")

        serializer = InventorySerializer(inventory, many=True)

        return success_response(
            "Inventory fetched successfully",
            serializer.data
        )


class InventoryDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, pk):
        try:
            inventory = Inventory.objects.select_related(
                "variant",
                "variant__product"
            ).get(inventoryid=pk)
        except Inventory.DoesNotExist:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)

        serializer = InventorySerializer(inventory)

        return success_response(
            "Inventory fetched successfully",
            serializer.data
        )


class StockInView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request):
        variant_id = request.data.get("variant")
        quantity = int(request.data.get("quantity", 0))
        remarks = request.data.get("remarks", "")

        if not variant_id:
            return error_response("Variant is required")

        if quantity <= 0:
            return error_response("Quantity must be greater than 0")

        try:
            variant = ProductVariant.objects.get(variantid=variant_id)
        except ProductVariant.DoesNotExist:
            return error_response("Variant not found", status.HTTP_404_NOT_FOUND)

        inventory, created = Inventory.objects.get_or_create(
            variant=variant,
            defaults={
                "available_stock": variant.stock,
                "reserved_stock": 0,
                "damaged_stock": 0,
                "reorder_level": 10
            }
        )

        inventory.available_stock += quantity
        inventory.save()

        variant.stock = inventory.available_stock
        variant.is_in_stock = variant.stock > 0
        variant.save()

        StockTransaction.objects.create(
            inventory=inventory,
            transaction_type="stock_in",
            quantity=quantity,
            remarks=remarks or "Stock added",
            created_by=request.user
        )

        serializer = InventorySerializer(inventory)

        return success_response(
            "Stock added successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class StockOutView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request):
        variant_id = request.data.get("variant")
        quantity = int(request.data.get("quantity", 0))
        remarks = request.data.get("remarks", "")

        if not variant_id:
            return error_response("Variant is required")

        if quantity <= 0:
            return error_response("Quantity must be greater than 0")

        try:
            variant = ProductVariant.objects.get(variantid=variant_id)
        except ProductVariant.DoesNotExist:
            return error_response("Variant not found", status.HTTP_404_NOT_FOUND)

        try:
            inventory = Inventory.objects.get(variant=variant)
        except Inventory.DoesNotExist:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)

        if inventory.available_stock < quantity:
            return error_response("Insufficient available stock")

        inventory.available_stock -= quantity
        inventory.save()

        variant.stock = inventory.available_stock
        variant.is_in_stock = variant.stock > 0
        variant.save()

        StockTransaction.objects.create(
            inventory=inventory,
            transaction_type="stock_out",
            quantity=quantity,
            remarks=remarks or "Stock removed",
            created_by=request.user
        )

        serializer = InventorySerializer(inventory)

        return success_response(
            "Stock removed successfully",
            serializer.data
        )


class StockAdjustmentView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request):
        variant_id = request.data.get("variant")
        available_stock = request.data.get("available_stock")
        damaged_stock = request.data.get("damaged_stock", 0)
        reorder_level = request.data.get("reorder_level")
        remarks = request.data.get("remarks", "")

        if not variant_id:
            return error_response("Variant is required")

        if available_stock is None:
            return error_response("Available stock is required")

        try:
            available_stock = int(available_stock)
            damaged_stock = int(damaged_stock)
            if reorder_level is not None:
                reorder_level = int(reorder_level)
        except ValueError:
            return error_response("Stock values must be valid numbers")

        if available_stock < 0 or damaged_stock < 0:
            return error_response("Stock values cannot be negative")

        try:
            variant = ProductVariant.objects.get(variantid=variant_id)
        except ProductVariant.DoesNotExist:
            return error_response("Variant not found", status.HTTP_404_NOT_FOUND)

        inventory, created = Inventory.objects.get_or_create(
            variant=variant,
            defaults={
                "available_stock": available_stock,
                "reserved_stock": 0,
                "damaged_stock": damaged_stock,
                "reorder_level": reorder_level or 10
            }
        )

        inventory.available_stock = available_stock
        inventory.damaged_stock = damaged_stock

        if reorder_level is not None:
            inventory.reorder_level = reorder_level

        inventory.save()

        variant.stock = inventory.available_stock
        variant.is_in_stock = variant.stock > 0
        variant.save()

        StockTransaction.objects.create(
            inventory=inventory,
            transaction_type="adjustment",
            quantity=available_stock,
            remarks=remarks or "Stock adjusted",
            created_by=request.user
        )

        serializer = InventorySerializer(inventory)

        return success_response(
            "Stock adjusted successfully",
            serializer.data
        )


class LowStockView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        inventory = Inventory.objects.select_related(
            "variant",
            "variant__product"
        ).filter(
            available_stock__lte=F("reorder_level"),
            available_stock__gt=0
        )

        serializer = InventorySerializer(inventory, many=True)

        return success_response(
            "Low stock products fetched successfully",
            serializer.data
        )


class OutOfStockView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        inventory = Inventory.objects.select_related(
            "variant",
            "variant__product"
        ).filter(
            available_stock=0
        )

        serializer = InventorySerializer(inventory, many=True)

        return success_response(
            "Out of stock products fetched successfully",
            serializer.data
        )


class StockHistoryView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, variant_id):
        try:
            inventory = Inventory.objects.get(variant__variantid=variant_id)
        except Inventory.DoesNotExist:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)

        transactions = StockTransaction.objects.filter(
            inventory=inventory
        ).order_by("-transactionid")

        serializer = StockTransactionSerializer(transactions, many=True)

        return success_response(
            "Stock history fetched successfully",
            serializer.data
        )