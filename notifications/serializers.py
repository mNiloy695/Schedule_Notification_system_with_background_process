from .models import Notification
from rest_framework import serializers
from django.utils import timezone


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','title','message','schedule_time','status','retry_count','max_retry','created_at','updated_at']
        read_only_fields = ["created_by", "status","updated_at","created_at","retry_count","max_retry"]

    def validate(self, attrs):
        if attrs["schedule_time"] < timezone.now():
            raise serializers.ValidationError({"error":"Schedule time must be in future"})
        return attrs
