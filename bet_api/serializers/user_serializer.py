# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from bet_api.models import UserProfile 
from django.contrib.auth.password_validation import validate_password



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields ="__all__"  # Adjust fields as necessary


class UserProfileSerializerSearch(serializers.ModelSerializer):
    id = serializers.IntegerField(source='userAccount.id')
    username = serializers.CharField(source='userAccount.username')
    email = serializers.EmailField(source='userAccount.email')
    first_name = serializers.CharField(source='userAccount.first_name')
    last_name = serializers.CharField(source='userAccount.last_name')
    profile_picture = serializers.ImageField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_picture'
        ]


