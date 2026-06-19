from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'reviewid',
            'user',
            'user_name',
            'product',
            'product_name',
            'rating',
            'comment',
            'status',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value