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
    image1 = serializers.ImageField()
    image2 = serializers.ImageField()
    class Meta:
        fields = ["image1", "image2"]


class GradCAMSerializer(serializers.Serializer):
    image = serializers.ImageField()
    target_class = serializers.IntegerField(required=False, min_value=0, max_value=61)
    class Meta:
        fields = ["image", "target_class"]