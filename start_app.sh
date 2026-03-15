#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a la base de datos..."
sleep 5

# Crear tablas
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Crear superusuario
echo "Configurando superusuario..."
bash create_superuser.sh

# Arrancar el servidor
echo "Arrancando Gunicorn..."
exec gunicorn football_stats_app.wsgi:application --bind 0.0.0.0:8000