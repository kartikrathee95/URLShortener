import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=400)
    short_url = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_at = models.DateTimeField(
        null=True, blank=True, default=None
    )
    visits = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.expiration_at:
            # set the default expiration at to 24 hours from now
            self.expiration_at = timezone.now() + timedelta(hours=24)

        if not self.short_url:
            self.short_url = self.generate_short_url()

        # CRUD operations
        super().save(*args, **kwargs)

    def generate_short_url(self):
        """
        Generate a unique short URL identifier (e.g., 'abc123').
        """
        if not self.original_url.startswith("http"):
            raise ValidationError("The original URL must start with 'http' or 'https'.")

        # generate a random suffix using all characters and digits
        all_chars = string.ascii_letters + string.digits
        length = 6
        short_url = "".join(random.choice(all_chars for _ in range(length)))
        while ShortenedURL.objects.filter(short_url=short_url).exists():
            short_url = "".join(random.choice(all_chars for _ in range(length)))

        return short_url

    def get_full_short_url(self):
        return settings.SITE_URL + self.short_url

    def is_expired(self):
        return timezone.now() > self.expiration_at

    def __str__(self):
        return f"{self.original_url} -> {self.short_url}"


class AccessLog(models.Model):
    short_url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE)
    access_date = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.short_url} - {self.ip_address} - {self.access_date}"

    class Meta:
        verbose_name_plural = "Access logs"
