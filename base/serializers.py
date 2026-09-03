from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Item


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ItemSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Item
        fields = (
            "id",
            "creator",
            "item_name",
            "item_description",
            "item_price",
            "item_image",
        )

    def validate_item_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
