from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from usuarios.decorators import entrenador_o_admin_required
from usuarios.models import PerfilJugador, Usuario, PerfilEntrenador
from .models import Equipo, EquipoEntrenador, EquipoJugador
from control_jugadores.models import Lesion, Sancion

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
        equipo.save()

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
    Cuando el entrenador abandona el equipo:
    1. Se marcan como inactivos (is_active=False) todos los jugadores del equipo
    2. Se marcan como inactivos (is_active=False) todos los entrenadores del equipo
    3. Se elimina el equipo de la base de datos
    4. Se envía email a todos los jugadores y entrenadores notificando el cambio
    """
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('landing')
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Seguridad: Solo un entrenador activo del equipo puede abandonarlo
    try:
        es_entrenador = EquipoEntrenador.objects.filter(
            perfil_entrenador=request.user.perfil_entrenador,
            equipo=equipo,
            es_activo=True
        ).exists()
        
        if not es_entrenador:
            messages.error(request, "No tienes permiso para abandonar este equipo.")
            return redirect('landing')
    except:
        messages.error(request, "Error al verificar permisos.")
        return redirect('landing')
    
    try:
        # Recopilar información de jugadores y entrenadores ANTES de eliminar
        jugadores_activos = equipo.jugadores.filter(es_activo=True).select_related(
            'perfil_jugador__usuario'
        )
        entrenadores_activos = equipo.entrenadores.filter(es_activo=True).select_related(
            'perfil_entrenador__usuario'
        )
        
        # Recopilar emails y nombres de jugadores
        emails_jugadores = []
        nombres_jugadores = []
        for relacion_jugador in jugadores_activos:
            usuario = relacion_jugador.perfil_jugador.usuario
            if usuario.email:
                emails_jugadores.append(usuario.email)
                nombres_jugadores.append(usuario.get_full_name())
        
        # Recopilar emails y nombres de entrenadores
        emails_entrenadores = []
        nombres_entrenadores = []
        for relacion_entrenador in entrenadores_activos:
            usuario = relacion_entrenador.perfil_entrenador.usuario
            if usuario.email:
                emails_entrenadores.append(usuario.email)
                nombres_entrenadores.append(usuario.get_full_name())
        
        # Guardar nombre del equipo
        equipo_nombre = equipo.nombre
        
        with transaction.atomic():
            # Marcar como inactivos todos los usuarios de los jugadores
            for relacion_jugador in jugadores_activos:
                usuario_jugador = relacion_jugador.perfil_jugador.usuario
                usuario_jugador.tiene_equipo = False
                usuario_jugador.save()
            
            # Marcar como inactivos todos los usuarios de los entrenadores
            for relacion_entrenador in entrenadores_activos:
                usuario_entrenador = relacion_entrenador.perfil_entrenador.usuario
                usuario_entrenador.tiene_equipo = False
                usuario_entrenador.save()
            
            # Eliminar el equipo (esto cascada borra EquipoJugador y EquipoEntrenador)
            equipo.delete()
        
        # Enviar emails después de la transacción completada
        _enviar_emails_abandono_equipo(equipo_nombre, emails_jugadores, emails_entrenadores)
        
        messages.success(request, f"Has abandonado el equipo '{equipo_nombre}'. El equipo ha sido eliminado y todos sus miembros desactivados.")
        return redirect('landing')
    
    except Exception as e:
        messages.error(request, f"Error al abandonar el equipo: {str(e)}")
        return redirect('landing')


def _enviar_emails_abandono_equipo(equipo_nombre, emails_jugadores, emails_entrenadores):
    """
    Función auxiliar para enviar emails a jugadores y entrenadores
    cuando el equipo es abandonado.
    """
    try:
        # Todos los emails a notificar
        todos_emails = emails_jugadores + emails_entrenadores
        
        if not todos_emails:
            return
        
        subject = f'Notificación: El equipo {equipo_nombre} ha sido eliminado'
        
        # Crear contenido HTML para el email
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <h2 style="color: #dc3545;">⚠️ Notificación importante</h2>
                    <p>Estimado/a usuario,</p>
                    <p>
                        Le informamos que el equipo <strong>{equipo_nombre}</strong> ha sido eliminado
                        y todas las relaciones con los miembros del equipo han sido desactivadas.
                    </p>
                    <p>
                        En este momento, <strong>usted no tiene equipo asignado</strong> en nuestro sistema.
                        Si esto es un error o desea unirse a otro equipo, por favor contacte con un administrador.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Este es un mensaje automático. Por favor, no responda a este correo.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Crear versión de texto plano
        text_message = f"""
Notificación importante

Estimado/a usuario,

Le informamos que el equipo {equipo_nombre} ha sido eliminado
y todas las relaciones con los miembros del equipo han sido desactivadas.

En este momento, usted no tiene equipo asignado en nuestro sistema.
Si esto es un error o desea unirse a otro equipo, por favor contacte con un administrador.

Este es un mensaje automático. Por favor, no responda a este correo.
        """
        
        # Enviar email a todos
        send_mail(
            subject=subject,
            message=text_message,
            from_email=None,  # Usa DEFAULT_FROM_EMAIL de settings
            recipient_list=todos_emails,
            html_message=html_message,
            fail_silently=True  # No lanzar excepción si falla el envío
        )
    
    except Exception as e:
        # Log del error pero no interrumpir el flujo principal
        print(f"Error al enviar emails de abandono de equipo: {str(e)}")


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

@login_required
def agregar_lesion(request):
    """
    AJAX endpoint para registrar una lesión de un jugador.
    Solo el entrenador del equipo del jugador puede registrar lesiones.
    Espera JSON con: jugador_id, tipo, dias_duracion, descripcion, activa
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            jugador_id = data.get('jugador_id')
            tipo = data.get('tipo')
            dias_duracion = data.get('dias_duracion')
            descripcion = data.get('descripcion', '')
            activa = bool(data.get('activa', True))
            
            # Validaciones
            if not jugador_id or not tipo or not dias_duracion:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos obligatorios'
                }, status=400)
            
            # Obtener el perfil del jugador
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
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permiso para registrar lesiones de este jugador'
                }, status=403)
            
            # Validar tipo de lesión
            tipos_validos = ['muscular', 'fractura', 'distension', 'contusion', 'esguince', 'otra']
            if tipo not in tipos_validos:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de lesión inválido'
                }, status=400)
            
            # Validar duración
            dias = int(dias_duracion)
            if dias < 1 or dias > 365:
                return JsonResponse({
                    'success': False,
                    'message': 'La duración debe estar entre 1 y 365 días'
                }, status=400)
            
            # Crear la lesión
            lesion = Lesion.objects.create(
                jugador=perfil_jugador,
                tipo=tipo,
                dias_duracion=dias,
                descripcion=descripcion,
                activa=activa
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Lesión registrada para {perfil_jugador.usuario.get_full_name()}',
                'lesion_id': lesion.id
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required
def agregar_sancion(request):
    """
    AJAX endpoint para registrar una sanción de un jugador.
    Solo el entrenador del equipo del jugador puede registrar sanciones.
    Espera JSON con: jugador_id, tipo, razon, partidos_duracion, activa
    Los signals automáticamente crearán el aviso y enviarán email.
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            jugador_id = data.get('jugador_id')
            tipo = data.get('tipo')
            razon = data.get('razon')
            partidos_duracion = data.get('partidos_duracion', 0)
            activa = bool(data.get('activa', True))
            
            # Validaciones
            if not jugador_id or not tipo or not razon:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos obligatorios'
                }, status=400)
            
            # Obtener el perfil del jugador
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
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permiso para registrar sanciones de este jugador'
                }, status=403)
            
            # Validar tipo de sanción
            tipos_validos = ['amarilla', 'roja', 'suspension', 'amonestacion']
            if tipo not in tipos_validos:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de sanción inválido'
                }, status=400)
            
            # Validar duración
            try:
                partidos = int(partidos_duracion) if partidos_duracion else 0
                if partidos < 0 or partidos > 99:
                    return JsonResponse({
                        'success': False,
                        'message': 'Los partidos de duración deben estar entre 0 y 99'
                    }, status=400)
            except ValueError:
                partidos = 0
            
            # Crear la sanción
            sancion = Sancion.objects.create(
                jugador=perfil_jugador,
                tipo=tipo,
                razon=razon,
                partidos_duracion=partidos,
                activa=activa
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Sanción registrada para {perfil_jugador.usuario.get_full_name()}. Email enviado automáticamente.',
                'sancion_id': sancion.id
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
