"""
URL configuration for football_stats_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from equipos import views as equipos_views
from control_jugadores import views as control_jugadores_views

# URLs AJAX (sin i18n)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('teams/ajax/agregar_lesion/', equipos_views.agregar_lesion, name='agregar_lesion'),
    path('teams/ajax/agregar_sancion/', equipos_views.agregar_sancion, name='agregar_sancion'),
    # Control de jugadores AJAX endpoints
    path('control-jugadores/ajax/obtener-lesiones/<int:jugador_id>/', control_jugadores_views.obtener_lesiones_jugador, name='obtener_lesiones_jugador'),
    path('control-jugadores/ajax/obtener-sanciones/<int:jugador_id>/', control_jugadores_views.obtener_sanciones_jugador, name='obtener_sanciones_jugador'),
    path('control-jugadores/ajax/eliminar-lesion/<int:lesion_id>/', control_jugadores_views.eliminar_lesion, name='eliminar_lesion'),
    path('control-jugadores/ajax/eliminar-sancion/<int:sancion_id>/', control_jugadores_views.eliminar_sancion, name='eliminar_sancion'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.landing, name="landing"),
    path('auth/', include('usuarios.urls')),
    path('teams/', include('equipos.urls')),
    path('events/', include('eventos.urls')),
    path('control-jugadores/', include('control_jugadores.urls')),
    path("test-400/", views.error_400_test),
    path("test-403/", views.error_403_test),
    path("test-500/", views.error_500_test),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Vistas personalizadas de error
handler404 = 'football_stats_app.views.error_404'
handler500 = 'football_stats_app.views.error_500'
handler403 = 'football_stats_app.views.error_403'
handler400 = 'football_stats_app.views.error_400'
