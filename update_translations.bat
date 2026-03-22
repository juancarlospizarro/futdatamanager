@echo off
REM Script para actualizar archivos de traducción en Windows CMD
REM Uso: update_translations.bat

echo.
echo Actualizando archivos de traducción...
echo.

echo Generando mensajes para español...
python manage.py makemessages -l es

echo.
echo Generando mensajes para inglés...
python manage.py makemessages -l en

echo.
echo Compilando mensajes...
python manage.py compilemessages

echo.
echo Traducción actualizada correctamente
echo.
pause
