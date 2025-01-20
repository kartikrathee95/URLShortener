# URL Shortener

A simple URL shortening web application built using Django and Django REST Framework. This app allows users to shorten URLs, visit the shortened URL, and view analytics on the usage of each shortened link. Additionally, users can set a password for a shortened URL and view access logs.

## Features

* Shorten URLs: Convert long URLs into short URLs.
* Password protection: Set a password on shortened URLs for additional security.
* Visit Shortened URLs: Redirect to the original URL when visiting a shortened URL.
* Analytics: Track the number of times a shortened URL has been accessed and view access logs.
* Error Handling: Handle invalid URLs and missing shortened URLs with appropriate error messages.

## Requirements

* Python 3.x
* Django
* Django REST Framework
* SQLite (default database)

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/url-shortener.git

2. Navigate to the project directory:

cd url-shortener

3. Create and activate a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install the required dependencies:

pip install -r requirements.txt

5. Apply the migrations to set up the database:

python manage.py migrate

6. (Optional) Create a superuser to access the admin panel:

python manage.py createsuperuser

7. Run the development server:

python manage.py runserver

You can now access the application by visiting http://127.0.0.1:8000 in your web browser.

## Endpoints

### 1. Home Page

* **URL**: `/`
* **Method**: `GET`
* **Description**: Displays the home page of the application.

### 2. Shorten URL

* **URL**: `/shorten`
* **Method**: `POST`
* **Request Body (JSON)**:

    { "original_url": "https://example.com" }

* **Response (Success)**:

    { "short_url": "abcd1234" }

* **Response (Failure)**:

    { "error": "Invalid URL" }

* **Description**: Takes an original URL and returns a shortened URL.

### 3. Visit Shortened URL

* **URL**: `/shorten/<short_url>/`
* **Method**: `GET`
* **Query Parameter**:
    * `password`: The password for the shortened URL (optional).
* **Response**: Redirects to the original URL if the password (if set) is correct, or returns an error if the password is incorrect or the URL is not found.

### 4. Analytics

* **URL**: `/analytics/<short_url>/`
* **Method**: `GET`
* **Response**:

{
  "original_url": "https://example.com",
  "short_url": "abcd1234",
  "access_count": 10,
  "logs": [
    { "ip_address": "192.168.0.1", "user_agent": "Mozilla/5.0" }
  ]
}

* **Description**: Returns the analytics for a shortened URL, including access count and logs.

## Example Usage

1. **Shorten a URL**: Send a `POST` request to `/shorten` with the original URL. Example:

     curl -X POST http://127.0.0.1:8000/shorten -H "Content-Type: application/json" -d '{"original_url": "https://example.com"}'

Response:

     { "short_url": "abcd1234" }

2. **Visit a Shortened URL**: Send a `GET` request to `/shorten/<short_url>/`. Example:

     curl http://127.0.0.1:8000/shorten/abcd1234/

3. **View Analytics for a Shortened URL**: Send a `GET` request to `/analytics/<short_url>/`. Example:

     curl http://127.0.0.1:8000/analytics/abcd1234/ 
