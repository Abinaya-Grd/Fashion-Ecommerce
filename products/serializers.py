from rest_framework import serializers
from .models import Product, ProductImage,Color,Size,ProductVariant
from categories.serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ProductStyleSerializer,
    BrandSerializer
)

class ProductSerializer(serializers.ModelSerializer):
    categoryid = serializers.IntegerField(source='category.id', read_only=True)
    subcategoryid = serializers.IntegerField(source='subcategory.id', read_only=True)
    productstyleid = serializers.IntegerField(source='product_style.id', read_only=True)
    brandid = serializers.IntegerField(source='brand.id', read_only=True)

    category_details = CategorySerializer(source='category', read_only=True)
    subcategory_details = SubCategorySerializer(source='subcategory', read_only=True)
    product_style_details = ProductStyleSerializer(source='product_style', read_only=True)
    brand_details = BrandSerializer(source='brand', read_only=True)

    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'productid',

            'category',
            'subcategory',
            'product_style',
            'brand',

            'categoryid',
            'subcategoryid',
            'productstyleid',
            'brandid',

            'category_details',
            'subcategory_details',
            'product_style_details',
            'brand_details',
            'name',
            'slug',
            'sku',
            'thumbnail',
            'price',
            'offer_price',
            'stock',
            'is_in_stock',
            'stock_status',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'category': {'write_only': True},
            'subcategory': {'write_only': True},
            'product_style': {'write_only': True, 'required': False},
            'brand': {'write_only': True},
        }

    def get_stock_status(self, obj):
        if obj.stock == 0:
            return "Out of Stock"
        elif obj.stock <= 5:
            return "Limited Stock"
        return "In Stock"

class ProductImageSerializer(serializers.ModelSerializer):
    productid = serializers.IntegerField(source='product.productid', read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            'imageid',
            'product',
            'productid',
            'image',
            'is_primary',
            'created_at',
        ]

        extra_kwargs = {
            'product': {'write_only': True}
        } 
   
class ColorSerializer(serializers.ModelSerializer):
    

   class Meta:
    model = Color
    fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):


  class Meta:
    model = Size
    fields = '__all__'


class ProductVariantSerializer(serializers.ModelSerializer):


  variantid = serializers.IntegerField(
    source='id',
    read_only=True
  )

  productid = serializers.IntegerField(
    source='product.productid',
    read_only=True
  )

  colorid = serializers.IntegerField(
    source='color.colorid',
    read_only=True
 )

  sizeid = serializers.IntegerField(
    source='size.sizeid',
    read_only=True
  )

  product_details = ProductSerializer(
    source='product',
    read_only=True
  )

  color_details = ColorSerializer(
    source='color',
    read_only=True
 )

  size_details = SizeSerializer(
    source='size',
    read_only=True
 )

  class Meta:
    model = ProductVariant

    fields = [
        'variantid',

        'product',
        'productid',
        'product_details',

        'color',
        'colorid',
        'color_details',

        'size',
        'sizeid',
        'size_details',

        'sku',
        'price',
        'offer_price',
        'stock',
        'is_in_stock',
        'status',

        'created_at',
        'updated_at',
    ]

    extra_kwargs = {
        'product': {'write_only': True},
        'color': {'write_only': True},
        'size': {'write_only': True},
    }
        
           