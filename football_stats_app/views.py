from django.shortcuts import render, redirect
from equipos.models import Equipo, EquipoJugador, EquipoEntrenador
from django.core.exceptions import SuspiciousOperation, PermissionDenied


def error_404(request, exception):
    """Maneja errores 404 (página no encontrada)"""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Maneja errores 500 (error del servidor)"""
    return render(request, 'errors/500.html', status=500)

def error_500_test(request):
    """
    Función de prueba que dispara un error 500.
    Solo para testing en ambiente de desarrollo.
    """
    1 / 0  # ZeroDivisionError


def error_403(request, exception):
    """Maneja errores 403 (permiso denegado)"""
    return render(request, 'errors/403.html', status=403)

def error_403_test(request):
    """
    Función de prueba que dispara un error 403.
    Solo para testing en ambiente de desarrollo.
    """
    raise PermissionDenied


def error_400(request, exception):
    """Maneja errores 400 (solicitud incorrecta)"""
    return render(request, 'errors/400.html', status=400)

def error_400_test(request):
    """
    Función de prueba que dispara un error 400.
    Solo para testing en ambiente de desarrollo.
    """
    raise SuspiciousOperation("Algo huele mal")


def landing(request):
    """
    Vista principal que redirige al usuario según su rol y estado de autenticación.
    - Si no está logueado: muestra página de inicio
    - Si es entrenador sin equipo: redirige a crear/seleccionar equipo
    - Si es entrenador con equipo: redirige a su equipo
    - Si es jugador: muestra dashboard de jugador
    """
    # 1. Si el usuario NO está logueado
    if not request.user.is_authenticated:
        return render(request, 'landing.html')

    # 2. Si el usuario SÍ está logueado
    usuario = request.user

    # CASO A: Es un ADMIN
    if usuario.is_superuser:
        return redirect('/admin/') 

    # CASO B: Es un ENTRENADOR
    elif usuario.rol == usuario.Rol.ENTRENADOR:
        if usuario.tiene_equipo:
            return render(request, 'usuarios/inicio_entrenador_con_equipo.html')
        else:
            equipos = Equipo.objects.all()
            # Obtener el histórico de equipos donde ha entrenado (solo registros inactivos = periodos pasados)
            equipos_historico = EquipoEntrenador.objects.filter(
                perfil_entrenador=usuario.perfil_entrenador,
                es_activo=False
            ).select_related('equipo').order_by('-fecha_incorporacion')
            
            return render(request, 'usuarios/inicio_entrenador_sin_equipo.html', {
                'equipos': equipos,
                'equipos_historico': equipos_historico
            })

    # CASO C: Es un JUGADOR
    elif usuario.rol == usuario.Rol.JUGADOR:
        if usuario.tiene_equipo:
            return render(request, 'usuarios/inicio_jugador_con_equipo.html')
        else:
            equipos = Equipo.objects.all()
            # Obtener el histórico de equipos donde ha jugado (solo registros inactivos = periodos pasados)
            equipos_historico = EquipoJugador.objects.filter(
                perfil_jugador=usuario.perfil_jugador,
                es_activo=False
            ).select_related('equipo').order_by('-fecha_incorporacion')
            
            return render(request, 'usuarios/inicio_jugador_sin_equipo.html', {
                'equipos': equipos,
                'equipos_historico': equipos_historico
            })

    # CASO D: Rol desconocido o error
    else:
        return render(request, 'landing.html')