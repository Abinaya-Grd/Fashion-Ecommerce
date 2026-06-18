from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Category, SubCategory, ProductStyle, Brand
from .serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ProductStyleSerializer,
    BrandSerializer,
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


class CategoryListCreateView(APIView):
    def get(self, request):
        categories = Category.objects.all().order_by('-id')
        serializer = CategorySerializer(categories, many=True)
        return success_response("Categories fetched successfully", serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Category created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category)
        return success_response("Category fetched successfully", serializer.data)

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return success_response("Category updated successfully", serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return error_response("Category not found", status.HTTP_404_NOT_FOUND)

        category.delete()
        return success_response("Category deleted successfully")


class SubCategoryListCreateView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')

        subcategories = SubCategory.objects.all().order_by('-id')

        if category_id:
            subcategories = subcategories.filter(category_id=category_id)

        serializer = SubCategorySerializer(subcategories, many=True)

        return success_response(
            "Subcategories fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = SubCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Subcategory created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubCategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            subcategory = SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return error_response("Subcategory not found", status.HTTP_404_NOT_FOUND)

        serializer = SubCategorySerializer(subcategory)

        return success_response(
            "Subcategory fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        try:
            subcategory = SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return error_response("Subcategory not found", status.HTTP_404_NOT_FOUND)

        serializer = SubCategorySerializer(
            subcategory,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Subcategory updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            subcategory = SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return error_response("Subcategory not found", status.HTTP_404_NOT_FOUND)

        subcategory.delete()

        return success_response("Subcategory deleted successfully")


class ProductStyleListCreateView(APIView):
    def get(self, request):
        subcategory_id = request.query_params.get('subcategory_id')

        styles = ProductStyle.objects.all().order_by('-id')

        if subcategory_id:
            styles = styles.filter(subcategory_id=subcategory_id)

        serializer = ProductStyleSerializer(styles, many=True)

        return success_response(
            "Styles fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = ProductStyleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Style created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductStyleDetailView(APIView):
    def get(self, request, pk):
        try:
            style = ProductStyle.objects.get(pk=pk)
        except ProductStyle.DoesNotExist:
            return error_response("Style not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductStyleSerializer(style)

        return success_response(
            "Style fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        try:
            style = ProductStyle.objects.get(pk=pk)
        except ProductStyle.DoesNotExist:
            return error_response("Style not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductStyleSerializer(
            style,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Style updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            style = ProductStyle.objects.get(pk=pk)
        except ProductStyle.DoesNotExist:
            return error_response("Style not found", status.HTTP_404_NOT_FOUND)

        style.delete()

        return success_response("Style deleted successfully")


class BrandListCreateView(APIView):
    def get(self, request):
        brands = Brand.objects.all().order_by('-id')
        serializer = BrandSerializer(brands, many=True)

        return success_response(
            "Brands fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = BrandSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Brand created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandDetailView(APIView):
    def get(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return error_response("Brand not found", status.HTTP_404_NOT_FOUND)

        serializer = BrandSerializer(brand)

        return success_response(
            "Brand fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return error_response("Brand not found", status.HTTP_404_NOT_FOUND)

        serializer = BrandSerializer(
            brand,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return success_response(
                "Brand updated successfully",
                serializer.data
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return error_response("Brand not found", status.HTTP_404_NOT_FOUND)

        brand.delete()

        return success_response("Brand deleted successfully")