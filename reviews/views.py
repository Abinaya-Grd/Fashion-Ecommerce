from django.db.models import Avg, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Review
from .serializers import ReviewSerializer
from products.models import Product


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


class ReviewListCreateView(APIView):

    def get(self, request):
        product_id = request.query_params.get("product_id")

        reviews = Review.objects.filter(status="active").order_by("-reviewid")

        if product_id:
            reviews = reviews.filter(product_id=product_id)

        serializer = ReviewSerializer(reviews, many=True)

        return success_response("Reviews fetched successfully", serializer.data)


class AddReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        try:
            product = Product.objects.get(productid=product_id)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        if Review.objects.filter(user=request.user, product=product).exists():
            return error_response("You already reviewed this product")

        serializer = ReviewSerializer(data={
            "product": product.productid,
            "rating": rating,
            "comment": comment,
            "status": "active"
        })

        if serializer.is_valid():
            serializer.save(user=request.user)

            return success_response(
                "Review added successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRatingSummaryView(APIView):

    def get(self, request, product_id):
        reviews = Review.objects.filter(
            product_id=product_id,
            status="active"
        )

        summary = reviews.aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("reviewid")
        )

        return success_response(
            "Rating summary fetched successfully",
            summary
        )