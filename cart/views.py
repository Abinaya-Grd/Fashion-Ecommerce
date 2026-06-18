from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
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


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return success_response("Cart fetched successfully", serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")
        variant_id = request.data.get("variant")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(productid=product_id)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        variant = None
        price = product.offer_price or product.price

        if variant_id:
            try:
                variant = ProductVariant.objects.get(variantid=variant_id)
                price = variant.offer_price or variant.price
            except ProductVariant.DoesNotExist:
                return error_response("Variant not found", status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={
                "quantity": quantity,
                "price": price
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return success_response(
            "Product added to cart successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )
        
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        try:
            cart_item = CartItem.objects.get(
                cartitemid=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return error_response(
                "Cart item not found",
                status.HTTP_404_NOT_FOUND
            )

        quantity = int(request.data.get("quantity", 1))

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return success_response(
            "Cart updated successfully",
            serializer.data
        )

class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        try:
            cart_item = CartItem.objects.get(
                cartitemid=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return error_response(
                "Cart item not found",
                status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        return success_response(
            "Item removed from cart successfully"
        )

class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )

        cart.items.all().delete()

        return success_response(
            "Cart cleared successfully"
        )                        