from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NotificationSerializer
from django.utils import timezone
from .models import Notification
# Create your views here.

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save(created_by=request.user)
            return Response({"notification": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request,pk=None):
        if pk:
            try:
                notification = Notification.objects.get(id=pk, created_by=request.user)
            except Notification.DoesNotExist:
                return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            notifications = Notification.objects.filter(created_by=request.user).order_by('-created_at')
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)




        
