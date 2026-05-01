from django.db import models
from django.utils.translation import gettext_lazy as _
from usuarios.models import PerfilJugador


class Lesion(models.Model):
    """Modelo para registrar lesiones de jugadores"""
    
    class TipoLesion(models.TextChoices):
        MUSCULAR = 'muscular', _('Lesión muscular')
        FRACTURA = 'fractura', _('Fractura')
        DISTENSION = 'distension', _('Distensión')
        CONTUSION = 'contusion', _('Contusión')
        ESGUINCE = 'esguince', _('Esguince')
        OTRA = 'otra', _('Otra')
    
    jugador = models.ForeignKey(
        PerfilJugador,
        on_delete=models.CASCADE,
        related_name='lesiones',
        verbose_name=_('Jugador')
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoLesion.choices,
        verbose_name=_('Tipo de lesión')
    )
    
    dias_duracion = models.PositiveIntegerField(
        verbose_name=_('Duración estimada (días)')
    )
    
    fecha_inicio = models.DateField(
        auto_now_add=True,
        verbose_name=_('Fecha de lesión')
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Lesión activa')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Lesión')
        verbose_name_plural = _('Lesiones')
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.jugador.usuario.get_full_name()} - {self.get_tipo_display()}"


class Sancion(models.Model):
    """Modelo para registrar sanciones disciplinarias"""
    
    class TipoSancion(models.TextChoices):
        TARJETA_AMARILLA = 'amarilla', _('Tarjeta amarilla')
        TARJETA_ROJA = 'roja', _('Tarjeta roja')
        SUSPENSION = 'suspension', _('Suspensión')
        AMONESTACION = 'amonestacion', _('Amonestación')
    
    jugador = models.ForeignKey(
        PerfilJugador,
        on_delete=models.CASCADE,
        related_name='sanciones',
        verbose_name=_('Jugador')
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoSancion.choices,
        verbose_name=_('Tipo de sanción')
    )
    
    partidos_duracion = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Partidos de suspensión')
    )
    
    razon = models.TextField(
        verbose_name=_('Razón de la sanción')
    )
    
    fecha = models.DateField(
        auto_now_add=True,
        verbose_name=_('Fecha de sanción')
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Sanción activa')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Sanción')
        verbose_name_plural = _('Sanciones')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.jugador.usuario.get_full_name()} - {self.get_tipo_display()}"


class Aviso(models.Model):
    """Modelo para registrar avisos/notificaciones de sanciones a jugadores"""
    
    class TipoAviso(models.TextChoices):
        TARJETA_AMARILLA = 'amarilla', _('Tarjeta amarilla')
        TARJETA_ROJA = 'roja', _('Tarjeta roja')
        SUSPENSION = 'suspension', _('Suspensión')
        AMONESTACION = 'amonestacion', _('Amonestación')
        ACUMULACION = 'acumulacion', _('Acumulación de tarjetas')
    
    jugador = models.ForeignKey(
        PerfilJugador,
        on_delete=models.CASCADE,
        related_name='avisos',
        verbose_name=_('Jugador')
    )
    
    sancion = models.ForeignKey(
        Sancion,
        on_delete=models.CASCADE,
        related_name='avisos',
        verbose_name=_('Sanción asociada'),
        null=True,
        blank=True
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoAviso.choices,
        verbose_name=_('Tipo de aviso')
    )
    
    asunto = models.CharField(
        max_length=200,
        verbose_name=_('Asunto del aviso')
    )
    
    mensaje = models.TextField(
        verbose_name=_('Mensaje del aviso')
    )
    
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de envío')
    )
    
    leido = models.BooleanField(
        default=False,
        verbose_name=_('Leído')
    )
    
    enviado_email = models.BooleanField(
        default=False,
        verbose_name=_('Email enviado')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Aviso')
        verbose_name_plural = _('Avisos')
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.jugador.usuario.get_full_name()} - {self.asunto}"
