from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from equipos.models import Equipo, EquipoEntrenador
from usuarios.decorators import entrenador_o_admin_required
from .models import Partido, Entrenamiento


def verificar_entrenador_equipo(user, equipo):
    """Verifica si el usuario es entrenador activo del equipo."""
    if user.rol != 'entrenador':
        return False
    return EquipoEntrenador.objects.filter(
        perfil_entrenador=user.perfil_entrenador,
        equipo=equipo,
        es_activo=True
    ).exists()


# ============== PARTIDOS ==============

@login_required
@entrenador_o_admin_required
def crear_partido(request, slug):
    """Crear un nuevo partido."""
    equipo = get_object_or_404(Equipo, slug=slug)
    
    # Verificar que el usuario es entrenador del equipo
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para crear partidos en este equipo"))
        return redirect('landing')
    
    if request.method == 'POST':
        # Crear el partido desde el formulario POST
        equipo_visitante_id = request.POST.get('equipo_visitante_id')
        nombre_equipo_visitante = request.POST.get('nombre_equipo_visitante', '').strip()
        
        equipo_visitante = None
        if equipo_visitante_id:
            equipo_visitante = get_object_or_404(Equipo, id=equipo_visitante_id)
        elif not nombre_equipo_visitante:
            messages.error(request, _("Debes seleccionar un equipo o introducir un nombre"))
            return render(request, 'eventos/crear_partido.html', {
                'equipo': equipo,
                'equipos': Equipo.objects.exclude(id=equipo.id)
            })
        
        partido = Partido.objects.create(
            equipo_local=equipo,
            equipo_visitante=equipo_visitante,
            nombre_equipo_visitante=nombre_equipo_visitante,
            estadio_nombre=request.POST.get('estadio_nombre', ''),
            estadio_direccion=request.POST.get('estadio_direccion', ''),
            fecha_hora=request.POST.get('fecha_hora'),
            posesion_local=int(request.POST.get('posesion_local', 0)),
            posesion_visitante=int(request.POST.get('posesion_visitante', 0)),
        )
        
        messages.success(request, _("Partido creado correctamente"))
        return redirect('equipos:informacion_equipo', slug=slug)
    
    context = {
        'equipo': equipo,
        'equipos': Equipo.objects.exclude(id=equipo.id),
        'action': 'crear'
    }
    return render(request, 'eventos/crear_partido.html', context)


@login_required
@entrenador_o_admin_required
def editar_partido(request, partido_id):
    """Editar un partido existente."""
    partido = get_object_or_404(Partido, id=partido_id)
    equipo = partido.equipo_local
    
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para editar este partido"))
        return redirect('landing')
    
    if request.method == 'POST':
        equipo_visitante_id = request.POST.get('equipo_visitante_id')
        nombre_equipo_visitante = request.POST.get('nombre_equipo_visitante', '').strip()
        
        equipo_visitante = None
        if equipo_visitante_id:
            equipo_visitante = get_object_or_404(Equipo, id=equipo_visitante_id)
        elif not nombre_equipo_visitante:
            messages.error(request, _("Debes seleccionar un equipo o introducir un nombre"))
            return render(request, 'eventos/crear_partido.html', {
                'equipo': equipo,
                'equipos': Equipo.objects.exclude(id=equipo.id),
                'partido': partido,
                'action': 'editar'
            })
        
        partido.equipo_visitante = equipo_visitante
        partido.nombre_equipo_visitante = nombre_equipo_visitante
        partido.estadio_nombre = request.POST.get('estadio_nombre', '')
        partido.estadio_direccion = request.POST.get('estadio_direccion', '')
        partido.fecha_hora = request.POST.get('fecha_hora')
        partido.posesion_local = int(request.POST.get('posesion_local', 0))
        partido.posesion_visitante = int(request.POST.get('posesion_visitante', 0))
        partido.finalizado = request.POST.get('finalizado') == 'on'
        partido.save()
        
        messages.success(request, _("Partido actualizado correctamente"))
        return redirect('equipos:informacion_equipo', slug=equipo.slug)
    
    context = {
        'equipo': equipo,
        'equipos': Equipo.objects.exclude(id=equipo.id),
        'partido': partido,
        'action': 'editar'
    }
    return render(request, 'eventos/crear_partido.html', context)


@login_required
@entrenador_o_admin_required
def eliminar_partido(request, partido_id):
    """Eliminar un partido."""
    partido = get_object_or_404(Partido, id=partido_id)
    equipo = partido.equipo_local
    
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para eliminar este partido"))
        return redirect('landing')
    
    if request.method == 'POST':
        partido.delete()
        messages.success(request, _("Partido eliminado correctamente"))
    
    return redirect('equipos:informacion_equipo', slug=equipo.slug)


@login_required
def listar_partidos(request, slug):
    """Listar partidos de un equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)
    partidos = Partido.objects.filter(equipo_local=equipo).order_by('-fecha_hora')
    
    context = {
        'equipo': equipo,
        'partidos': partidos,
    }
    return render(request, 'eventos/listar_partidos.html', context)


# ============== ENTRENAMIENTOS ==============

@login_required
@entrenador_o_admin_required
def crear_entrenamiento(request, slug):
    """Crear un nuevo entrenamiento."""
    equipo = get_object_or_404(Equipo, slug=slug)
    
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para crear entrenamientos en este equipo"))
        return redirect('landing')
    
    if request.method == 'POST':
        entrenamiento = Entrenamiento.objects.create(
            equipo=equipo,
            fecha_hora=request.POST.get('fecha_hora'),
            tipo=request.POST.get('tipo'),
            descripcion=request.POST.get('descripcion', ''),
        )
        
        messages.success(request, _("Entrenamiento creado correctamente"))
        return redirect('equipos:informacion_equipo', slug=slug)
    
    context = {
        'equipo': equipo,
        'tipos_entrenamiento': Entrenamiento.TIPO_CHOICES,
        'action': 'crear'
    }
    return render(request, 'eventos/crear_entrenamiento.html', context)


@login_required
@entrenador_o_admin_required
def editar_entrenamiento(request, entrenamiento_id):
    """Editar un entrenamiento existente."""
    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id)
    equipo = entrenamiento.equipo
    
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para editar este entrenamiento"))
        return redirect('landing')
    
    if request.method == 'POST':
        entrenamiento.fecha_hora = request.POST.get('fecha_hora')
        entrenamiento.tipo = request.POST.get('tipo')
        entrenamiento.descripcion = request.POST.get('descripcion', '')
        entrenamiento.save()
        
        messages.success(request, _("Entrenamiento actualizado correctamente"))
        return redirect('equipos:informacion_equipo', slug=equipo.slug)
    
    context = {
        'equipo': equipo,
        'entrenamiento': entrenamiento,
        'tipos_entrenamiento': Entrenamiento.TIPO_CHOICES,
        'action': 'editar'
    }
    return render(request, 'eventos/crear_entrenamiento.html', context)


@login_required
@entrenador_o_admin_required
def eliminar_entrenamiento(request, entrenamiento_id):
    """Eliminar un entrenamiento."""
    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id)
    equipo = entrenamiento.equipo
    
    if not verificar_entrenador_equipo(request.user, equipo):
        messages.error(request, _("No tienes permiso para eliminar este entrenamiento"))
        return redirect('landing')
    
    if request.method == 'POST':
        entrenamiento.delete()
        messages.success(request, _("Entrenamiento eliminado correctamente"))
    
    return redirect('equipos:informacion_equipo', slug=equipo.slug)


@login_required
def listar_entrenamientos(request, slug):
    """Listar entrenamientos de un equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)
    entrenamientos = Entrenamiento.objects.filter(equipo=equipo).order_by('-fecha_hora')
    
    context = {
        'equipo': equipo,
        'entrenamientos': entrenamientos,
    }
    return render(request, 'eventos/listar_entrenamientos.html', context)


# ============== VISTAS AJAX PARA ENTRENAMIENTOS ==============

@login_required
def crear_entrenamiento_ajax(request):
    """Crear un entrenamiento vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse({'error': 'No eres entrenador'}, status=403)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse({'error': 'No tienes equipo asignado'}, status=403)
        
        equipo = equipo_entrenador.equipo
        
        fecha_hora = request.POST.get('fecha_hora')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion', '')
        
        if not fecha_hora or not tipo:
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
        
        entrenamiento = Entrenamiento.objects.create(
            equipo=equipo,
            fecha_hora=fecha_hora,
            tipo=tipo,
            descripcion=descripcion,
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Entrenamiento creado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
def obtener_entrenamientos_ajax(request):
    """Obtener entrenamientos del equipo actual del usuario (para el calendario)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        entrenamientos = Entrenamiento.objects.filter(equipo=equipo).order_by('fecha_hora')
        
        eventos = []
        for entrenamiento in entrenamientos:
            eventos.append({
                'id': entrenamiento.id,
                'title': f"{entrenamiento.get_tipo_display()}",
                'start': entrenamiento.fecha_hora.isoformat(),
                'type': 'entrenamiento',
                'tipo': entrenamiento.get_tipo_display(),
                'descripcion': entrenamiento.descripcion,
                'fecha_hora': entrenamiento.fecha_hora.strftime('%d/%m/%Y %H:%M')
            })
        
        return JsonResponse(eventos, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def listar_entrenamientos_ajax(request):
    """Listar entrenamientos del equipo actual (para el modal de eliminación)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        entrenamientos = Entrenamiento.objects.filter(equipo=equipo).order_by('-fecha_hora')
        
        datos = []
        for entrenamiento in entrenamientos:
            datos.append({
                'id': entrenamiento.id,
                'tipo': entrenamiento.get_tipo_display(),
                'fecha_hora': entrenamiento.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'descripcion': entrenamiento.descripcion,
            })
        
        return JsonResponse(datos, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def eliminar_entrenamiento_ajax(request, entrenamiento_id):
    """Eliminar un entrenamiento vía AJAX."""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id)
        equipo = entrenamiento.equipo
        
        # Verificar que el usuario es entrenador activo del equipo
        if not verificar_entrenador_equipo(request.user, equipo):
            return JsonResponse({'error': 'No tienes permiso'}, status=403)
        
        entrenamiento.delete()
        return JsonResponse({'success': True, 'mensaje': 'Entrenamiento eliminado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============== VISTAS AJAX PARA PARTIDOS ==============

@login_required
def crear_partido_ajax(request):
    """Crear un partido vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse({'error': 'No eres entrenador'}, status=403)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse({'error': 'No tienes equipo asignado'}, status=403)
        
        equipo = equipo_entrenador.equipo
        
        fecha_hora = request.POST.get('fecha_hora')
        equipo_visitante_id = request.POST.get('equipo_visitante_id')
        nombre_equipo_visitante = request.POST.get('nombre_equipo_visitante', '').strip()
        estadio_nombre = request.POST.get('estadio_nombre', '')
        estadio_direccion = request.POST.get('estadio_direccion', '')
        posesion_local = request.POST.get('posesion_local', 0)
        posesion_visitante = request.POST.get('posesion_visitante', 0)
        
        if not fecha_hora or not estadio_nombre:
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
        
        # Validar que hay equipo visitante (BD o manual)
        if not equipo_visitante_id and not nombre_equipo_visitante:
            return JsonResponse({'error': 'Debes seleccionar un equipo o escribir uno'}, status=400)
        
        equipo_visitante = None
        if equipo_visitante_id:
            equipo_visitante = get_object_or_404(Equipo, id=equipo_visitante_id)
        
        partido = Partido.objects.create(
            equipo_local=equipo,
            equipo_visitante=equipo_visitante,
            nombre_equipo_visitante=nombre_equipo_visitante,
            estadio_nombre=estadio_nombre,
            estadio_direccion=estadio_direccion,
            fecha_hora=fecha_hora,
            posesion_local=int(posesion_local) if posesion_local else 0,
            posesion_visitante=int(posesion_visitante) if posesion_visitante else 0,
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Partido creado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


@login_required
def obtener_equipos_ajax(request):
    """Obtener lista de equipos disponibles (excluyendo el del usuario)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        
        # Obtener todos los equipos excepto el propio
        equipos = Equipo.objects.exclude(id=equipo.id).values('id', 'nombre')
        
        return JsonResponse(list(equipos), safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def obtener_partidos_ajax(request):
    """Obtener partidos del equipo actual del usuario (para el calendario)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        partidos = Partido.objects.filter(
            equipo_local=equipo
        ).order_by('fecha_hora')
        
        eventos = []
        for partido in partidos:
            rival = partido.equipo_visitante.nombre if partido.equipo_visitante else partido.nombre_equipo_visitante
            rival_slug = partido.equipo_visitante.slug if partido.equipo_visitante else None
            
            # Si está finalizado, añadir indicator visual
            titulo = f"Partido vs {rival}"
            if partido.finalizado:
                titulo = f"✓ {titulo}"
            
            eventos.append({
                'id': partido.id,
                'title': titulo,
                'start': partido.fecha_hora.isoformat(),
                'type': 'partido',
                'rival': rival,
                'rival_slug': rival_slug,
                'estadio': partido.estadio_nombre,
                'estadio_direccion': partido.estadio_direccion,
                'fecha_hora': partido.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'finalizado': partido.finalizado
            })
        
        return JsonResponse(eventos, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def listar_partidos_ajax(request):
    """Listar partidos del equipo actual (para el modal de eliminación)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        partidos = Partido.objects.filter(equipo_local=equipo).order_by('-fecha_hora')
        
        datos = []
        for partido in partidos:
            rival = partido.equipo_visitante.nombre if partido.equipo_visitante else partido.nombre_equipo_visitante
            datos.append({
                'id': partido.id,
                'rival': rival,
                'fecha_hora': partido.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'estadio': partido.estadio_nombre,
            })
        
        return JsonResponse(datos, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def eliminar_partido_ajax(request, partido_id):
    """Eliminar un partido vía AJAX."""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        partido = get_object_or_404(Partido, id=partido_id)
        equipo = partido.equipo_local
        
        # Verificar que el usuario es entrenador activo del equipo
        if not verificar_entrenador_equipo(request.user, equipo):
            return JsonResponse({'error': 'No tienes permiso'}, status=403)
        
        partido.delete()
        return JsonResponse({'success': True, 'mensaje': 'Partido eliminado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def finalizar_partido_ajax(request, partido_id):
    """Marcar un partido como finalizado vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        partido = get_object_or_404(Partido, id=partido_id)
        equipo = partido.equipo_local
        
        # Verificar que el usuario es entrenador activo del equipo
        if not verificar_entrenador_equipo(request.user, equipo):
            return JsonResponse({'error': 'No tienes permiso'}, status=403)
        
        partido.finalizado = True
        partido.save()
        return JsonResponse({'success': True, 'mensaje': 'Partido marcado como finalizado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def obtener_partidos_finalizados_ajax(request):
    """Obtener partidos finalizados del equipo actual (para partidos anteriores)."""
    try:
        # Verificar que el usuario es entrenador
        if request.user.rol != 'entrenador':
            return JsonResponse([], safe=False)
        
        # Obtener el equipo activo
        equipo_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            es_activo=True
        ).first()
        
        if not equipo_entrenador:
            return JsonResponse([], safe=False)
        
        equipo = equipo_entrenador.equipo
        partidos = Partido.objects.filter(
            equipo_local=equipo,
            finalizado=True
        ).order_by('-fecha_hora')[:10]  # Últimos 10 partidos finalizados
        
        datos = []
        for partido in partidos:
            rival = partido.equipo_visitante.nombre if partido.equipo_visitante else partido.nombre_equipo_visitante
            datos.append({
                'id': partido.id,
                'rival': rival,
                'fecha_hora': partido.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'estadio': partido.estadio_nombre,
            })
        
        return JsonResponse(datos, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)
