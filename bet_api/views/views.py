#  IsAuthenticated
import rest_framework as rf
from bet_api.services import UserActivityService
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.conf import settings
import os

class UserRegisterView(rf.views.APIView):
    permission_classes = [rf.permissions.AllowAny]
    def post(self, request):
        return UserActivityService.register_user(request)
         
class LoginView(rf.views.APIView):
    permission_classes = [rf.permissions.AllowAny]
    def post(self, request):
        return UserActivityService.login_user(request)
    
class UserProfileView(rf.views.APIView):
    permission_classes = [rf.permissions.IsAuthenticated]     
    def get(self, request):
        return UserActivityService.get_user_profile(request.user)
    
    def patch(self, request):
        return UserActivityService.update_user_profile(request.user, request.data)
    
    
class Usersearch(rf.views.APIView):
    permission_classes = [rf.permissions.IsAuthenticated]  
    def get(self, request):
        query = request.GET.get('q', '').strip()
        return UserActivityService.userSearch(request,query)


class GoogleAuthView(rf.views.APIView):
    permission_classes = [rf.permissions.AllowAny]
    def post(self, request):
        return UserActivityService.google_auth(request)
