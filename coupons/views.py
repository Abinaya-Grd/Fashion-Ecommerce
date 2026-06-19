from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Coupon
from .serializers import CouponSerializer


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


class CouponListCreateView(APIView):

    def get(self, request):
        coupons = Coupon.objects.all().order_by('-couponid')
        serializer = CouponSerializer(coupons, many=True)

        return success_response(
            "Coupons fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = CouponSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Coupon created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponDetailView(APIView):

    def get(self, request, pk):
        try:
            coupon = Coupon.objects.get(couponid=pk)
        except Coupon.DoesNotExist:
            return error_response("Coupon not found", status.HTTP_404_NOT_FOUND)

        serializer = CouponSerializer(coupon)
        return success_response("Coupon fetched successfully", serializer.data)

    def put(self, request, pk):
        try:
            coupon = Coupon.objects.get(couponid=pk)
        except Coupon.DoesNotExist:
            return error_response("Coupon not found", status.HTTP_404_NOT_FOUND)

        serializer = CouponSerializer(coupon, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Coupon updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            coupon = Coupon.objects.get(couponid=pk)
        except Coupon.DoesNotExist:
            return error_response("Coupon not found", status.HTTP_404_NOT_FOUND)

        coupon.delete()
        return success_response("Coupon deleted successfully")


class ApplyCouponView(APIView):

    def post(self, request):
        code = request.data.get("code")
        order_amount = Decimal(str(request.data.get("order_amount", 0)))

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return error_response("Invalid coupon code")

        if not coupon.is_valid_coupon():
            return error_response("Coupon expired or inactive")

        if order_amount < coupon.min_order_amount:
            return error_response("Order amount is less than minimum amount")

        if coupon.discount_type == "percentage":
            discount_amount = (order_amount * coupon.discount_value) / 100
        else:
            discount_amount = coupon.discount_value

        final_amount = order_amount - discount_amount

        if final_amount < 0:
            final_amount = 0

        return success_response(
            "Coupon applied successfully",
            {
                "coupon_code": coupon.code,
                "order_amount": order_amount,
                "discount_amount": discount_amount,
                "final_amount": final_amount
            }
        )