from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from .serializers import WishlistSerializer
from products.models import Product, ProductVariant


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


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist = Wishlist.objects.filter(user=request.user).order_by('-wishlistid')
        serializer = WishlistSerializer(wishlist, many=True)

        return success_response(
            "Wishlist fetched successfully",
            serializer.data
        )


class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")
        variant_id = request.data.get("variant")

        try:
            product = Product.objects.get(productid=product_id)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        variant = None

        if variant_id:
            try:
                variant = ProductVariant.objects.get(variantid=variant_id)
            except ProductVariant.DoesNotExist:
                return error_response("Variant not found", status.HTTP_404_NOT_FOUND)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product,
            variant=variant
        )

        if not created:
            return error_response("Product already in wishlist")

        serializer = WishlistSerializer(wishlist_item)

        return success_response(
            "Product added to wishlist successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )


class RemoveWishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            wishlist_item = Wishlist.objects.get(
                wishlistid=pk,
                user=request.user
            )
        except Wishlist.DoesNotExist:
            return error_response("Wishlist item not found", status.HTTP_404_NOT_FOUND)

        wishlist_item.delete()

        return success_response("Wishlist item removed successfully")


class ClearWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Wishlist.objects.filter(user=request.user).delete()

        return success_response("Wishlist cleared successfully")