from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Avg, Count, Q
from equipos.models import Equipo, EquipoJugador, EquipoEntrenador
from usuarios.models import PerfilJugador
from control_jugadores.models import Lesion, Sancion
from eventos.models import Partido
from .models import Estadistica
from .analisis import obtener_jugadores_en_forma, obtener_jugadores_pobre_forma, obtener_once_recomendado
import json


@login_required
def analisis(request):
    """
    Vista que muestra el análisis del equipo del usuario con gráficas.
    Solo disponible para entrenadores con equipo activo.
    """
    from django.contrib import messages
    
    # Verificar que es entrenador
    if request.user.rol != request.user.Rol.ENTRENADOR:
        messages.error(request, "Solo los entrenadores pueden acceder al análisis.")
        return redirect('landing')
    
    # Verificar que tiene perfil de entrenador
    if not hasattr(request.user, 'perfil_entrenador'):
        messages.error(request, "Error: no tienes perfil de entrenador.")
        return redirect('landing')
    
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        
        if not equipos_activos.exists():
            messages.error(request, "No tienes ningún equipo activo.")
            return redirect('landing')
        
        equipo_entrenador = equipos_activos.first()
        equipo = equipo_entrenador.equipo
        
        # Obtener jugadores en forma y pobre forma usando valoraciones
        jugadores_en_forma = obtener_jugadores_en_forma(equipo.id, limite=5)
        jugadores_pobre_forma = obtener_jugadores_pobre_forma(equipo.id, limite=5)
        
        # Obtener once recomendado (mejor jugador de cada posición)
        once_recomendado = obtener_once_recomendado(equipo.id)
        
        # Obtener jugadores del equipo para contar lesiones y sanciones
        jugadores_equipo = equipo.jugadores.filter(es_activo=True).select_related(
            'perfil_jugador__usuario'
        )
        
        # Datos para gráficas
        chart_data = {
            'total_jugadores': jugadores_equipo.count(),
            'jugadores_en_forma': len(jugadores_en_forma),
            'jugadores_pobre_forma': len(jugadores_pobre_forma),
            'lesiones_total': Lesion.objects.filter(
                jugador__equipos__equipo=equipo,
                jugador__equipos__es_activo=True,
                activa=True
            ).count(),
            'sanciones_total': Sancion.objects.filter(
                jugador__equipos__equipo=equipo,
                jugador__equipos__es_activo=True,
                activa=True
            ).count(),
        }
        
        # Obtener partidos finalizados del equipo
        partidos_finalizados = Partido.objects.filter(
            equipo_local=equipo,
            finalizado=True
        ).order_by('-fecha_hora')
        
        context = {
            'equipo': equipo,
            'jugadores_en_forma': jugadores_en_forma,
            'jugadores_pobre_forma': jugadores_pobre_forma,
            'once_recomendado': once_recomendado,
            'chart_data': chart_data,
            'partidos_finalizados': partidos_finalizados,
            'breadcrumbs': [
                {'name': 'Inicio', 'url': '/'},
                {'name': 'Análisis', 'url': None}
            ]
        }
        
        return render(request, 'estadisticas/analisis.html', context)
    
    except Exception as e:
        messages.error(request, f"Error al cargar el análisis: {str(e)}")
        return redirect('landing')


# ============== AJAX ENDPOINTS ==============

@login_required
@require_http_methods(["GET"])
def obtener_jugadores_equipo(request):
    """Obtiene los jugadores activos del equipo del entrenador."""
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        jugadores = EquipoJugador.objects.filter(
            equipo=equipo,
            es_activo=True
        ).select_related('perfil_jugador__usuario').values(
            'perfil_jugador__id',
            'perfil_jugador__usuario__first_name',
            'perfil_jugador__usuario__last_name',
            'perfil_jugador__dorsal',
            'perfil_jugador__posicion'
        )
        
        return JsonResponse({
            'success': True,
            'jugadores': list(jugadores)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def guardar_estadistica(request):
    """Guarda una estadística de un jugador en un partido."""
    try:
        data = json.loads(request.body)
        equipo_id = request.user.perfil_entrenador.equipos.filter(es_activo=True).first().equipo_id
        
        jugador_id = data.get('jugador_id')
        partido_id = data.get('partido_id')
        
        if not jugador_id or not partido_id:
            return JsonResponse({'error': 'Jugador y partido requeridos'}, status=400)
        
        partido = Partido.objects.get(id=partido_id, equipo_local_id=equipo_id)
        jugador = PerfilJugador.objects.get(id=jugador_id)
        
        # Verificar que el jugador pertenece al equipo
        if not EquipoJugador.objects.filter(
            equipo_id=equipo_id,
            perfil_jugador=jugador,
            es_activo=True
        ).exists():
            return JsonResponse({'error': 'El jugador no pertenece al equipo'}, status=400)
        
        # Crear o actualizar estadística
        estadistica, created = Estadistica.objects.update_or_create(
            partido=partido,
            jugador=jugador,
            defaults={
                'titular': data.get('titular', False),
                'minutos_jugados': int(data.get('minutos_jugados', 0)),
                'goles': int(data.get('goles', 0)),
                'asistencias': int(data.get('asistencias', 0)),
                'tiros': int(data.get('tiros', 0)),
                'pases': int(data.get('pases', 0)),
                'fueras_de_juego': int(data.get('fueras_de_juego', 0)),
                'paradas': int(data.get('paradas', 0)),
                'despejes': int(data.get('despejes', 0)),
                'faltas': int(data.get('faltas', 0)),
                'tarjetas_amarillas': int(data.get('tarjetas_amarillas', 0)),
                'tarjeta_roja': data.get('tarjeta_roja', False),
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Estadística guardada correctamente',
            'created': created
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def eliminar_estadistica(request, estadistica_id):
    """Elimina una estadística de la base de datos."""
    try:
        equipo_id = request.user.perfil_entrenador.equipos.filter(es_activo=True).first().equipo_id
        
        estadistica = Estadistica.objects.get(
            id=estadistica_id,
            partido__equipo_local_id=equipo_id
        )
        
        estadistica.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Estadística eliminada correctamente'
        })
    
    except Estadistica.DoesNotExist:
        return JsonResponse({'error': 'Estadística no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_estadisticas_partido(request, partido_id):
    """Obtiene las estadísticas registradas en un partido."""
    try:
        equipo_id = request.user.perfil_entrenador.equipos.filter(es_activo=True).first().equipo_id
        
        estadisticas = Estadistica.objects.filter(
            partido_id=partido_id,
            partido__equipo_local_id=equipo_id
        ).select_related('jugador__usuario').values(
            'id',
            'jugador__usuario__first_name',
            'jugador__usuario__last_name',
            'goles',
            'asistencias',
            'despejes'
        )
        
        return JsonResponse({
            'success': True,
            'estadisticas': list(estadisticas)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def importar_estadisticas_csv(request):
    """Importa estadísticas desde un archivo CSV para un partido específico."""
    import csv
    from io import TextIOWrapper
    from django.db import transaction
    
    try:
        # Validar que tiene archivo y partido
        if 'archivo' not in request.FILES:
            return JsonResponse({'error': 'No se proporciono archivo'}, status=400)
        
        partido_id = request.POST.get('partido_id')
        if not partido_id:
            return JsonResponse({'error': 'Partido no especificado'}, status=400)
        
        # Obtener equipo del entrenador
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Verificar que el partido pertenece al equipo
        partido = Partido.objects.get(id=partido_id, equipo_local=equipo)
        
        # Leer archivo CSV
        archivo = request.FILES['archivo']
        
        # Validar extensión
        if not archivo.name.endswith('.csv'):
            return JsonResponse({'error': 'El archivo debe ser CSV'}, status=400)
        
        # Decodificar CSV
        try:
            archivo_texto = TextIOWrapper(archivo.file, encoding='utf-8')
        except:
            archivo_texto = TextIOWrapper(archivo.file, encoding='latin-1')
        
        reader = csv.DictReader(archivo_texto)
        
        if not reader.fieldnames:
            return JsonResponse({'error': 'El CSV está vacío o no tiene encabezados'}, status=400)
        
        estadisticas_a_crear = []
        errores = []
        advertencias = []
        
        # Procesar cada fila
        for idx, row in enumerate(reader, start=2):  # Empieza en 2 porque 1 es header
            try:
                # Obtener datos básicos
                nombre = (row.get('nombre') or '').strip()
                apellido = (row.get('apellido') or '').strip()
                dorsal = row.get('dorsal', '').strip()
                email = row.get('email', '').strip()
                
                # Intentar identificar el jugador
                jugador = None
                
                # Opción 1: Por dorsal
                if dorsal:
                    try:
                        dorsal_num = int(dorsal)
                        jugador_query = EquipoJugador.objects.filter(
                            equipo=equipo,
                            perfil_jugador__dorsal=dorsal_num,
                            es_activo=True
                        ).select_related('perfil_jugador')
                        
                        if jugador_query.exists():
                            jugador = jugador_query.first().perfil_jugador
                    except (ValueError, EquipoJugador.DoesNotExist):
                        pass
                
                # Opción 2: Por nombre + apellido
                if not jugador and nombre and apellido:
                    jugador_query = EquipoJugador.objects.filter(
                        equipo=equipo,
                        perfil_jugador__usuario__first_name__iexact=nombre,
                        perfil_jugador__usuario__last_name__iexact=apellido,
                        es_activo=True
                    ).select_related('perfil_jugador')
                    
                    if jugador_query.exists():
                        jugador = jugador_query.first().perfil_jugador
                
                # Opción 3: Por email
                if not jugador and email:
                    jugador_query = EquipoJugador.objects.filter(
                        equipo=equipo,
                        perfil_jugador__usuario__email__iexact=email,
                        es_activo=True
                    ).select_related('perfil_jugador')
                    
                    if jugador_query.exists():
                        jugador = jugador_query.first().perfil_jugador
                
                if not jugador:
                    identificador = f"{nombre} {apellido}" if nombre and apellido else dorsal or email
                    errores.append(f"Fila {idx}: Jugador '{identificador}' no encontrado o no activo")
                    continue
                
                # Validar que no exista ya estadística para este jugador en este partido
                if Estadistica.objects.filter(partido=partido, jugador=jugador).exists():
                    advertencias.append(f"Fila {idx}: {jugador.usuario.get_full_name()} ya tiene estadística en este partido (se actualizará)")
                
                # Procesar datos numéricos
                def obtener_entero(valor, default=0):
                    try:
                        return int(valor) if valor and str(valor).strip() else default
                    except (ValueError, TypeError):
                        return default
                
                def obtener_booleano(valor):
                    if isinstance(valor, bool):
                        return valor
                    if isinstance(valor, str):
                        return valor.lower() in ['true', '1', 'si', 'yes', 'verdadero', 'v']
                    return False
                
                # Crear objeto estadística
                estadistica_data = {
                    'partido': partido,
                    'jugador': jugador,
                    'titular': obtener_booleano(row.get('titular')),
                    'minutos_jugados': obtener_entero(row.get('minutos_jugados'), 0),
                    'goles': obtener_entero(row.get('goles'), 0),
                    'asistencias': obtener_entero(row.get('asistencias'), 0),
                    'tiros': obtener_entero(row.get('tiros'), 0),
                    'pases': obtener_entero(row.get('pases'), 0),
                    'fueras_de_juego': obtener_entero(row.get('fueras_de_juego'), 0),
                    'paradas': obtener_entero(row.get('paradas'), 0),
                    'despejes': obtener_entero(row.get('despejes'), 0),
                    'faltas': obtener_entero(row.get('faltas'), 0),
                    'tarjetas_amarillas': obtener_entero(row.get('tarjetas_amarillas'), 0),
                    'tarjeta_roja': obtener_booleano(row.get('tarjeta_roja')),
                }
                
                estadisticas_a_crear.append(estadistica_data)
            
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")
        
        # Si hay errores críticos, no guardar nada
        if errores:
            return JsonResponse({
                'success': False,
                'error': f"Errores encontrados ({len(errores)}): " + " | ".join(errores[:5]),
                'errores': errores[:5]
            }, status=400)
        
        # Usar transacción para guardar todo o nada
        try:
            with transaction.atomic():
                creadas = 0
                for stat_data in estadisticas_a_crear:
                    partido_id = stat_data.pop('partido').id
                    jugador_id = stat_data.pop('jugador').id
                    
                    Estadistica.objects.update_or_create(
                        partido_id=partido_id,
                        jugador_id=jugador_id,
                        defaults=stat_data
                    )
                    creadas += 1
            
            return JsonResponse({
                'success': True,
                'creadas': creadas,
                'advertencias': advertencias
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f"Error al guardar estadísticas: {str(e)}"
            }, status=400)
    
    except Partido.DoesNotExist:
        return JsonResponse({'error': 'Partido no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Error procesando CSV: {str(e)}"}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_analisis_ofensivo_ajax(request):
    """Obtiene datos de análisis ofensivo del equipo desde la base de datos."""
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener estadísticas de partidos finalizados
        estadisticas = Estadistica.objects.filter(
            partido__equipo_local=equipo,
            partido__finalizado=True
        ).aggregate(
            goles_total=Sum('goles'),
            asistencias_total=Sum('asistencias'),
            tiros_total=Sum('tiros'),
            pases_total=Sum('pases'),
            fueras_de_juego_total=Sum('fueras_de_juego'),
            partidos_count=Count('partido', distinct=True)
        )
        
        # Calcular promedios
        partidos_count = estadisticas['partidos_count'] or 1
        
        datos = {
            'goles_total': estadisticas['goles_total'] or 0,
            'goles_promedio': round((estadisticas['goles_total'] or 0) / partidos_count, 2),
            'asistencias_total': estadisticas['asistencias_total'] or 0,
            'asistencias_promedio': round((estadisticas['asistencias_total'] or 0) / partidos_count, 2),
            'tiros_total': estadisticas['tiros_total'] or 0,
            'tiros_promedio': round((estadisticas['tiros_total'] or 0) / partidos_count, 2),
            'pases_total': estadisticas['pases_total'] or 0,
            'pases_promedio': round((estadisticas['pases_total'] or 0) / partidos_count, 2),
            'fueras_de_juego_total': estadisticas['fueras_de_juego_total'] or 0,
            'fueras_de_juego_promedio': round((estadisticas['fueras_de_juego_total'] or 0) / partidos_count, 2),
            'partidos_jugados': partidos_count
        }
        
        # Normalizar a escala 0-100 para la gráfica radar
        # Usar máximos realistas para fútbol
        datos_normalizados = {
            'goles': min(datos['goles_promedio'] * 20, 100),  # ~5 goles = 100
            'asistencias': min(datos['asistencias_promedio'] * 20, 100),  # ~5 asistencias = 100
            'tiros': min(datos['tiros_promedio'] * 5, 100),  # ~20 tiros = 100
            'pases': min(datos['pases_promedio'] / 15, 100),  # ~1500 pases = 100
            'fueras_de_juego': min((100 - datos['fueras_de_juego_promedio'] * 10), 100)  # Menos es mejor
        }
        
        return JsonResponse({
            'success': True,
            'datos': datos_normalizados,
            'detalles': datos
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_analisis_defensivo_ajax(request):
    """Obtiene datos de análisis defensivo del equipo desde la base de datos."""
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener estadísticas defensivas de partidos finalizados
        estadisticas = Estadistica.objects.filter(
            partido__equipo_local=equipo,
            partido__finalizado=True
        ).aggregate(
            despejes_total=Sum('despejes'),
            faltas_total=Sum('faltas'),
            tarjetas_amarillas_total=Sum('tarjetas_amarillas'),
            tarjeta_roja_total=Count('id', filter=Q(tarjeta_roja=True)),
            paradas_total=Sum('paradas'),
            partidos_count=Count('partido', distinct=True)
        )
        
        partidos_count = estadisticas['partidos_count'] or 1
        
        # Calcular datos defensivos
        datos = {
            'despejes_promedio': round((estadisticas['despejes_total'] or 0) / partidos_count, 2),
            'faltas_promedio': round((estadisticas['faltas_total'] or 0) / partidos_count, 2),
            'tarjetas_amarillas_promedio': round((estadisticas['tarjetas_amarillas_total'] or 0) / partidos_count, 2),
            'tarjeta_roja_total': estadisticas['tarjeta_roja_total'] or 0,
            'paradas_promedio': round((estadisticas['paradas_total'] or 0) / partidos_count, 2),
            'partidos_jugados': partidos_count
        }
        
        # Obtener resultados para calcular defensa efectiva
        partidos = Partido.objects.filter(
            equipo_local=equipo,
            finalizado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        )
        
        goles_en_contra = sum(p.goles_visitante for p in partidos)
        
        datos['goles_en_contra_promedio'] = round(goles_en_contra / max(partidos.count(), 1), 2)
        
        # Normalizar a escala 0-100 para la gráfica de barras
        datos_normalizados = {
            'despejes': min(datos['despejes_promedio'] * 2, 100),  # ~50 despejes = 100
            'intercepciones': min(datos['despejes_promedio'], 100),  # Proporción a despejes
            'entradas': min(datos['faltas_promedio'] * 3, 100),  # ~33 faltas = 100
            'bloqueos': min(datos['despejes_promedio'], 100),
            'tarjetas': min(100 - (datos['tarjetas_amarillas_promedio'] * 5), 100)  # Menos es mejor
        }
        
        return JsonResponse({
            'success': True,
            'datos': datos_normalizados,
            'detalles': datos
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def debug_jugadores_forma(request):
    """Endpoint de debug para ver información de jugadores en forma."""
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Información de debug
        info = {
            'equipo': equipo.nombre,
            'equipo_id': equipo.id,
            'jugadores_activos': equipo.jugadores.filter(es_activo=True).count(),
            'partidos_finalizados': Partido.objects.filter(
                equipo_local=equipo,
                finalizado=True
            ).count(),
            'estadisticas_totales': Estadistica.objects.filter(
                partido__equipo_local=equipo,
                partido__finalizado=True
            ).count(),
            'jugadores_en_forma': obtener_jugadores_en_forma(equipo.id, limite=5),
            'jugadores_pobre_forma': obtener_jugadores_pobre_forma(equipo.id, limite=5),
        }
        
        return JsonResponse(info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



    """Obtiene datos de análisis defensivo del equipo desde la base de datos."""
    try:
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'No tienes equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener estadísticas defensivas de partidos finalizados
        estadisticas = Estadistica.objects.filter(
            partido__equipo_local=equipo,
            partido__finalizado=True
        ).aggregate(
            despejes_total=Sum('despejes'),
            faltas_total=Sum('faltas'),
            tarjetas_amarillas_total=Sum('tarjetas_amarillas'),
            tarjeta_roja_total=Count('id', filter=Q(tarjeta_roja=True)),
            paradas_total=Sum('paradas'),
            partidos_count=Count('partido', distinct=True)
        )
        
        partidos_count = estadisticas['partidos_count'] or 1
        
        # Calcular datos defensivos
        datos = {
            'despejes_total': estadisticas['despejes_total'] or 0,
            'despejes_promedio': round((estadisticas['despejes_total'] or 0) / partidos_count, 2),
            'faltas_total': estadisticas['faltas_total'] or 0,
            'faltas_promedio': round((estadisticas['faltas_total'] or 0) / partidos_count, 2),
            'tarjetas_amarillas_total': estadisticas['tarjetas_amarillas_total'] or 0,
            'tarjetas_amarillas_promedio': round((estadisticas['tarjetas_amarillas_total'] or 0) / partidos_count, 2),
            'tarjeta_roja_total': estadisticas['tarjeta_roja_total'] or 0,
            'paradas_total': estadisticas['paradas_total'] or 0,
            'paradas_promedio': round((estadisticas['paradas_total'] or 0) / partidos_count, 2),
            'partidos_jugados': partidos_count
        }
        
        # Obtener resultados para calcular defensa efectiva
        partidos = Partido.objects.filter(
            equipo_local=equipo,
            finalizado=True,
            goles_local__isnull=False,
            goles_visitante__isnull=False
        )
        
        goles_en_contra = sum(p.goles_visitante for p in partidos)
        
        datos['goles_en_contra_promedio'] = round(goles_en_contra / max(partidos.count(), 1), 2)
        
        # Normalizar a escala 0-100 para la gráfica de barras
        datos_normalizados = {
            'despejes': min(datos['despejes_promedio'] * 2, 100),  # ~50 despejes = 100
            'faltas': min(100 - (datos['faltas_promedio'] * 5), 100),  # Menos es mejor
            'paradas': min(datos['paradas_promedio'] * 3, 100),  # ~33 paradas = 100
            'amarillas': min(100 - (datos['tarjetas_amarillas_promedio'] * 10), 100),  # Menos es mejor
            'rojas': min(100 - (datos['tarjeta_roja_total'] * 20), 100)  # Menos es mejor
        }
        
        return JsonResponse({
            'success': True,
            'datos': datos_normalizados,
            'detalles': datos
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_partidos_finalizados(request):
    """Obtiene los partidos finalizados del equipo del entrenador."""
    try:
        # Obtener equipo activo
        if not hasattr(request.user, 'perfil_entrenador'):
            return JsonResponse({'error': 'No tienes perfil de entrenador'}, status=403)
        
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'Sin equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener partidos finalizados
        partidos = Partido.objects.filter(
            equipo_local=equipo,
            finalizado=True
        ).order_by('-fecha_hora')
        
        partidos_lista = []
        for partido in partidos:
            fecha = partido.fecha_hora.strftime('%d/%m/%Y %H:%M') if partido.fecha_hora else 'N/A'
            equipo_visitante_nombre = partido.get_equipo_visitante_nombre()
            resultado_local = partido.goles_local if partido.goles_local is not None else 0
            resultado_visitante = partido.goles_visitante if partido.goles_visitante is not None else 0
            partidos_lista.append({
                'id': partido.id,
                'label': f"{fecha} - {partido.equipo_local.nombre} {resultado_local}-{resultado_visitante} {equipo_visitante_nombre}",
                'fecha': fecha
            })
        
        return JsonResponse({
            'success': True,
            'partidos': partidos_lista
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_estadisticas_jugador(request):
    """Obtiene las estadísticas totales de un jugador específico."""
    try:
        # Obtener equipo activo
        if not hasattr(request.user, 'perfil_entrenador'):
            return JsonResponse({'error': 'No tienes perfil de entrenador'}, status=403)
        
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'Sin equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener ID del jugador
        jugador_id = request.GET.get('jugador_id')
        if not jugador_id:
            return JsonResponse({'error': 'Falta jugador_id'}, status=400)
        
        # Obtener jugador
        try:
            jugador = PerfilJugador.objects.get(id=jugador_id)
        except PerfilJugador.DoesNotExist:
            return JsonResponse({'error': 'Jugador no encontrado'}, status=404)
        
        # Obtener estadísticas totales del jugador en partidos de este equipo
        stats_totales = Estadistica.objects.filter(
            jugador=jugador,
            partido__equipo_local=equipo
        ).aggregate(
            partidos_jugados=Count('id'),
            goles=Sum('goles'),
            asistencias=Sum('asistencias'),
            tiros=Sum('tiros'),
            pases=Sum('pases'),
            fueras_de_juego=Sum('fueras_de_juego'),
            paradas=Sum('paradas'),
            despejes=Sum('despejes'),
            faltas=Sum('faltas'),
            amarillas=Sum('tarjetas_amarillas'),
            rojas=Count('id', filter=Q(tarjeta_roja=True))
        )
        
        # Rellenar con 0 si es None
        for key in stats_totales:
            if stats_totales[key] is None:
                stats_totales[key] = 0
        
        return JsonResponse({
            'success': True,
            'nombre': jugador.usuario.get_full_name(),
            'posicion': jugador.get_posicion_display(),
            'dorsal': jugador.dorsal,
            'stats': stats_totales
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_estadisticas_jugador_por_90(request):
    """Obtiene las estadísticas de un jugador normalizadas a cada 90 minutos."""
    try:
        import pandas as pd
        
        # Obtener equipo activo
        if not hasattr(request.user, 'perfil_entrenador'):
            return JsonResponse({'error': 'No tienes perfil de entrenador'}, status=403)
        
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'Sin equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener ID del jugador
        jugador_id = request.GET.get('jugador_id')
        if not jugador_id:
            return JsonResponse({'error': 'Falta jugador_id'}, status=400)
        
        # Obtener jugador
        try:
            jugador = PerfilJugador.objects.get(id=jugador_id)
        except PerfilJugador.DoesNotExist:
            return JsonResponse({'error': 'Jugador no encontrado'}, status=404)
        
        # Obtener estadísticas del jugador en partidos de este equipo
        estadisticas_list = Estadistica.objects.filter(
            jugador=jugador,
            partido__equipo_local=equipo
        ).values(
            'goles', 'asistencias', 'tiros', 'pases', 'fueras_de_juego',
            'paradas', 'despejes', 'faltas', 'tarjetas_amarillas', 'tarjeta_roja',
            'minutos_jugados'
        )
        
        if not estadisticas_list:
            return JsonResponse({
                'success': True,
                'stats_por_90': {
                    'goles': 0,
                    'asistencias': 0,
                    'tiros': 0,
                    'pases': 0,
                    'fueras_de_juego': 0,
                    'despejes': 0,
                    'faltas': 0,
                    'paradas': 0,
                    'amarillas': 0,
                    'rojas': 0,
                    'partidos_jugados': 0,
                    'minutos_totales': 0
                }
            })
        
        # Crear DataFrame con pandas
        df = pd.DataFrame(list(estadisticas_list))
        
        # Calcular totales
        minutos_totales = df['minutos_jugados'].sum()
        partidos_jugados = len(df)
        
        # Si no hay minutos jugados, evitar división por cero
        if minutos_totales == 0:
            multiplicador = 0
        else:
            multiplicador = 90.0 / minutos_totales
        
        # Calcular estadísticas por 90 minutos
        stats_por_90 = {
            'goles': round(df['goles'].sum() * multiplicador, 2),
            'asistencias': round(df['asistencias'].sum() * multiplicador, 2),
            'tiros': round(df['tiros'].sum() * multiplicador, 2),
            'pases': round(df['pases'].sum() * multiplicador, 2),
            'fueras_de_juego': round(df['fueras_de_juego'].sum() * multiplicador, 2),
            'despejes': round(df['despejes'].sum() * multiplicador, 2),
            'faltas': round(df['faltas'].sum() * multiplicador, 2),
            'paradas': round(df['paradas'].sum() * multiplicador, 2),
            'amarillas': round(df['tarjetas_amarillas'].sum() * multiplicador, 2),
            'rojas': round(df['tarjeta_roja'].sum() * multiplicador, 2),
            'partidos_jugados': partidos_jugados,
            'minutos_totales': int(minutos_totales)
        }
        
        return JsonResponse({
            'success': True,
            'stats_por_90': stats_por_90
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_estadisticas_jugador_partido(request):
    """Obtiene las estadísticas de un jugador en un partido específico."""
    try:
        # Obtener equipo activo
        if not hasattr(request.user, 'perfil_entrenador'):
            return JsonResponse({'error': 'No tienes perfil de entrenador'}, status=403)
        
        # Obtener parámetros
        jugador_id = request.GET.get('jugador_id')
        partido_id = request.GET.get('partido_id')
        
        if not jugador_id or not partido_id:
            return JsonResponse({'error': 'Faltan parámetros'}, status=400)
        
        # Obtener estadística
        try:
            estadistica = Estadistica.objects.get(
                jugador_id=jugador_id,
                partido_id=partido_id
            )
        except Estadistica.DoesNotExist:
            return JsonResponse({
                'success': True,
                'encontrada': False,
                'mensaje': 'El jugador no participó en este partido'
            })
        
        return JsonResponse({
            'success': True,
            'encontrada': True,
            'titular': estadistica.titular,
            'minutos_jugados': estadistica.minutos_jugados,
            'goles': estadistica.goles,
            'asistencias': estadistica.asistencias,
            'tiros': estadistica.tiros,
            'pases': estadistica.pases,
            'fueras_de_juego': estadistica.fueras_de_juego,
            'paradas': estadistica.paradas,
            'despejes': estadistica.despejes,
            'faltas': estadistica.faltas,
            'amarillas': estadistica.tarjetas_amarillas,
            'rojas': 1 if estadistica.tarjeta_roja else 0
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def obtener_once_filtrado(request):
    """Obtiene el once filtrado por posición o sin filtro."""
    try:
        # Obtener equipo activo
        if not hasattr(request.user, 'perfil_entrenador'):
            return JsonResponse({'error': 'No tienes perfil de entrenador'}, status=403)
        
        equipos_activos = request.user.perfil_entrenador.equipos.filter(es_activo=True)
        if not equipos_activos.exists():
            return JsonResponse({'error': 'Sin equipo activo'}, status=400)
        
        equipo = equipos_activos.first().equipo
        
        # Obtener parámetro de filtro (puede ser None)
        posicion_filtro = request.GET.get('posicion', None)
        if posicion_filtro == '':
            posicion_filtro = None
        
        # Obtener jugadores
        jugadores = obtener_once_recomendado(equipo.id, posicion_filtro=posicion_filtro)
        
        return JsonResponse({
            'success': True,
            'jugadores': jugadores
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
