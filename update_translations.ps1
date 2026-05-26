# Script para actualizar archivos de traducción
# Uso: .\update_translations.ps1

Write-Host "Actualizando archivos de traducción..." -ForegroundColor Green

# Generar mensajes para español
Write-Host "Generando mensajes para español..." -ForegroundColor Yellow
python manage.py makemessages -l es

# Generar mensajes para inglés
Write-Host "Generando mensajes para inglés..." -ForegroundColor Yellow
python manage.py makemessages -l en

# Compilar mensajes
Write-Host "Compilando mensajes..." -ForegroundColor Yellow
python manage.py compilemessages

Write-Host "¡Traducción actualizada correctamente!" -ForegroundColor Green
