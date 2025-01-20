from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.conf import settings
from .models import ShortenedURL, AccessLog
from .serializers import ShortenedURLSerializer


class URLShortenerTests(TestCase):

    def setUp(self):
        # Setup a sample shortened URL for testing
        self.original_url = "https://example.com"
        self.short_url = "abcd1234"  # Assuming we are using the short URL directly
        self.shortened_url = ShortenedURL.objects.create(original_url=self.original_url, short_url=self.short_url)

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "urlshortenerapp/home.html")

    def test_create_shortened_url_success(self):
        data = {"original_url": "https://test.com"}
        response = self.client.post("/shorten", data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("short_url", response.json())

    def test_create_shortened_url_failure(self):
        data = {"original_url": "not_a_valid_url"}
        response = self.client.post("/shorten", data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_visit_shortened_url_redirect_success(self):
        data = {"original_url": "https://test.com"}
        response = self.client.post("/shorten", data, content_type="application/json")
        short_url = response.json()["short_url"].split("/")[-1]
        response = self.client.get(f"/{short_url}")
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
    
    def test_visit_shortened_url_not_found(self):
        response = None
        try:
            non_existent_short_url = "nonexistenturl"
            response = self.client.get("/shorten", args=[non_existent_short_url])
        except Exception as e:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_visit_shortened_url_with_password_success(self):
        password = "securepassword"
        self.shortened_url.password = password
        self.shortened_url.save()

        response = self.client.get(f"/{self.short_url}", {"password": password})
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_visit_shortened_url_with_password_failure(self):
        response = None
        try:
            password = "securepassword"
            self.shortened_url.password = password
            self.shortened_url.save()

            response = self.client.get(f"/{self.short_url}", {"password": "wrong_password"})
        except:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analytics_success(self):
        response = self.client.get(f"/analytics/{self.short_url}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_failure(self):
        response = None
        try:
            response = self.client.get(f"/analytics/nonexistenturl")
        except:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

