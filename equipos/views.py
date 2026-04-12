from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.decorators import entrenador_o_admin_required
from usuarios.models import PerfilJugador, Usuario, PerfilEntrenador
from .models import Equipo, EquipoEntrenador, EquipoJugador

@login_required
@entrenador_o_admin_required
def crear_equipo(request):
    """
    Crea un nuevo equipo de fútbol.
    Solo accesible para entrenadores y administradores.
    """

    usuario = request.user

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        anio_fundacion = request.POST.get("anio_fundacion")
        escudo = request.FILES.get("escudo")
        direccion = request.POST.get("direccion")
        telefono = request.POST.get("telefono")
        color_principal = request.POST.get("color_principal")
        color_secundario = request.POST.get("color_secundario")

        if not all([nombre, anio_fundacion, direccion, telefono]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("landing")

        equipo = Equipo(
            nombre=nombre,
            anio_fundacion=anio_fundacion,
            escudo=escudo,
            direccion=direccion,
            telefono=telefono,
            color_principal=color_principal,
            color_secundario=color_secundario
        )
        equipo.save()  # Esto ejecuta el método save() que genera el slug

        # Vincular al usuario como entrenador del equipo
        perfil_entrenador = PerfilEntrenador.objects.get_or_create(usuario=usuario)[0]
        EquipoEntrenador.objects.create(
            equipo=equipo,
            perfil_entrenador=perfil_entrenador
        )

        usuario.tiene_equipo = True
        usuario.save()

        messages.success(request, f"Equipo {equipo.nombre} creado correctamente.")

        # Recargar equipo para asegurar que tiene el slug
        equipo.refresh_from_db()
        return redirect('equipos:informacion_equipo', slug=equipo.slug)

    return render(request, "usuarios/inicio_entrenador_sin_equipo.html")

@login_required
def informacion_equipo(request, slug):
    """
    Muestra la información detallada de un equipo incluyendo jugadores activos,
    entrenamientos y opciones de edición para el entrenador del equipo.
    """
    equipo = get_object_or_404(Equipo, slug=slug)
    
    # Verificar si el usuario actual es entrenador de este equipo
    is_trainer = False
    if request.user.is_authenticated and request.user.rol == "entrenador":
        is_trainer = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            equipo=equipo,
            es_activo=True
        ).exists()
    
    # Obtener jugadores sin equipo
    jugadores_sin_equipo = PerfilJugador.objects.filter(
        usuario__tiene_equipo=False,
        usuario__rol='jugador'
    )
    
    # Obtener entrenador activo del equipo
    entrenador = equipo.entrenadores.filter(es_activo=True).first()
    
    # Obtener jugadores del equipo (activos)
    jugadores_equipo = equipo.jugadores.filter(es_activo=True).select_related(
        'perfil_jugador__usuario'
    ).order_by('perfil_jugador__usuario__first_name')
    
    context = {
        'equipo': equipo,
        'is_trainer': is_trainer,
        'jugadores_sin_equipo': jugadores_sin_equipo,
        'entrenador': entrenador,
        'jugadores_equipo': jugadores_equipo,
    }
    return render(request, 'equipos/informacion_equipo.html', context)

@login_required
@entrenador_o_admin_required
def editar_jugador(request, jugador_id):
    """
    Edita información de un jugador específico (dorsal y posición).
    Solo el entrenador del equipo donde el jugador está activo puede editar.
    """
    try:
        perfil_jugador = get_object_or_404(PerfilJugador, id=jugador_id)
        
        # Verificar que el usuario es entrenador de algún equipo del jugador
        es_entrenador = False
        for equipo_jugador in perfil_jugador.equipos.filter(es_activo=True):
            es_entrenador = EquipoEntrenador.objects.filter(
                perfil_entrenador=request.user.perfil_entrenador,
                equipo=equipo_jugador.equipo,
                es_activo=True
            ).exists()
            if es_entrenador:
                break
        
        if not es_entrenador:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        # Actualizar los datos
        dorsal = request.POST.get('dorsal')
        altura = request.POST.get('altura')
        peso = request.POST.get('peso')
        pierna_habil = request.POST.get('pierna_habil')
        posicion = request.POST.get('posicion')
        es_capitan = request.POST.get('es_capitan') == 'on'
        
        if dorsal and dorsal.strip():
            perfil_jugador.dorsal = int(dorsal)
        if altura and altura.strip():
            perfil_jugador.altura = int(altura)
        if peso and peso.strip():
            perfil_jugador.peso = float(peso)
        if pierna_habil:
            perfil_jugador.pierna_habil = pierna_habil
        if posicion:
            perfil_jugador.posicion = posicion
        else:
            perfil_jugador.posicion = None
        
        perfil_jugador.es_capitan = es_capitan
        perfil_jugador.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Información actualizada correctamente'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def eliminar_jugador_equipo(request, equipo_id, jugador_id):
    """
    Desactiva a un jugador de un equipo sin eliminar su perfil.
    Solo el entrenador del equipo puede ejecutar esta acción.
    """
    """
    Marca un jugador como inactivo en el equipo (mantiene histórico).
    Solo el entrenador del equipo puede hacerlo.
    """
    try:
        # Obtener el equipo y el jugador
        equipo = get_object_or_404(Equipo, id=equipo_id)
        perfil_jugador = get_object_or_404(PerfilJugador, id=jugador_id)
        
        # Verificar que el usuario es entrenador del equipo
        es_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            equipo=equipo,
            es_activo=True
        ).exists()
        
        if not es_entrenador:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        # Marcar la relación como inactiva en lugar de eliminar
        equipo_jugador = EquipoJugador.objects.filter(
            equipo=equipo,
            perfil_jugador=perfil_jugador,
            es_activo=True
        ).first()
        
        if not equipo_jugador:
            return JsonResponse({'success': False, 'error': 'El jugador no está activo en este equipo'}, status=404)
        
        # Marcar como inactivo y guardar la fecha de salida
        from django.utils import timezone
        equipo_jugador.es_activo = False
        equipo_jugador.fecha_salida = timezone.now().date()
        equipo_jugador.save()
        
        # Verificar si el jugador está activo en otros equipos
        otros_equipos = EquipoJugador.objects.filter(
            perfil_jugador=perfil_jugador,
            es_activo=True
        ).count()
        
        # Si no está en otros equipos activos, actualizar tiene_equipo
        if otros_equipos == 0:
            perfil_jugador.usuario.tiene_equipo = False
            perfil_jugador.usuario.save()
        
        # Limpiar datos deportivos del equipo (dorsal y posición)
        perfil_jugador.dorsal = None
        perfil_jugador.posicion = None
        perfil_jugador.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{perfil_jugador.usuario.get_full_name()} eliminado del equipo'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Vista AJAX para añadir jugador al equipo
@login_required
def agregar_jugador_equipo(request, equipo_id, jugador_id):
    """
    Agrega un jugador a un equipo.
    Solo el entrenador del equipo puede agregar jugadores.
    """
    if request.method == 'POST':
        equipo = get_object_or_404(Equipo, id=equipo_id)
        perfil_jugador = get_object_or_404(PerfilJugador, id=jugador_id)
        
        # Verificar que el usuario es entrenador de este equipo
        is_trainer = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            equipo=equipo,
            es_activo=True
        ).exists()
        
        if not is_trainer:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        # Verificar si el jugador ya está ACTIVO en este equipo
        ya_existe_activo = EquipoJugador.objects.filter(
            equipo=equipo,
            perfil_jugador=perfil_jugador,
            es_activo=True
        ).exists()
        
        if ya_existe_activo:
            return JsonResponse({
                'success': False,
                'error': 'El jugador ya está en este equipo'
            })
        
        # Crear nuevo registro (permite múltiples periodos)
        equipo_jugador = EquipoJugador.objects.create(
            equipo=equipo,
            perfil_jugador=perfil_jugador,
            es_activo=True
        )
        
        # Actualizar el booleano tiene_equipo del usuario
        perfil_jugador.usuario.tiene_equipo = True
        perfil_jugador.usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{perfil_jugador.usuario.get_full_name()} añadido al equipo'
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def listado_equipos(request):
    """
    Muestra el listado de todos los equipos disponibles en la plataforma.
    """
    equipos = Equipo.objects.all()
    return render(request, "equipos/listado.html", {"equipos": equipos})

@login_required
def editar_datos_equipo(request, equipo_id):
    """
    Edita los datos básicos de un equipo (nombre, colors, dirección, teléfono, escudo).
    Solo el entrenador o administrador del equipo puede editar.
    """
    equipo = get_object_or_404(Equipo, id=equipo_id)

    if request.method == "POST":
        try:
            equipo.nombre = request.POST.get("nombre")
            equipo.anio_fundacion = request.POST.get("anio_fundacion")
            equipo.direccion = request.POST.get("direccion")
            equipo.telefono = request.POST.get("telefono")
            equipo.color_principal = request.POST.get("color_principal")
            equipo.color_secundario = request.POST.get("color_secundario")

            if "escudo" in request.FILES:
                equipo.escudo = request.FILES["escudo"]

            equipo.save()
            messages.success(request, "Datos del equipo actualizados correctamente")
            return redirect('equipos:informacion_equipo', slug=equipo.slug)

        except Exception as e:
            return render(request, 'equipos/informacion_equipo.html', {'equipo': equipo, 'error': f"Error al actualizar: {str(e)}"})

    return render(request, 'equipos/informacion_equipo.html', {'equipo': equipo})

@login_required
def abandonar_equipo(request, equipo_id):
    """
    Permite a un jugador abandonar un equipo desactivando su relación con el equipo.
    """
    # Obtener el equipo y verificar que el usuario es el dueño (entrenador vinculado)
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Seguridad: Solo el entrenador del equipo puede borrarlo
    if request.user.perfil_entrenador.equipo != equipo:
        messages.error(request, "No tienes permiso para abandonar este equipo.")
        return redirect('landing')


@login_required
def pizarra_tactica(request, slug):
    """
    Vista para la pizarra táctica del equipo.
    Solo los entrenadores activos del equipo pueden acceder.
    """
    equipo = get_object_or_404(Equipo, slug=slug)
    
    # Verificar si el usuario es entrenador del equipo
    if request.user.rol != "entrenador":
        messages.error(request, "Solo los entrenadores pueden acceder a la pizarra táctica.")
        return redirect('landing')
    
    is_trainer = EquipoEntrenador.objects.filter(
        perfil_entrenador=request.user.perfil_entrenador,
        equipo=equipo,
        es_activo=True
    ).exists()
    
    if not is_trainer:
        messages.error(request, "No tienes permiso para acceder a la pizarra táctica de este equipo.")
        return redirect('landing')
    
    # Obtener jugadores del equipo (activos)
    jugadores_equipo = equipo.jugadores.filter(es_activo=True).select_related(
        'perfil_jugador__usuario'
    ).order_by('perfil_jugador__usuario__first_name')
    
    context = {
        'equipo': equipo,
        'jugadores': jugadores_equipo,
    }
    
    return render(request, 'equipos/pizarra_tactica.html', context)
