from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db.models import F
from django.utils import timezone
from django.db import models, transaction

class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=400)
    short_url = models.CharField(max_length=50, default="", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_hours = models.IntegerField(default=24,validators=[MaxValueValidator(10**7)] )
    expiration_at = models.DateTimeField(null=True, blank=True, default=None)
    visits = models.IntegerField(default=0)
    password = models.CharField(
        max_length=255, blank=True, null=True
    )  # Optional password to access the URL

    def save(self, *args, **kwargs):
        try:
            existing_url = ShortenedURL.objects.filter(short_url=self.short_url).first()
            # Update operation
            if existing_url:
                updated_fields = {}
                for field in self._meta.fields:
                    field_name = field.name
                    if field_name not in ("created_at","short_url","id"):
                        new_value = getattr(self, field_name)
                        updated_fields[field_name] = new_value
                if "password" not in updated_fields:
                    updated_fields["password"] = None
               
                # Update the fields in the database using the short_url to find the existing record
                existing_url.__class__.objects.filter(
                    short_url=existing_url.short_url
                ).update(**updated_fields)

            else:
                # Create operation
                super().save(*args, **kwargs)
        except Exception as e:
            print(str(e))
            raise Exception("Error saving the shortened URL")

    # Delete operation
    @classmethod
    def delete_by_short_url(cls, short_url):
        """Delete a ShortenedURL based on short_url."""
        try:
            record = cls.objects.get(short_url=short_url)
            record.delete()
        except cls.DoesNotExist:
            pass

    def update_visits(self):
        """Increment the visit count for the shortened URL."""
        self.visits = F("visits") + 1
        with transaction.atomic():
            super().save(update_fields=["visits"])

    def is_expired(self):
        """Check if the shortened URL has expired."""
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
