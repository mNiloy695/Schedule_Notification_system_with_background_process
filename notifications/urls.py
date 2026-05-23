from django.urls import path
from .views import NotificationListCreateView, NotificationDetailView, RetryNotificationView

urlpatterns = [
    path("", NotificationListCreateView.as_view(), name="notification-list-create"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:pk>/retry/", RetryNotificationView.as_view(), name="notification-retry"),
]