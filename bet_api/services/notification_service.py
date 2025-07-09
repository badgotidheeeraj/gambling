from bet_api.models.notification import Notification
from bet_api.serializers.notification_serializer import NotificationSerializer
from rest_framework.response import Response
from rest_framework import status

class NotificationService:
    @staticmethod
    def create_notification(user, message):
        notification = Notification.objects.create(user=user, message=message)
        return notification

    @staticmethod
    def get_user_notifications(user):
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @staticmethod
    def mark_as_read(notification_id, user):
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return Response({'success': True})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
