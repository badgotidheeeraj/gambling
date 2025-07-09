from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.models import User

from bet_api.serializers import UserRegisterSerializer, LoginSerializer,UserProfileSerializer,UserProfileSerializerSearch
from bet_api.models import UserProfile  
from bet_api.services.notification_service import NotificationService




class UserActivityService:
    @staticmethod
    def register_user(request):
        serializer = UserRegisterSerializer(data=request.data)
    
        if serializer.is_valid():
            user = serializer.save()
            # Send welcome notification
            NotificationService.create_notification(user, "Welcome to the platform!")
            return Response(
                {"success": True, "message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    @staticmethod
    def login_user(request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "username": user.username
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_user_profile(user, data):
        try:
            user_profile = UserProfile.objects.get(userAccount=user)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(user_profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def get_user_profile(user):     
        try:
            user_profile = UserProfile.objects.get(userAccount=user)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    def userSearch(request, text):
        matches = UserProfile.objects.filter(
            Q(userAccount__username__icontains=text) |
            Q(userAccount__first_name__icontains=text) |
            Q(userAccount__last_name__icontains=text)
        )
        print(matches)
        serializer = UserProfileSerializerSearch(matches, many=True, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
   

    @staticmethod
    def google_auth(request):
        try:
            access_token = request.data.get('access_token')
            if not access_token:
                return Response({'error': 'Access token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Use access token to get user info from Google API
            userinfo_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if userinfo_response.status_code != 200:
                return Response({'error': 'Failed to fetch user info from Google.'}, status=status.HTTP_400_BAD_REQUEST)

            userinfo = userinfo_response.json()
            email = userinfo.get('email')
            name = userinfo.get('name')
            picture = userinfo.get('picture')

            if not email:
                return Response({'error': 'Email not found in Google account.'}, status=status.HTTP_400_BAD_REQUEST)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split("@")[0], 'first_name': name}
            )
            UserProfile.objects.get_or_create(
                userAccount=user,
            )

            refresh = RefreshToken.for_user(user)
            print(f"User: {refresh}, Created: {refresh}")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'name': user.first_name,
                    'picture': picture,
                }
            })

        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







