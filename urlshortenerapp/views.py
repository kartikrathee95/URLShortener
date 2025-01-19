import json

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .models import AccessLog, ShortenedURL


def home(request):
    return render(request, "urlshortenerapp/home.html")


# POST request to create a new shortened URL
@csrf_exempt
def shorten_url(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)  # Parse the raw JSON body
            original_url = data.get("url")
            expiration_at = data.get("expiration_timestamp")
            # Validate the incoming URL
            ShortenedURL.validate_url(original_url)
            # If the expiration timestamp is provided, create a new shortened URL with the expiration timestamp
            shortened_url = ShortenedURL.objects.create(
                original_url=original_url, expiration_at=expiration_at
            )
            return JsonResponse(
                {"short_url": f"{shortened_url.short_url}"},
                status=201,
            )
        else:
            return JsonResponse({"error": "Invalid request method"}, status=400)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=422)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Function to redirect to the original URL)
def redirect_to_original(shortened_url):
    return redirect(shortened_url.original_url)


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
def visit_shortened_url(request, short_url):
    try:
        short_url = settings.BASE_URL + "/" + short_url
        shortened_url = get_object_or_404(ShortenedURL, short_url=short_url)
        if shortened_url.is_expired():
            return JsonResponse(
                {"error": "This URL has expired, Please create a new shortened URL"},
                status=404,
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
        return HttpResponseRedirect(shortened_url.original_url)
    except Http404:
        return render(request, "404.html", {"message": "Shortened URL not found"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# GET request to view the analytics of the shortened URL
@csrf_exempt
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
            status=200,
        )
    except Http404:
        return render(request, "404.html", {"message": "Shortened URL not found"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
