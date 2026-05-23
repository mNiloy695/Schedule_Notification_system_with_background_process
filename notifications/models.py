from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
User=get_user_model()

NOTIFICATION_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("sent", "Sent"),
    ("failed", "Failed"),
)

class Notification(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    schedule_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=NOTIFICATION_STATUS_CHOICES, default="pending")
    retry_count = models.IntegerField(default=0)
    max_retry = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title