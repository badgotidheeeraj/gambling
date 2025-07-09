import os
import django
from django.core.management import execute_from_command_line
from django.conf import settings
from django.contrib.auth import get_user_model 
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gambling.settings') 
django.setup()
User = get_user_model() 
 
def create_admin_user():
    admin_username = "admin"
    admin_email = "badgotidhee@gmail.com"
    admin_password = "admin"
 
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
        print(" Admin user created.")
    else:
        print("Admin user already exists, skipping...")




  
def main():
    print("🚀 Running setup script...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    create_admin_user()
    print("🎉 Setup complete!")
    
if __name__ == "__main__":
    main()
 
 