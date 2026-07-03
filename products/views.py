import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from orders.models import OrderItem
from .models import Product, ProductImage, Color, Size, ProductVariant, RecentlyViewedProduct
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
    ColorSerializer,
    SizeSerializer,
    ProductVariantSerializer,
)

logger = logging.getLogger("ecommerce")


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
        search = request.query_params.get("search")
        category_id = request.query_params.get("category_id")
        subcategory_id = request.query_params.get("subcategory_id")
        product_style_id = request.query_params.get("product_style_id")
        brand_id = request.query_params.get("brand_id")
        color_id = request.query_params.get("color_id")
        size_id = request.query_params.get("size_id")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        in_stock = request.query_params.get("in_stock")
        offer = request.query_params.get("offer")
        sort_by = request.query_params.get("sort_by")

        products = Product.objects.filter(status="active").order_by("-productid")

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(category__name__icontains=search) |
                Q(subcategory__name__icontains=search)
            )

        if category_id:
            products = products.filter(category_id=category_id)

        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        if product_style_id:
            products = products.filter(product_style_id=product_style_id)

        if brand_id:
            products = products.filter(brand_id=brand_id)

        if color_id:
            products = products.filter(variants__color_id=color_id)

        if size_id:
            products = products.filter(variants__size_id=size_id)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        if in_stock == "true":
            products = products.filter(is_in_stock=True)

        if in_stock == "false":
            products = products.filter(is_in_stock=False)

        if offer == "true":
            products = products.filter(offer_price__isnull=False)

        products = products.distinct()

        if sort_by == "price_low_high":
            products = products.order_by("price")
        elif sort_by == "price_high_low":
            products = products.order_by("-price")
        elif sort_by == "latest":
            products = products.order_by("-created_at")
        elif sort_by == "oldest":
            products = products.order_by("created_at")
        elif sort_by == "name_asc":
            products = products.order_by("name")
        elif sort_by == "name_desc":
            products = products.order_by("-name")

        page_number = request.query_params.get("page", 1)
        page_size = int(request.query_params.get("page_size", 10))

        paginator = Paginator(products, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = ProductSerializer(page_obj.object_list, many=True)

        return Response({
            "success": True,
            "message": "Products fetched successfully",
            "total_products": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "data": serializer.data
        })

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()

            logger.info(
                f"Product created | ID={product.productid} | Name={product.name}"
            )

            return success_response(
                "Product created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        logger.warning(f"Product creation failed | Errors={serializer.errors}")
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
            logger.warning(
                f"Full product creation failed | Errors={product_serializer.errors}"
            )
            return Response(
                product_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        product = product_serializer.save()

        logger.info(
            f"Full product created | ID={product.productid} | Name={product.name}"
        )

        images = request.FILES.getlist("images")
        uploaded_images = []

        for image in images:
            product_image = ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=False
            )

            logger.info(
                f"Product image uploaded | ProductID={product.productid} | Image={product_image.image.name}"
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
            product = Product.objects.get(productid=pk)
        except Product.DoesNotExist:
            logger.warning(f"Product fetch failed | ProductID={pk}")
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)

        return success_response(
            "Product fetched successfully",
            serializer.data
        )

    def put(self, request, pk):
        try:
            product = Product.objects.get(productid=pk)
        except Product.DoesNotExist:
            logger.warning(f"Product update failed | ProductID={pk}")
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            product = serializer.save()

            logger.info(
                f"Product updated | ID={product.productid} | Name={product.name}"
            )

            return success_response(
                "Product updated successfully",
                serializer.data
            )

        logger.warning(
            f"Product update validation failed | ProductID={pk} | Errors={serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(productid=pk)
        except Product.DoesNotExist:
            logger.warning(f"Product delete failed | ProductID={pk}")
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        logger.info(
            f"Product deleted | ID={product.productid} | Name={product.name}"
        )

        product.delete()

        return success_response("Product deleted successfully")


class ProductImageListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        product_id = request.query_params.get("product_id")

        images = ProductImage.objects.all().order_by("-imageid")

        if product_id:
            images = images.filter(product_id=product_id)

        serializer = ProductImageSerializer(images, many=True)

        return success_response(
            "Product images fetched successfully",
            serializer.data
        )

    def post(self, request):
        product_id = request.data.get("product")
        images = request.FILES.getlist("images")

        if not product_id:
            logger.warning("Product image upload failed | Product missing")
            return error_response("Product is required")

        if not images:
            logger.warning(f"Product image upload failed | ProductID={product_id} | No images")
            return error_response("At least one image is required")

        uploaded_images = []

        for image in images:
            serializer = ProductImageSerializer(data={
                "product": product_id,
                "image": image,
                "is_primary": False
            })

            if serializer.is_valid():
                product_image = serializer.save()

                logger.info(
                    f"Product image uploaded | ProductID={product_id} | ImageID={product_image.imageid}"
                )

                uploaded_images.append(serializer.data)
            else:
                logger.warning(
                    f"Product image upload failed | ProductID={product_id} | Errors={serializer.errors}"
                )
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
            image = ProductImage.objects.get(imageid=pk)
        except ProductImage.DoesNotExist:
            logger.warning(f"Product image update failed | ImageID={pk}")
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
            product_image = serializer.save()

            logger.info(
                f"Product image updated | ImageID={product_image.imageid} | ProductID={product_image.product.productid}"
            )

            return success_response(
                "Product image updated successfully",
                serializer.data
            )

        logger.warning(
            f"Product image update validation failed | ImageID={pk} | Errors={serializer.errors}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            image = ProductImage.objects.get(imageid=pk)
        except ProductImage.DoesNotExist:
            logger.warning(f"Product image delete failed | ImageID={pk}")
            return error_response(
                "Product image not found",
                status.HTTP_404_NOT_FOUND
            )

        logger.info(
            f"Product image deleted | ImageID={image.imageid} | ProductID={image.product.productid}"
        )

        image.delete()

        return success_response("Product image deleted successfully")


class ColorListCreateView(APIView):
    def get(self, request):
        colors = Color.objects.all().order_by("-colorid")
        serializer = ColorSerializer(colors, many=True)
        return success_response("Colors fetched successfully", serializer.data)

    def post(self, request):
        serializer = ColorSerializer(data=request.data)

        if serializer.is_valid():
            color = serializer.save()

            logger.info(
                f"Color created | ID={color.colorid} | Name={color.name}"
            )

            return success_response(
                "Color created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        logger.warning(f"Color creation failed | Errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SizeListCreateView(APIView):
    def get(self, request):
        sizes = Size.objects.all().order_by("-sizeid")
        serializer = SizeSerializer(sizes, many=True)
        return success_response("Sizes fetched successfully", serializer.data)

    def post(self, request):
        serializer = SizeSerializer(data=request.data)

        if serializer.is_valid():
            size = serializer.save()

            logger.info(
                f"Size created | ID={size.sizeid} | Name={size.name}"
            )

            return success_response(
                "Size created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        logger.warning(f"Size creation failed | Errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantListCreateView(APIView):
    def get(self, request):
        product_id = request.query_params.get("product_id")
        color_id = request.query_params.get("color_id")
        size_id = request.query_params.get("size_id")

        variants = ProductVariant.objects.all().order_by("-variantid")

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
            variant = serializer.save()

            logger.info(
                f"Variant created | VariantID={variant.variantid} | ProductID={variant.product.productid} | SKU={variant.sku}"
            )

            return success_response(
                "Product variant created successfully",
                serializer.data,
                status.HTTP_201_CREATED
            )

        logger.warning(f"Variant creation failed | Errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelatedProductsView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(productid=pk, status="active")
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(
            status="active",
            category=product.category
        ).exclude(productid=product.productid).order_by("-created_at")[:8]

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Related products fetched successfully",
            serializer.data
        )


class LatestProductsView(APIView):
    def get(self, request):
        products = Product.objects.filter(
            status="active"
        ).order_by("-created_at")[:12]

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Latest products fetched successfully",
            serializer.data
        )


class FeaturedProductsView(APIView):
    def get(self, request):
        products = Product.objects.filter(
            status="active",
            offer_price__isnull=False
        ).order_by("-created_at")[:12]

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Featured products fetched successfully",
            serializer.data
        )


class BestSellerProductsView(APIView):
    def get(self, request):
        best_sellers = OrderItem.objects.values(
            "product"
        ).annotate(
            total_sold=Sum("quantity")
        ).order_by("-total_sold")[:12]

        product_ids = [item["product"] for item in best_sellers]

        products = Product.objects.filter(
            productid__in=product_ids,
            status="active"
        )

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Best seller products fetched successfully",
            serializer.data
        )


class AddRecentlyViewedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            product = Product.objects.get(productid=pk, status="active")
        except Product.DoesNotExist:
            return error_response("Product not found", status.HTTP_404_NOT_FOUND)

        RecentlyViewedProduct.objects.update_or_create(
            user=request.user,
            product=product
        )

        logger.info(
            f"Recently viewed added | User={request.user.email} | ProductID={product.productid}"
        )

        return success_response("Product added to recently viewed")


class RecentlyViewedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        viewed = RecentlyViewedProduct.objects.filter(
            user=request.user
        ).select_related("product").order_by("-viewed_at")[:10]

        products = [item.product for item in viewed]
        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Recently viewed products fetched successfully",
            serializer.data
        )


class RecommendedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        viewed_categories = RecentlyViewedProduct.objects.filter(
            user=request.user
        ).values_list("product__category", flat=True)

        products = Product.objects.filter(
            status="active",
            category__in=viewed_categories
        ).exclude(
            viewed_by__user=request.user
        ).distinct().order_by("-created_at")[:12]

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Recommended products fetched successfully",
            serializer.data
        )


class FrequentlyBoughtTogetherView(APIView):
    def get(self, request, pk):
        order_ids = OrderItem.objects.filter(
            product_id=pk
        ).values_list("order_id", flat=True)

        product_ids = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(
            product_id=pk
        ).values("product").annotate(
            total_bought=Sum("quantity")
        ).order_by("-total_bought")[:8]

        ids = [item["product"] for item in product_ids]

        products = Product.objects.filter(
            productid__in=ids,
            status="active"
        )

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Frequently bought together products fetched successfully",
            serializer.data
        )


class TrendingProductsView(APIView):
    def get(self, request):
        last_30_days = timezone.now() - timedelta(days=30)

        product_ids = OrderItem.objects.filter(
            order__created_at__gte=last_30_days,
            order__payment_status="paid"
        ).values("product").annotate(
            total_sold=Sum("quantity")
        ).order_by("-total_sold")[:12]

        ids = [item["product"] for item in product_ids]

        products = Product.objects.filter(
            productid__in=ids,
            status="active"
        )

        serializer = ProductSerializer(products, many=True)

        return success_response(
            "Trending products fetched successfully",
            serializer.data
        )