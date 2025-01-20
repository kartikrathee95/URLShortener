from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AccessLog, ShortenedURL
from .serializers import ShortenedURLSerializer


@swagger_auto_schema(method="GET", responses={200: "OK"})
@api_view(["GET"])
def home(request):
    return render(request, "urlshortenerapp/home.html")


# POST request to create a new shortened URL
@csrf_exempt
@swagger_auto_schema(
    method="POST",
    request_body=ShortenedURLSerializer,
    responses={
        201: "Created",
        400: "Bad Request",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    },
)
@api_view(["POST"])
def shorten_url(request):
    try:
        if request.method == "POST":
            # Deserialize the request data using ShortenedURLSerializer
            serializer = ShortenedURLSerializer(data=request.data)
            if serializer.is_valid():
                shortened_url = serializer.create(serializer.validated_data)
                return JsonResponse(
                    {"short_url": shortened_url.short_url},
                    status=status.HTTP_201_CREATED,
                )

            else:
                return JsonResponse(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

    except ValidationError as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Function to redirect to the original URL)
def redirect_to_original(shortened_url):
    return HttpResponseRedirect(shortened_url.original_url)


# Function to log the access (GET request)
def log_access_to_url(request, shortened_url):
    # Fetch the user's IP address
    ip_address = request.META.get("REMOTE_ADDR", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    # save access log entry
    AccessLog.objects.create(
        short_url=shortened_url, ip_address=ip_address, user_agent=user_agent
    )


# GET request to visit the shortened URL
@csrf_exempt
@swagger_auto_schema(
    method="GET",
    responses={
        200: "Success",
        301: "Redirect",
        302: "Redirect",
        404: "Not Found",
        403: "Forbidden",
    },
)
@api_view(["GET"])
def visit_shortened_url(request, short_url):
    try:
        short_url = settings.BASE_URL + "/" + short_url
        shortened_url = get_object_or_404(ShortenedURL, short_url=short_url)
        if shortened_url.is_expired():
            return JsonResponse(
                {"error": "This URL has expired, Please create a new shortened URL"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # If the URL has a password, check if the user has provided the correct password
        if shortened_url.password:
            entered_password = request.GET.get("password")
            if not entered_password or entered_password != shortened_url.password:
                return JsonResponse(
                    {"error": "Password required or incorrect password"}, status=403
                )
        # Update the access count
        shortened_url.update_visits()
        # Log the access
        log_access_to_url(request, shortened_url)
        user_agent = request.headers.get("Referer", "")
        if "swagger" in user_agent:
            # Return the URL in the response instead of performing the redirect
            return JsonResponse(
                {
                    "short_url": shortened_url.short_url,
                    "redirect_to": shortened_url.original_url,
                },
                status=status.HTTP_200_OK,
            )
        return HttpResponseRedirect(shortened_url.original_url)
    except Http404:
        return JsonResponse(
            {"error": "Shortened URL not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# GET request to view the analytics of the shortened URL
@csrf_exempt
@swagger_auto_schema(
    method="GET",
    responses={200: "Analytics Data", 404: "Not Found", 500: "Internal Server Error"},
)
@api_view(["GET"])
def analytics(request, short_url):
    try:
        shortened_url = get_object_or_404(ShortenedURL, short_url=short_url)
        # Gather analytics data
        access_logs = AccessLog.objects.filter(short_url=shortened_url)
        logs = [
            {"ip_address": log.ip_address, "accessed_at": log.accessed_at}
            for log in access_logs
        ]

        return JsonResponse(
            {
                "original_url": shortened_url.original_url,
                "short_url": shortened_url.short_url,
                "access_count": shortened_url.visits,
                "logs": logs,
            },
            status=status.HTTP_200_OK,
        )
    except Http404:
        return JsonResponse(
            {"error": "Shortened URL not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
