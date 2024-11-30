import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Remove existing superuser if it exists
User.objects.filter(username='admin').delete()

# Create a new superuser
User.objects.create_superuser(
    username='admin', 
    email='admin@example.com', 
    password='admin12345'
)
print("Superuser created successfully with username 'admin' and password 'admin12345'")
