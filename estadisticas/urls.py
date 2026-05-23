from django.urls import path
from . import views

app_name = 'estadisticas'

urlpatterns = [
    path('analisis/', views.analisis, name='analisis'),
    
    # AJAX endpoints para estadísticas
    path('ajax/obtener-jugadores/', views.obtener_jugadores_equipo, name='obtener_jugadores'),
    path('ajax/guardar-estadistica/', views.guardar_estadistica, name='guardar_estadistica'),
    path('ajax/obtener-estadisticas/<int:partido_id>/', views.obtener_estadisticas_partido, name='obtener_estadisticas'),
    path('ajax/eliminar-estadistica/<int:estadistica_id>/', views.eliminar_estadistica, name='eliminar_estadistica'),
    path('ajax/importar-csv/', views.importar_estadisticas_csv, name='importar_csv'),
    path('ajax/obtener-analisis-ofensivo/', views.obtener_analisis_ofensivo_ajax, name='obtener_analisis_ofensivo'),
    path('ajax/obtener-analisis-defensivo/', views.obtener_analisis_defensivo_ajax, name='obtener_analisis_defensivo'),
    path('ajax/obtener-partidos-finalizados/', views.obtener_partidos_finalizados, name='obtener_partidos_finalizados'),
    path('ajax/obtener-estadisticas-jugador/', views.obtener_estadisticas_jugador, name='obtener_estadisticas_jugador'),
    path('ajax/obtener-estadisticas-jugador-por-90/', views.obtener_estadisticas_jugador_por_90, name='obtener_estadisticas_jugador_por_90'),
    path('ajax/obtener-estadisticas-jugador-partido/', views.obtener_estadisticas_jugador_partido, name='obtener_estadisticas_jugador_partido'),
    path('ajax/obtener-once-filtrado/', views.obtener_once_filtrado, name='obtener_once_filtrado'),
    path('debug/jugadores-forma/', views.debug_jugadores_forma, name='debug_jugadores_forma'),
]
