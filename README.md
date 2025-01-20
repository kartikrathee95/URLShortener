# URL Shortener

A simple URL shortening web application built using **Django** and **Django REST Framework**. This app allows users to:

- Shorten URLs
- Visit the shortened URL
- View analytics on the usage of each shortened link
- Set a password for a shortened URL
- View access logs

## Features

- **Shorten URLs**: Convert long URLs into short URLs.
- **Password Protection**: Set a password on shortened URLs for additional security.
- **Visit Shortened URLs**: Redirect to the original URL when visiting a shortened URL.
- **Analytics**: Track the number of times a shortened URL has been accessed.
- **Error Handling**: Handle invalid URLs and missing shortened URLs with appropriate error messages.

---

## Deployed API

The deployed version of the URL Shortener app is available at [https://short-ly-cfl1.onrender.com/swagger/](https://short-ly-cfl1.onrender.com/swagger/). You can access the following API actions:

1. **Shorten URL**: Convert long URLs into short URLs.
2. **Password Protection**: Set a password on shortened URLs for additional security.
3. **Visit Shortened URLs**: Redirect to the original URL when visiting a shortened URL.
4. **Analytics**: Track the number of times a shortened URL has been accessed.
5. **Error Handling**: Handle invalid URLs and missing shortened URLs with appropriate error messages.

You can test the following actions using **`curl`** or **Postman**.

---

## API Actions: Using Deployed API

### 1. **Shorten a URL**

**POST**: `/shorten/`

To shorten a URL, send a POST request with the `original_url` parameter in the request body.

**Using `curl`**:

```bash
curl -X POST "https://short-ly-cfl1.onrender.com/shorten/" -H "Content-Type: application/json" -d '{"original_url": "https://github.com/kartikrathee95/URLShortener/blob/main/README.md"}'
```
## Response

- **original_url**: (https://github.com/kartikrathee95/URLShortener/blob/main/README.md)
- **short_url**: (https://short-ly-cfl1.onrender.com/abc123)
- **expiration_hours**: 30 hours from creation
- **expiration_at**: 2025-01-21T16:20:04.562Z
- **visits**: 0
- **created_at**: 2025-01-20T16:20.04.562Z


### 2. **Visit a Shortened URL**

**GET**: `/{short_url}/`

To visit a shortened URL, send a GET request to the shortened URL. Optionally, include a `password` query parameter.

**Using `curl`**:

```bash
curl "https://short-ly-cfl1.onrender.com/abc123/?password=yourpassword"
```
## Response
- **original_url**: (https://github.com/kartikrathee95/URLShortener/blob/main/README.md)
- **redirect_url**: (https://short-ly-cfl1.onrender.com/abc123)
- **Redirects to original URL**

### 3. **Set a Password for a Shortened URL**

**POST**: `/shorten/`

You can include the `password` parameter when creating a shortened URL to set a password for accessing the link.

**Using `curl`**:

```bash
curl -X POST "https://short-ly-cfl1.onrender.com/shorten/" -H "Content-Type: application/json" -d '{"original_url": "https://github.com/kartikrathee95/URLShortener/blob/main/README.md", "password": "string"}'
```
## Response

- **original_url**: https://github.com/kartikrathee95/URLShortener/blob/main/README.md
- **short_url**: https://short-ly-cfl1.onrender.com/abc123
- **password**: string
- **expiration_hours**: 30
- **expiration_at**: 2025-01-21T16:20:04.562Z
- **visits**: 0
- **created_at**: 2025-01-20T16:20:04.562Z


### 4. **Track Analytics (View Visits)**

**GET**: `/analytics/{short_url}/`

To track the analytics of a shortened URL, send a GET request to view the visit count and other details.

**Using `curl`**:

```bash
curl "https://short-ly-cfl1.onrender.com/analytics/abc123/"
```
## Response

- **Short URL**: [https://short-ly-cfl1.onrender.com/1004cc54](https://short-ly-cfl1.onrender.com/1004cc54)
- **Original URL**: [https://github.com/kartikrathee95/URLShortener/edit/main/README.md](https://github.com/kartikrathee95/URLShortener/edit/main/README.md)
- **Number of Visits**: 10
### Logs
- **IP Address**: 127.0.0.1  
  **Accessed At**: 2025-01-20T11:28:07.644Z



## Installation Guide

1. Clone the repository:
   ```bash
   git clone https://github.com/kartikrathee95/URLShortener.git
   ```

2. Navigate to the project directory:
   ```bash
   cd URLShortener
   ```

4. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Apply the migrations to set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. (Optional) Create a superuser to access the admin panel:
    ```bash
    python manage.py createsuperuser
    ```
   
8. Run Unit Tests
   ```bash
    python manage.py test
   ```
   
10. Run the development server:
    ```bash
    python manage.py runserver
    ```


You can now access the application by visiting ```http://127.0.0.1:8000``` in your web browser.

## API Endpoints

### 1. Swagger UI
- **URL**: `/swagger`
- **Method**: `GET`
- **Description**: Make API requests using Swagger UI

### 2. Shorten URL
- **URL**: `/shorten`
- **Method**: `POST`
- **Request Body (JSON)**:
    ```json
    { "original_url": "https://example.com" }
    ```
- **Response (Success)**:
    ```json
    { "short_url": "http://localhost:8000/abcd1234" }  (haslib implementation)
    ```
- **Response (Failure)**:
    ```json
    { "error": "Invalid URL" }
    ```
- **Description**: Takes an original URL and returns a shortened URL.

### 3. Visit Shortened URL
- **URL**: `/<short_url>/`
- **Method**: `GET`
- **Query Parameter**:
    - `password`: The password for the shortened URL (optional).
- **Response**: Redirects to the original URL if the password (if set) is correct, or returns an error if the password is incorrect or the URL is not found.

### 4. Analytics
- **URL**: `/analytics/<short_url>/`
- **Method**: `GET`
- **Response**:
    ```json
    {
      "original_url": "https://example.com",
      "short_url": "abcd1234",
      "access_count": 10,
      "logs": [
        { "ip_address": "192.168.0.1", "user_agent": "Mozilla/5.0" }
      ]
    }
    ```
- **Description**: Returns the analytics for a shortened URL, including access count and logs.

## Example Usage

1. **Shorten a URL**: Send a `POST` request to `/shorten` with the original URL. Example:
    ```bash
    curl -X POST http://127.0.0.1:8000/shorten -H "Content-Type: application/json" -d '{"original_url": "https://example.com"}'
    ```
    **Response**:
    ```json
    { "short_url": "http://localhost:8000/abcd1234" }
    ```

2. **Visit a Shortened URL**: Send a `GET` request to `/<short_url>/`. Example:
    ```bash
    curl http://127.0.0.1:8000/abcd1234/
    ```

3. **View Analytics for a Shortened URL**: Send a `GET` request to `/analytics/<short_url>/`. Example:
    ```bash
    curl http://127.0.0.1:8000/analytics/http://localhost:8000/abcd1234/
    ```
