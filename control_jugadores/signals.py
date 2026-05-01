"""
Signals para control_jugadores
Automáticamente crea avisos y envía emails cuando se registra una sanción
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext as _
from django.urls import reverse
from .models import Sancion, Aviso


@receiver(post_save, sender=Sancion)
def crear_aviso_sancion(sender, instance, created, **kwargs):
    """
    Signal que se dispara cuando se crea una sanción.
    Automáticamente crea un aviso y envía un email al jugador.
    """
    if created and instance.activa:
        try:
            # Mapear tipo de sanción a tipo de aviso
            tipo_aviso = instance.tipo
            
            # Generar asunto y mensaje según el tipo de sanción
            asunto, mensaje = generar_contenido_aviso(instance)
            
            # Crear el aviso
            aviso = Aviso.objects.create(
                jugador=instance.jugador,
                sancion=instance,
                tipo=tipo_aviso,
                asunto=asunto,
                mensaje=mensaje
            )
            
            # Enviar email
            enviar_email_aviso(aviso)
            
        except Exception as e:
            print(f"Error al crear aviso de sanción: {str(e)}")


def generar_contenido_aviso(sancion):
    """
    Genera el asunto y mensaje del aviso según el tipo de sanción.
    """
    tipo_display = sancion.get_tipo_display()
    jugador_nombre = sancion.jugador.usuario.get_full_name()
    
    asunto = f"⚠️ Aviso de Sanción: {tipo_display}"
    
    # Crear mensaje personalizado según el tipo
    if sancion.tipo == 'amarilla':
        mensaje = f"""
        {jugador_nombre},
        
        Lamentamos informarte que has recibido una tarjeta amarilla en el partido.
        
        Detalles:
        - Tipo de sanción: {tipo_display}
        - Fecha: {sancion.fecha.strftime('%d/%m/%Y')}
        - Razón: {sancion.razon}
        
        Recuerda que la acumulación de 2 tarjetas amarillas resulta en una suspensión automática.
        
        Saludos,
        El equipo de FutDataManager
        """
    
    elif sancion.tipo == 'roja':
        mensaje = f"""
        {jugador_nombre},
        
        Lamentamos informarte que has recibido una tarjeta roja directa.
        
        Detalles:
        - Tipo de sanción: {tipo_display}
        - Fecha: {sancion.fecha.strftime('%d/%m/%Y')}
        - Razón: {sancion.razon}
        
        Esta es una falta grave que resultará en una suspensión automática.
        
        Saludos,
        El equipo de FutDataManager
        """
    
    elif sancion.tipo == 'suspension':
        mensaje = f"""
        {jugador_nombre},
        
        Te comunicamos que has sido suspendido por los siguientes partidos.
        
        Detalles:
        - Tipo de sanción: {tipo_display}
        - Partidos de suspensión: {sancion.partidos_duracion}
        - Fecha: {sancion.fecha.strftime('%d/%m/%Y')}
        - Razón: {sancion.razon}
        
        Durante este periodo no podrás participar en los partidos oficiales.
        
        Saludos,
        El equipo de FutDataManager
        """
    
    elif sancion.tipo == 'amonestacion':
        mensaje = f"""
        {jugador_nombre},
        
        Te informamos de que has recibido una amonestación disciplinaria.
        
        Detalles:
        - Tipo de sanción: {tipo_display}
        - Fecha: {sancion.fecha.strftime('%d/%m/%Y')}
        - Razón: {sancion.razon}
        
        Esta amonestación se registra en tu expediente disciplinario.
        
        Saludos,
        El equipo de FutDataManager
        """
    
    else:
        mensaje = f"""
        {jugador_nombre},
        
        Te informamos de una sanción registrada en tu perfil.
        
        Detalles:
        - Tipo de sanción: {tipo_display}
        - Fecha: {sancion.fecha.strftime('%d/%m/%Y')}
        - Razón: {sancion.razon}
        
        Si tienes alguna pregunta, contacta con tu entrenador.
        
        Saludos,
        El equipo de FutDataManager
        """
    
    return asunto, mensaje


def enviar_email_aviso(aviso):
    """
    Envía un email al jugador notificando sobre su sanción.
    Incluye un pixel de tracking invisible para detectar cuándo se abre el email.
    """
    try:
        # Obtener email del jugador
        email_jugador = aviso.jugador.usuario.email
        
        if not email_jugador:
            print(f"El jugador {aviso.jugador.usuario.get_full_name()} no tiene email registrado")
            return False
        
        # Crear el mensaje HTML sin pixel tracking
        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #27a770;">⚠️ Aviso de Sanción</h2>
                
                <p><strong>Hola {aviso.jugador.usuario.get_full_name()},</strong></p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #27a770; margin: 20px 0;">
                    <p style="margin: 0;">{aviso.mensaje.replace(chr(10), '<br>')}</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999;">
                    Este es un mensaje automático de FutDataManager. Por favor no respondas a este correo.
                </p>
            </body>
        </html>
        """
        
        # Usar EmailMultiAlternatives para enviar HTML + texto plano
        from django.core.mail import EmailMultiAlternatives
        
        msg = EmailMultiAlternatives(
            subject=aviso.asunto,
            body=aviso.mensaje,  # Versión texto plano
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_jugador]
        )
        
        # Adjuntar versión HTML
        msg.attach_alternative(mensaje_html, "text/html")
        
        # Enviar
        msg.send(fail_silently=False)
        
        # Marcar como enviado
        aviso.enviado_email = True
        aviso.save()
        
        print(f"Email de sanción enviado a {email_jugador} (Token: {token[:10]}...)")
        return True
        
    except Exception as e:
        print(f"Error al enviar email de aviso: {str(e)}")
        return False
