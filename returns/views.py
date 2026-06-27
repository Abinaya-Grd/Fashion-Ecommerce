from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import ReturnRequest
from .serializers import ReturnRequestSerializer
from orders.models import Order, OrderItem
from accounts.permissions import IsAdminRole


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


class ReturnListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        returns = ReturnRequest.objects.filter(
            user=request.user
        ).order_by("-returnid")

        serializer = ReturnRequestSerializer(returns, many=True)

        return success_response(
            "Return requests fetched successfully",
            serializer.data
        )

    def post(self, request):
        order_id = request.data.get("order")
        order_item_id = request.data.get("order_item")
        reason = request.data.get("reason")

        if not reason:
            return error_response("Return reason is required")

        try:
            order = Order.objects.get(
                orderid=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        if order.order_status != "delivered":
            return error_response("Return allowed only for delivered orders")

        try:
            order_item = OrderItem.objects.get(
                orderitemid=order_item_id,
                order=order
            )
        except OrderItem.DoesNotExist:
            return error_response("Order item not found", status.HTTP_404_NOT_FOUND)

        if ReturnRequest.objects.filter(
            user=request.user,
            order=order,
            order_item=order_item
        ).exists():
            return error_response("Return request already exists for this item")

        return_request = ReturnRequest.objects.create(
            user=request.user,
            order=order,
            order_item=order_item,
            reason=reason,
            refund_amount=order_item.total_price
        )

        serializer = ReturnRequestSerializer(return_request)

        return success_response(
            "Return request created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class ReturnDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            return_request = ReturnRequest.objects.get(
                returnid=pk,
                user=request.user
            )
        except ReturnRequest.DoesNotExist:
            return error_response("Return request not found", status.HTTP_404_NOT_FOUND)

        serializer = ReturnRequestSerializer(return_request)

        return success_response(
            "Return request fetched successfully",
            serializer.data
        )


class CancelReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            return_request = ReturnRequest.objects.get(
                returnid=pk,
                user=request.user
            )
        except ReturnRequest.DoesNotExist:
            return error_response("Return request not found", status.HTTP_404_NOT_FOUND)

        if return_request.status != "requested":
            return error_response("Only requested returns can be cancelled")

        return_request.status = "cancelled"
        return_request.save()

        serializer = ReturnRequestSerializer(return_request)

        return success_response(
            "Return request cancelled successfully",
            serializer.data
        )


class ApproveReturnView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        admin_note = request.data.get("admin_note")

        try:
            return_request = ReturnRequest.objects.get(returnid=pk)
        except ReturnRequest.DoesNotExist:
            return error_response("Return request not found", status.HTTP_404_NOT_FOUND)

        if return_request.status != "requested":
            return error_response("Only requested returns can be approved")

        return_request.status = "approved"
        return_request.admin_note = admin_note
        return_request.save()

        serializer = ReturnRequestSerializer(return_request)

        return success_response(
            "Return request approved successfully",
            serializer.data
        )


class RejectReturnView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        admin_note = request.data.get("admin_note")

        if not admin_note:
            return error_response("Admin note is required for rejection")

        try:
            return_request = ReturnRequest.objects.get(returnid=pk)
        except ReturnRequest.DoesNotExist:
            return error_response("Return request not found", status.HTTP_404_NOT_FOUND)

        if return_request.status != "requested":
            return error_response("Only requested returns can be rejected")

        return_request.status = "rejected"
        return_request.admin_note = admin_note
        return_request.save()

        serializer = ReturnRequestSerializer(return_request)

        return success_response(
            "Return request rejected successfully",
            serializer.data
        )