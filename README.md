# 🔔 Notification System API

A lightweight authentication backend built with **Django**, **Django REST Framework (DRF)**, and **SimpleJWT** (JSON Web Tokens). This service handles secure user signup, authentication, and token management (refresh token rotation & blacklisting) for a schedule notification system.

---

## 🚀 Getting Started

### 1. Installation

Clone the repository and set up a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required dependencies
pip install django djangorestframework djangorestframework-simplejwt
```

### 2. Database Migrations

Apply migrations to initialize the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Run the Server

Start the local development server:

```bash
python manage.py runserver 8089
```

---

## 🔒 API Endpoints Reference

All requests and responses use the `application/json` content type.

### 1. User Registration

Creates a new user account.

* **URL:** `/api/accounts/auth/register/`
* **Method:** `POST`
* **Access:** Public

#### Request Body
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "SecurePassword123"
}
```

#### Response (201 Created)
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

### 2. User Login

Authenticates user credentials and returns user details along with JWT Access and Refresh tokens.

* **URL:** `/api/accounts/auth/login/`
* **Method:** `POST`
* **Access:** Public

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

#### Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 3. User Logout

Logs the user out by blacklisting the provided refresh token.

* **URL:** `/api/accounts/auth/logout/`
* **Method:** `POST`
* **Access:** Authenticated (Requires Bearer Token)

#### Headers
```http
Authorization: Bearer <your_access_token>
```

#### Request Body
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Responses

##### Success (205 Reset Content)
```json
{
  "detail": "Successfully logged out"
}
```

##### Error (400 Bad Request)
Returned if the request fails (e.g. invalid or missing refresh token).
```json
{
  "detail": "Something went wrong"
}
```

