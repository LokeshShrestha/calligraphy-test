from django.contrib.auth.models import User
from rest_framework import serializers


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    class Meta:
        fields = ["username", "password"]

class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    class Meta:
        fields = ["image"]


class SimilaritySerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    processed_image_base64 = serializers.CharField(required=False, allow_blank=True)
    target_class = serializers.IntegerField(min_value=0, max_value=35)  # Updated to 36 classes (0-35)
    class Meta:
        fields = ["image", "processed_image_base64", "target_class"]
class FeedbackSerializer(serializers.Serializer):
    user_image = serializers.CharField(required=True)  # base64
    reference_image = serializers.CharField(required=True)  # base64
    blended_overlay = serializers.CharField(required=True)  # base64
    target_class = serializers.IntegerField(min_value=0, max_value=35)
    similarity_score = serializers.FloatField(required=True)
    distance = serializers.FloatField(required=True)
    is_same_character = serializers.BooleanField(required=True)
    class Meta:
        fields = ["user_image", "reference_image", "blended_overlay", "target_class", "similarity_score", "distance", "is_same_character"]
