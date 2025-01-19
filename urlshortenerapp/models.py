import hashlib
import time
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError, models, transaction
from django.db.models import F
from django.utils import timezone


class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=400)
    short_url = models.CharField(max_length=50, default="", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(null=True, blank=True, default=None)
    visits = models.IntegerField(default=0)
    password = models.CharField(
        max_length=255, blank=True, null=True
    )  # Optional password to access the URL

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()

        if not self.expiration_at:
            # set the default expiration at to 24 hours from now
            self.expiration_at = self.created_at + timedelta(hours=24)

        if not self.short_url:
            self.short_url = self.generate_short_url()
        existing_url = ShortenedURL.objects.filter(short_url=self.short_url).first()
        # Update operation
        if existing_url:
            updated_fields = {}
            for field in self._meta.fields:
                field_name = field.name
                if field_name != "created_at" and field_name != "short_url":
                    new_value = getattr(existing_url, field_name)
                    updated_fields[field_name] = new_value

            # Update the fields in the database using the short_url to find the existing record
            existing_url.__class__.objects.filter(
                short_url=existing_url.short_url
            ).update(**updated_fields)

        else:
            # Create operation
            super().save(*args, **kwargs)

    # Delete operation
    @classmethod
    def delete_by_short_url(cls, short_url):
        """Delete a ShortenedURL based on short_url."""
        try:
            record = cls.objects.get(short_url=short_url)
            record.delete()
        except cls.DoesNotExist:
            pass

    # Function to generate a unique short URL, ensure requests are Idempotent
    def generate_short_url(self):
        """
        Generate a unique short URL identifier (e.g., 'abc123').
        """
        if not self.original_url.startswith("http"):
            raise ValidationError("The original URL must start with 'http' or 'https'.")

        # Use SHA-256 to hash the URL
        url_hash = hashlib.sha256(self.original_url.encode()).hexdigest()

        short_url_id = url_hash[
            :8
        ]  # 8 characters: can be increased for more unique URLs

        # Generate the full short URL
        short_url = f"{settings.BASE_URL}/{short_url_id}"

        return short_url

    @classmethod
    def validate_url(cls, url):
        """
        Validate that the provided URL is well-formed.
        """
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError("The original URL is not well-formed.")

    def update_visits(self):

        print(
            f"Updating visits for {self.short_url}"
        )  # Add this line to see when it's called
        self.refresh_from_db()
        self.visits = F("visits") + 1
        with transaction.atomic():
            super().save(update_fields=["visits"])

    def is_expired(self):
        return timezone.now() > self.expiration_at

    def __str__(self):
        return f"{self.original_url} -> {self.short_url}"


class AccessLog(models.Model):
    short_url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.short_url} - {self.ip_address} - {self.access_date}"

    class Meta:
        verbose_name_plural = "Access logs"
