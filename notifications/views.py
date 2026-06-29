from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message
    }, status=status_code)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-notificationid")

        serializer = NotificationSerializer(notifications, many=True)

        return success_response(
            "Notifications fetched successfully",
            serializer.data
        )


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            notification = Notification.objects.get(
                notificationid=pk,
                user=request.user
            )
        except Notification.DoesNotExist:
            return error_response("Notification not found", status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)

        return success_response(
            "Notification marked as read",
            serializer.data
        )


class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return success_response("All notifications marked as read")


class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(
                notificationid=pk,
                user=request.user
            )
        except Notification.DoesNotExist:
            return error_response("Notification not found", status.HTTP_404_NOT_FOUND)

        notification.delete()

        return success_response("Notification deleted successfully")


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return success_response(
            "Unread notification count fetched successfully",
            {"unread_count": count}
        )