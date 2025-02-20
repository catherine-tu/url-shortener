# URL Shortener Service

A URL shortener service built with Flask in the backend and SQLite as the database.

## Features

- Shorten long URLs to unique short codes (random combination of 6 digits/letters)
- Redirect the generated short URLs to the same domain as the original long URLs
- Track click statistics for each shortened URL through the /stats/<short_code> route
- Input validation for URLs (will raise an error if the URL is invalid format)

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run application:

```bash
python app.py
```

## API Endpoints

### 1. Shorten URL

- **POST** `/shorten`
- Request body: `{"url": "https://example.com/very/long/url"}`
- Returns: Short URL and code

#### Example Post:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url":"https://www.google.com"}' http://127.0.0.1:5000/shorten
```

#### Example Output:

```
{
  "original_url": "https://www.google.com",
  "short_code": "rPESgq",
  "short_url": "http://localhost:5000/rPESgq"
}
```

### 2. Access Short URL's Original Long URL

- **GET** `/<short_code>`
- Redirects to the original URL
- Increments click counter

#### Example Post:

```bash
curl -i http://127.0.0.1:5001/rPESgq
```

#### Example Output:

```
HTTP/1.1 302 FOUND
Server: Werkzeug/3.1.3 Python/3.11.11
Date: Wed, 19 Feb 2025 13:45:22 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 231
Location: https://www.google.com
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
Connection: close

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="https://www.google.com">https://www.google.com</a>. If not, click the link.
```

### 3. Get URL Statistics

- **GET** `/stats/<short_code>`
- Returns: Creation date, click count, and original URL

## Example Usage

```bash
# Shorten a URL
curl -X POST -H "Content-Type: application/json" \
     -d '{"url":"https://example.com/very/long/url"}' \
     http://localhost:5000/shorten

# Get URL statistics -- click count
curl http://localhost:5000/stats/<short_code>
```

#### Example Post:

```bash
curl http://127.0.0.1:5000/stats/rPESgq
```

#### Example Output:

```
{
  "clicks": 0,
  "created_at": "2025-02-19T13:11:15.451619",
  "original_url": "https://www.google.com",
  "short_code": "rPESgq"
}
```

## Further Implementations:

### Here is a list of things I would like to expand on this project:

- Users allowed to add their own, custom shortened URL codes instead of generating a random one.
- Implement user log in and authentication, allowing them to access their own unique shortened URLs.
- Allow users to edit short codes and links
- Let users use their own domain instead of 127.0.0.1:5000
