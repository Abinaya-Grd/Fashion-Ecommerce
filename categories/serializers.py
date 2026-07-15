from rest_framework import serializers
from .models import Category, SubCategory, ProductStyle, Brand


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    subcategoryid = serializers.IntegerField(source='id', read_only=True)
    categoryid = serializers.IntegerField(source='category.id', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            'subcategoryid',
            'categoryid',
            'category',
            'category_details',
            'name',
            'slug',
            'image',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'category': {'write_only': True}
        }


class ProductStyleSerializer(serializers.ModelSerializer):
    styleid = serializers.IntegerField(source='id', read_only=True)
    subcategoryid = serializers.IntegerField(source='subcategory.id', read_only=True)
    subcategory_details = SubCategorySerializer(source='subcategory', read_only=True)

    class Meta:
        model = ProductStyle
        fields = [
            'styleid',
            'subcategory',
            'subcategoryid',
            'subcategory_details',
            'name',
            'slug',
            'image',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'subcategory': {'write_only': True}
        }


class BrandSerializer(serializers.ModelSerializer):
    brandid = serializers.IntegerField(source="id", read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "brandid",
            "name",
            "slug",
            "logo",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.build_url()
        return None