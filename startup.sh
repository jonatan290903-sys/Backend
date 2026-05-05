#!/bin/sh

# Salir si algún comando falla
set -e

echo "--- Iniciando proceso de arranque ---"

# 1. Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# 2. Crear superusuario si no existe (Optimizado en un solo comando de shell)
echo "Verificando superusuario..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

# 3. Reparar secuencias solo si es necesario (vía variable de entorno o primera vez)
if [ "$FIX_SEQUENCES" = "true" ]; then
    echo "Sincronizando secuencias de base de datos..."
    python fix_sequences.py
else
    echo "Saltando sincronización de secuencias (FIX_SEQUENCES no es true)"
fi

# 4. Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 90 \
    --log-level info
