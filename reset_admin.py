import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Reset admin password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin12345')
    admin.save()
    print("Admin password has been reset to: admin12345")
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
    print("New admin user created with password: admin12345")
