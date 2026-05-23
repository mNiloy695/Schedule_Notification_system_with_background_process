# 🔔 Background Job Based Notification System

A production-grade backend API built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, **Redis**, and **Celery** to schedule and deliver notifications asynchronously with automated retries.

---

## 🌟 Features Implemented

1. **User Authentication**: Secure register, login, and logout endpoints powered by JWT (`simplejwt`) with token blacklisting.
2. **Notification Scheduling**: Post notifications with future schedule times which are processed in the background at the exact time specified.
3. **Queue & Background processing**: Celery worker integration using Redis as a message broker.
4. **Resilient Retry Mechanism**: 
   - Exponential backoff retry logic.
   - Safe retry termination: Limits to 3 attempts (configurable via `max_retry`) before marking notifications as permanently `failed` to prevent infinite loops.
5. **On-Demand Retries**: A dedicated endpoint `/api/notifications/<pk>/retry/` to reset and re-run failed notification jobs.
6. **Robust Validation**: Rejects requests if `schedule_time` is in the past.
7. **Dockerized Environment**: Built-in Docker and Docker Compose configurations running Python, PostgreSQL, Redis, and Celery.

---

## 📂 Project Architecture

```
Notification_System/
├── core/
│   ├── celery.py         # Celery configuration & instantiation
│   ├── settings.py       # Decouple-based settings for Postgres, Redis, and DRF
│   └── urls.py           # Project root URL routing
├── accounts/             # Registration, login (JWT), and logout views
├── notifications/
│   ├── models.py         # Notification model (title, message, status, retry_count)
│   ├── serializers.py    # Serializers with future schedule_time validation
│   ├── tasks.py          # Asynchronous delivery task with backoff retry logic
│   ├── views.py          # Views for list, details, create, and retry notifications
│   └── urls.py           # App routing
├── Dockerfile            # Container build specification
├── docker-compose.yml    # Service orchestration for Postgres, Redis, App, and Celery
└── requirements.txt      # Python dependencies
```

---

## ⚡ Quick Start with Docker Compose

Run the entire system (Django, Postgres, Redis, and Celery) with a single command:

### 1. Build and Start Services
```bash
docker-compose up --build
```
This starts:
- **`notification_db`**: PostgreSQL (port 5432)
- **`notification_redis`**: Redis (port 6379)
- **`notification_web`**: Django API server (port 8000)
- **`notification_celery`**: Background task worker

### 2. Check Service Logs
```bash
docker-compose logs -f
```

---

## 🔒 API Reference

All requests and responses use the `application/json` content type.

### Auth Endpoints

#### 1. Register User
* **URL:** `/api/accounts/auth/register/`
* **Method:** `POST`
* **Access:** Public

```json
// Request Body
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "SecurePassword123"
}
```

#### 2. Login User
* **URL:** `/api/accounts/auth/login/`
* **Method:** `POST`
* **Access:** Public

```json
// Response Body (200 OK)
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "refresh": "refresh_token...",
  "access": "access_token..."
}
```

#### 3. Logout User
* **URL:** `/api/accounts/auth/logout/`
* **Method:** `POST`
* **Access:** Authenticated (Requires Bearer token in headers)

```http
Authorization: Bearer <your_access_token>
```
```json
// Request Body
{
  "refresh": "<refresh_token_to_blacklist>"
}
```

---

### Notification Endpoints

Include `Authorization: Bearer <your_access_token>` in headers for all endpoints below.

#### 4. Schedule Notification
* **URL:** `/api/notifications/`
* **Method:** `POST`

```json
// Request Body
{
  "title": "Welcome Email",
  "message": "Welcome to our platform!",
  "schedule_time": "2026-05-24T18:00:00Z"
}
```

```json
// Response Body (201 Created)
{
  "notification": {
    "id": 1,
    "title": "Welcome Email",
    "message": "Welcome to our platform!",
    "schedule_time": "2026-05-24T18:00:00Z",
    "status": "pending",
    "retry_count": 0,
    "max_retry": 3,
    "created_at": "2026-05-23T15:30:00Z",
    "updated_at": "2026-05-23T15:30:00Z"
  }
}
```
* **Validation (400 Bad Request)**: Rejects if `schedule_time` is in the past:
```json
{
  "error": "Schedule time must be in future"
}
```

#### 5. View Notification History
* **URL:** `/api/notifications/`
* **Method:** `GET`
Returns list of all notifications created by the user, ordered by creation date (newest first).

#### 6. View Notification Detail
* **URL:** `/api/notifications/<id>/`
* **Method:** `GET`

#### 7. Retry Failed Notification
* **URL:** `/api/notifications/<id>/retry/`
* **Method:** `POST`
Resets the status of a permanently failed notification (`"status": "failed"`) back to `pending`, resets the retry counter to `0`, and immediately re-enqueues it in Celery.

---

##  Queue & Job Architecture Design

1. **Future Scheduling (`eta`)**: When a notification is created, it is scheduled in Celery with an `eta` value set to `schedule_time`. The message resides in the Redis broker until the scheduled time, when the worker retrieves and runs it.
2. **Handling Job Failures & Retries**: 
   - A mock transmission is executed inside `send_notification_task`.
   - If transmission fails (e.g. timeout, SMTP error), the exception is caught, `retry_count` is incremented.
   - If `retry_count` < `max_retry` (3), Celery re-queues the task with a backoff delay (`15 * retry_count` seconds).
   - If `retry_count` reaches 3, the notification status is set to `failed`, preventing infinite retries.
