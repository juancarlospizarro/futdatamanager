"""
Views (Controladores) para control_jugadores
"""

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .models import Aviso, Lesion, Sancion
from equipos.models import EquipoEntrenador
from usuarios.models import PerfilJugador



@login_required
@require_http_methods(["GET"])
def obtener_lesiones_jugador(request, jugador_id):
    """
    Obtiene todas las lesiones de un jugador en formato JSON.
    """
    try:
        perfil_jugador = PerfilJugador.objects.get(id=jugador_id)
        lesiones = perfil_jugador.lesiones.all().values(
            'id', 'tipo', 'fecha_inicio', 'dias_duracion', 'descripcion', 'activa'
        )
        return JsonResponse({
            'success': True,
            'lesiones': list(lesiones)
        })
    except PerfilJugador.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Jugador no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_sanciones_jugador(request, jugador_id):
    """
    Obtiene todas las sanciones de un jugador en formato JSON.
    """
    try:
        perfil_jugador = PerfilJugador.objects.get(id=jugador_id)
        sanciones = perfil_jugador.sanciones.all().values(
            'id', 'tipo', 'fecha', 'razon', 'partidos_duracion', 'activa'
        )
        return JsonResponse({
            'success': True,
            'sanciones': list(sanciones)
        })
    except PerfilJugador.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Jugador no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def eliminar_lesion(request, lesion_id):
    """
    Elimina una lesión. Solo el entrenador del equipo puede hacerlo.
    """
    try:
        lesion = Lesion.objects.get(id=lesion_id)
        equipo_del_jugador = lesion.jugador.equipos.filter(fecha_salida__isnull=True).first()
        
        if not equipo_del_jugador:
            return JsonResponse({
                'success': False,
                'error': 'El jugador no está en ningún equipo'
            }, status=400)
        
        # Verificar que el usuario es entrenador del equipo
        es_entrenador = EquipoEntrenador.objects.filter(
            equipo=equipo_del_jugador.equipo,
            perfil_entrenador__usuario=request.user
        ).exists()
        
        if not es_entrenador:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para eliminar esta lesión'
            }, status=403)
        
        lesion.delete()
        return JsonResponse({
            'success': True,
            'message': 'Lesión eliminada correctamente'
        })
    except Lesion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lesión no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def eliminar_sancion(request, sancion_id):
    """
    Elimina una sanción. Solo el entrenador del equipo puede hacerlo.
    """
    try:
        sancion = Sancion.objects.get(id=sancion_id)
        equipo_del_jugador = sancion.jugador.equipos.filter(fecha_salida__isnull=True).first()
        
        if not equipo_del_jugador:
            return JsonResponse({
                'success': False,
                'error': 'El jugador no está en ningún equipo'
            }, status=400)
        
        # Verificar que el usuario es entrenador del equipo
        es_entrenador = EquipoEntrenador.objects.filter(
            equipo=equipo_del_jugador.equipo,
            perfil_entrenador__usuario=request.user
        ).exists()
        
        if not es_entrenador:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para eliminar esta sanción'
            }, status=403)
        
        sancion.delete()
        return JsonResponse({
            'success': True,
            'message': 'Sanción eliminada correctamente'
        })
    except Sancion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sanción no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
