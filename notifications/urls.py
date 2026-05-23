from .views import NotificationView
from django.urls import path


urlpatterns = [
    path("", NotificationView.as_view(), name="notification"),
    path("<int:pk>/", NotificationView.as_view(), name="notification"),
   
]