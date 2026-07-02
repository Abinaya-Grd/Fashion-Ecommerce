from django.shortcuts import render

# Create your views here.
from decimal import Decimal

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdminRole
from .models import PurchaseReturn
from .serializers import PurchaseReturnSerializer
from purchases.models import Purchase, PurchaseItem
from inventory.models import Inventory, StockTransaction
from notifications.models import Notification


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


class PurchaseReturnListCreateView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        returns = PurchaseReturn.objects.all().order_by("-purchasereturnid")
        serializer = PurchaseReturnSerializer(returns, many=True)

        return success_response(
            "Purchase returns fetched successfully",
            serializer.data
        )

    def post(self, request):
        purchase_id = request.data.get("purchase")
        purchase_item_id = request.data.get("purchase_item")
        quantity = int(request.data.get("quantity", 0))
        reason = request.data.get("reason")
        remarks = request.data.get("remarks")

        if not purchase_id:
            return error_response("Purchase is required")

        if not purchase_item_id:
            return error_response("Purchase item is required")

        if quantity <= 0:
            return error_response("Quantity must be greater than 0")

        if not reason:
            return error_response("Reason is required")

        try:
            purchase = Purchase.objects.get(purchaseid=purchase_id)
        except Purchase.DoesNotExist:
            return error_response("Purchase not found", status.HTTP_404_NOT_FOUND)

        if purchase.status != "received":
            return error_response("Return allowed only for received purchases")

        try:
            purchase_item = PurchaseItem.objects.get(
                purchaseitemid=purchase_item_id,
                purchase=purchase
            )
        except PurchaseItem.DoesNotExist:
            return error_response("Purchase item not found", status.HTTP_404_NOT_FOUND)

        if quantity > purchase_item.quantity:
            return error_response("Return quantity cannot exceed purchased quantity")

        existing_return_qty = PurchaseReturn.objects.filter(
            purchase=purchase,
            purchase_item=purchase_item,
            status__in=["requested", "approved", "completed"]
        ).count()

        if existing_return_qty >= purchase_item.quantity:
            return error_response("This purchase item is already fully returned")

        refund_amount = Decimal(quantity) * purchase_item.cost_price

        purchase_return = PurchaseReturn.objects.create(
            purchase=purchase,
            purchase_item=purchase_item,
            supplier=purchase.supplier,
            quantity=quantity,
            refund_amount=refund_amount,
            reason=reason,
            remarks=remarks,
            status="requested"
        )

        Notification.objects.create(
            user=request.user,
            title="Purchase Return Requested",
            message=f"Purchase return #{purchase_return.purchasereturnid} has been requested.",
            notification_type="general"
        )

        serializer = PurchaseReturnSerializer(purchase_return)

        return success_response(
            "Purchase return created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class PurchaseReturnDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        try:
            return PurchaseReturn.objects.get(purchasereturnid=pk)
        except PurchaseReturn.DoesNotExist:
            return None

    def get(self, request, pk):
        purchase_return = self.get_object(pk)

        if not purchase_return:
            return error_response("Purchase return not found", status.HTTP_404_NOT_FOUND)

        serializer = PurchaseReturnSerializer(purchase_return)

        return success_response(
            "Purchase return fetched successfully",
            serializer.data
        )

    def delete(self, request, pk):
        purchase_return = self.get_object(pk)

        if not purchase_return:
            return error_response("Purchase return not found", status.HTTP_404_NOT_FOUND)

        if purchase_return.status in ["approved", "completed"]:
            return error_response("Approved or completed purchase return cannot be deleted")

        purchase_return.delete()

        return success_response("Purchase return deleted successfully")


class ApprovePurchaseReturnView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        remarks = request.data.get("remarks")

        try:
            purchase_return = PurchaseReturn.objects.get(purchasereturnid=pk)
        except PurchaseReturn.DoesNotExist:
            return error_response("Purchase return not found", status.HTTP_404_NOT_FOUND)

        if purchase_return.status != "requested":
            return error_response("Only requested purchase returns can be approved")

        purchase_return.status = "approved"
        purchase_return.remarks = remarks or purchase_return.remarks
        purchase_return.save()

        Notification.objects.create(
            user=request.user,
            title="Purchase Return Approved",
            message=f"Purchase return #{purchase_return.purchasereturnid} has been approved.",
            notification_type="general"
        )

        serializer = PurchaseReturnSerializer(purchase_return)

        return success_response(
            "Purchase return approved successfully",
            serializer.data
        )


class RejectPurchaseReturnView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        remarks = request.data.get("remarks")

        if not remarks:
            return error_response("Remarks is required for rejection")

        try:
            purchase_return = PurchaseReturn.objects.get(purchasereturnid=pk)
        except PurchaseReturn.DoesNotExist:
            return error_response("Purchase return not found", status.HTTP_404_NOT_FOUND)

        if purchase_return.status != "requested":
            return error_response("Only requested purchase returns can be rejected")

        purchase_return.status = "rejected"
        purchase_return.remarks = remarks
        purchase_return.save()

        Notification.objects.create(
            user=request.user,
            title="Purchase Return Rejected",
            message=f"Purchase return #{purchase_return.purchasereturnid} has been rejected.",
            notification_type="general"
        )

        serializer = PurchaseReturnSerializer(purchase_return)

        return success_response(
            "Purchase return rejected successfully",
            serializer.data
        )


class CompletePurchaseReturnView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def put(self, request, pk):
        try:
            purchase_return = PurchaseReturn.objects.get(purchasereturnid=pk)
        except PurchaseReturn.DoesNotExist:
            return error_response("Purchase return not found", status.HTTP_404_NOT_FOUND)

        if purchase_return.status != "approved":
            return error_response("Only approved purchase returns can be completed")

        variant = purchase_return.purchase_item.variant

        try:
            inventory = Inventory.objects.get(variant=variant)
        except Inventory.DoesNotExist:
            return error_response("Inventory not found", status.HTTP_404_NOT_FOUND)

        if inventory.available_stock < purchase_return.quantity:
            return error_response("Insufficient inventory stock to return")

        inventory.available_stock -= purchase_return.quantity
        inventory.save()

        variant.stock = inventory.available_stock
        variant.is_in_stock = variant.stock > 0
        variant.save()

        StockTransaction.objects.create(
            inventory=inventory,
            transaction_type="stock_out",
            quantity=purchase_return.quantity,
            remarks=f"Purchase return #{purchase_return.purchasereturnid} completed",
            created_by=request.user
        )

        purchase_return.status = "completed"
        purchase_return.save()

        Notification.objects.create(
            user=request.user,
            title="Purchase Return Completed",
            message=f"Purchase return #{purchase_return.purchasereturnid} completed and inventory updated.",
            notification_type="general"
        )

        serializer = PurchaseReturnSerializer(purchase_return)

        return success_response(
            "Purchase return completed successfully",
            serializer.data
        )