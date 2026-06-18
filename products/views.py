from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product, ProductImage, Color, Size, ProductVariant
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
    ColorSerializer,
    SizeSerializer,
    ProductVariantSerializer,
)


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


class ProductListCreateView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        product_style_id = request.query_params.get('product_style_id')
        brand_id = request.query_params.get('brand_id')

        products = Product.objects.all().order_by('-productid')

        if category_id:
            products = products.filter(category_id=category_id)

        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        if product_style_id:
            products = products.filter(product_style_id=product_style_id)

        if brand_id:
            products = products.filter(brand_id=brand_id)

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Products fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Product created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductFullCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        product_data = {
            "category": request.data.get("category"),
            "subcategory": request.data.get("subcategory"),
            "product_style": request.data.get("product_style"),
            "brand": request.data.get("brand"),
            "name": request.data.get("name"),
            "price": request.data.get("price"),
            "offer_price": request.data.get("offer_price"),
            "stock": request.data.get("stock"),
            "description": request.data.get("description"),
            "status": request.data.get("status", "active"),
        }

        product_serializer = ProductSerializer(data=product_data)

        if not product_serializer.is_valid():
            return Response(
                product_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        product = product_serializer.save()

        images = request.FILES.getlist("images")

        uploaded_images = []

        for image in images:
            product_image = ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=False
            )
            uploaded_images.append(
                ProductImageSerializer(product_image).data
            )

        response_data = ProductSerializer(product).data
        response_data["uploaded_images"] = uploaded_images

        return success_response(
            "Full product created successfully",
            response_data,
            status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)

        return success_response(
            "Product fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Product updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        product.delete()

        return success_response("Product deleted successfully")


class ProductImageListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        product_id = request.query_params.get('product_id')

        images = ProductImage.objects.all().order_by('-imageid')

        if product_id:
            images = images.filter(product_id=product_id)

        serializer = ProductImageSerializer(images, many=True)

        return success_response(
            "Product images fetched successfully",
            serializer.data
        )

    def post(self, request):
        product_id = request.data.get('product')
        images = request.FILES.getlist('images')

        if not product_id:
            return error_response("Product is required")

        if not images:
            return error_response("At least one image is required")

        uploaded_images = []

        for image in images:
            serializer = ProductImageSerializer(data={
                'product': product_id,
                'image': image,
                'is_primary': False
            })

            if serializer.is_valid():
                serializer.save()
                uploaded_images.append(serializer.data)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        return success_response(
            "Product images uploaded successfully",
            uploaded_images,
            status.HTTP_201_CREATED
        )


class ProductImageDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return error_response(
                "Product image not found",
                status.HTTP_404_NOT_FOUND
            )

        serializer = ProductImageSerializer(
            image,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Product image updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return error_response(
                "Product image not found",
                status.HTTP_404_NOT_FOUND
            )

        image.delete()

        return success_response("Product image deleted successfully")


class ColorListCreateView(APIView):
    def get(self, request):
        colors = Color.objects.all().order_by('-colorid')
        serializer = ColorSerializer(colors, many=True)
        return success_response("Colors fetched successfully", serializer.data)

    def post(self, request):
        serializer = ColorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Color created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SizeListCreateView(APIView):
    def get(self, request):
        sizes = Size.objects.all().order_by('-sizeid')
        serializer = SizeSerializer(sizes, many=True)
        return success_response("Sizes fetched successfully", serializer.data)

    def post(self, request):
        serializer = SizeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Size created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantListCreateView(APIView):
    def get(self, request):
        product_id = request.query_params.get('product_id')
        color_id = request.query_params.get('color_id')
        size_id = request.query_params.get('size_id')

        variants = ProductVariant.objects.all().order_by('-variantid')

        if product_id:
            variants = variants.filter(product_id=product_id)

        if color_id:
            variants = variants.filter(color_id=color_id)

        if size_id:
            variants = variants.filter(size_id=size_id)

        serializer = ProductVariantSerializer(variants, many=True)

        return success_response(
            "Product variants fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = ProductVariantSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Product variant created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)