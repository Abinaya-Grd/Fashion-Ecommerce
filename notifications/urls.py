from django.urls import path

from .views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    DeleteNotificationView,
    UnreadNotificationCountView,
)

urlpatterns = [
    path('', NotificationListView.as_view()),
    path('/unread-count', UnreadNotificationCountView.as_view()),
    path('/<int:pk>/read', MarkNotificationReadView.as_view()),
    path('/read-all', MarkAllNotificationsReadView.as_view()),
    path('/<int:pk>', DeleteNotificationView.as_view()),
]