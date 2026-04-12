from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [
    path("crear_equipo/", views.crear_equipo, name='crear_equipo'),
    path('listado_equipos/', views.listado_equipos, name='listado_equipos'),
    path('api/agregar-jugador/<int:equipo_id>/<int:jugador_id>/', views.agregar_jugador_equipo, name='agregar_jugador_equipo'),
    path('api/editar-jugador/<int:jugador_id>/', views.editar_jugador, name='editar_jugador'),
    path('api/eliminar-jugador/<int:equipo_id>/<int:jugador_id>/', views.eliminar_jugador_equipo, name='eliminar_jugador_equipo'),
    path('miperfil/abandonar-equipo/', views.abandonar_equipo, name="abandonar_equipo"),
    path('<slug:slug>/pizarra/', views.pizarra_tactica, name='pizarra_tactica'),
    path('<slug:slug>/', views.informacion_equipo, name='informacion_equipo'),
]