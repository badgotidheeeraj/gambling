from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bet_api.services.notification_service import NotificationService

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return NotificationService.get_user_notifications(request.user)

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, notification_id):
        return NotificationService.mark_as_read(notification_id, request.user)
