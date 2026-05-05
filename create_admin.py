import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'adminpassword123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='directivo' # O el rol que prefieras
    )
    print(f"Superuser '{username}' creado exitosamente con contraseña '{password}'")
else:
    print(f"El usuario '{username}' ya existe.")
