from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # AJAX Entrenamientos
    path('ajax/crear_entrenamiento/', views.crear_entrenamiento_ajax, name='crear_entrenamiento_ajax'),
    path('ajax/obtener_entrenamientos/', views.obtener_entrenamientos_ajax, name='obtener_entrenamientos_ajax'),
    path('ajax/listar_entrenamientos/', views.listar_entrenamientos_ajax, name='listar_entrenamientos_ajax'),
    path('ajax/eliminar_entrenamiento/<int:entrenamiento_id>/', views.eliminar_entrenamiento_ajax, name='eliminar_entrenamiento_ajax'),
    
    # AJAX Partidos
    path('ajax/crear_partido/', views.crear_partido_ajax, name='crear_partido_ajax'),
    path('ajax/obtener_partidos/', views.obtener_partidos_ajax, name='obtener_partidos_ajax'),
    path('ajax/listar_partidos/', views.listar_partidos_ajax, name='listar_partidos_ajax'),
    path('ajax/eliminar_partido/<int:partido_id>/', views.eliminar_partido_ajax, name='eliminar_partido_ajax'),
    path('ajax/finalizar_partido/<int:partido_id>/', views.finalizar_partido_ajax, name='finalizar_partido_ajax'),
    path('ajax/obtener_partidos_finalizados/', views.obtener_partidos_finalizados_ajax, name='obtener_partidos_finalizados_ajax'),
    path('ajax/obtener_equipos/', views.obtener_equipos_ajax, name='obtener_equipos_ajax'),
    
    # Partidos
    path('<slug:slug>/crear_partido/', views.crear_partido, name='crear_partido'),
    path('partido/<int:partido_id>/editar/', views.editar_partido, name='editar_partido'),
    path('partido/<int:partido_id>/eliminar/', views.eliminar_partido, name='eliminar_partido'),
    path('<slug:slug>/partidos/', views.listar_partidos, name='listar_partidos'),
    
    # Entrenamientos
    path('<slug:slug>/crear_entrenamiento/', views.crear_entrenamiento, name='crear_entrenamiento'),
    path('entrenamiento/<int:entrenamiento_id>/editar/', views.editar_entrenamiento, name='editar_entrenamiento'),
    path('entrenamiento/<int:entrenamiento_id>/eliminar/', views.eliminar_entrenamiento, name='eliminar_entrenamiento'),
    path('<slug:slug>/entrenamientos/', views.listar_entrenamientos, name='listar_entrenamientos'),
]
