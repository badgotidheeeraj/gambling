from django.db import models
from django.contrib.auth.models import User

# This file defines the UserProfile model which extends the default User model
class UserProfile(models.Model):
    userAccount = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    balance= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)    
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    
    def __str__(self):
        return f"{self.userAccount.username}'s Profile"