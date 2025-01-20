import hashlib
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from rest_framework import serializers

from .models import AccessLog, ShortenedURL


class ShortenedURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortenedURL
        fields = [
            "original_url",
            "short_url",
            "created_at",
            "expiration_hours",
            "expiration_at",
            "visits",
            "password",
        ]
        read_only_fields = ["short_url", "created_at", "expiration_at", "visits"]

    @classmethod
    def validate_url(cls, value):
        """
        Validate that the provided URL is well-formed.
        """
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise ValidationError("The input URL is not well-formed.")
        return value

    def create(self, validated_data):
        """
        Override the create method to handle the `created_at`, `expiration_at`,
        and `short_url` fields manually and call the model's save method.
        """
        if not validated_data.get("created_at"):
            validated_data["created_at"] = timezone.now()

        expiration_hours = validated_data.get("expiration_hours", 24)
        expiration_at = validated_data.get("expiration_at")
        if not expiration_at:
            expiration_at = validated_data["created_at"] + timedelta(
                hours=expiration_hours
            )
        validated_data["expiration_at"] = expiration_at

        # Generate the short URL
        if not validated_data.get("short_url"):
            validated_data["short_url"] = self.generate_short_url(
                validated_data["original_url"]
            )

        # call save method of model
        instance = ShortenedURL(**validated_data)
        instance.save()

        return instance

    def generate_short_url(self, original_url):
        """
        Generate a unique short URL identifier (e.g., 'abc123') based on the original URL.
        """
        if not original_url.startswith("http"):
            raise ValidationError("The original URL must start with 'http' or 'https'.")

        # Use SHA-256 to hash the URL and generate the short URL
        url_hash = hashlib.sha256(original_url.encode()).hexdigest()

        short_url_id = url_hash[
            :8
        ]  # Shorten to the first 8 characters (can be adjusted for scalability)
        short_url = f"{settings.BASE_URL}/{short_url_id}"

        return short_url


class AccessLogSerializer(serializers.ModelSerializer):
    short_url = serializers.CharField(source="short_url.short_url", read_only=True)

    class Meta:
        model = AccessLog
        fields = ["id", "short_url", "accessed_at", "user_agent", "ip_address"]
        read_only_fields = [
            "id",
            "accessed_at",
        ]  # Access time and ID are automatically generated

    def to_representation(self, instance):
        """
        show short_url as string
        """
        representation = super().to_representation(instance)
        representation["short_url"] = str(instance.short_url)
        return representation
