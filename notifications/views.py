from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NotificationSerializer
from .models import Notification
from .tasks import send_notification_task


class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save(created_by=request.user)
            send_notification_task.apply_async(
                args=[notification.id],
                eta=notification.schedule_time
            )
            response_serializer = NotificationSerializer(notification)
            return Response({"notification": response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        notifications = Notification.objects.filter(created_by=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, created_by=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetryNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, created_by=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        if notification.status != "failed":
            return Response(
                {"detail": f"Only failed notifications can be retried. Current status is '{notification.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification.status = "pending"
        notification.retry_count = 0
        notification.save()

        send_notification_task.delay(notification.id)

        serializer = NotificationSerializer(notification)
        return Response(
            {
                "detail": "Notification retry has been scheduled successfully.",
                "notification": serializer.data
            },
            status=status.HTTP_200_OK
        )
