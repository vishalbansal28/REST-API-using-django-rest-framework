import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Remove existing superuser
try:
    user = User.objects.get(username='admin')
    user.delete()
    print("Superuser 'admin' has been removed successfully!")
except User.DoesNotExist:
    print("No superuser with username 'admin' found.")
