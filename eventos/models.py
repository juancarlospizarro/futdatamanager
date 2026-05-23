from django.db import models
from django.utils.translation import gettext_lazy as _
from equipos.models import Equipo


class Competicion(models.Model):
    """Modelo para representar competiciones (ligas, copas, torneos, etc.)"""
    
    class TipoCompeticion(models.TextChoices):
        LIGA = 'liga', _('Liga')
        COPA = 'copa', _('Copa')
        AMISTOSO = 'amistoso', _('Amistoso')
        TORNEO = 'torneo', _('Torneo')
        SUPERCOPA = 'supercopa', _('Supercopa')
    
    nombre = models.CharField(
        max_length=200,
        verbose_name=_('Nombre de la competición'),
        help_text=_('Ej: Liga Local 2024-2025')
    )
    
    ano = models.PositiveIntegerField(
        verbose_name=_('Año/Temporada'),
        help_text=_('Año de inicio de la temporada')
    )
    
    tipo = models.CharField(
        max_length=15,
        choices=TipoCompeticion.choices,
        default=TipoCompeticion.LIGA,
        verbose_name=_('Tipo de competición')
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    
    fecha_inicio = models.DateField(
        verbose_name=_('Fecha de inicio'),
        null=True,
        blank=True
    )
    
    fecha_fin = models.DateField(
        verbose_name=_('Fecha de fin'),
        null=True,
        blank=True
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Competición activa')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Competición')
        verbose_name_plural = _('Competiciones')
        ordering = ['-ano', 'nombre']
        indexes = [
            models.Index(fields=['ano', 'tipo']),
        ]
        unique_together = ['nombre', 'ano', 'tipo']
    
    def __str__(self):
        return f"{self.nombre} ({self.ano})"


class Partido(models.Model):
    """Modelo para registrar partidos de fútbol."""
    
    competicion = models.ForeignKey(
        Competicion,
        on_delete=models.CASCADE,
        related_name='partidos',
        verbose_name=_("Competición"),
        null=True,
        blank=True
    )
    
    equipo_local = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_local',
        verbose_name=_("Equipo local")
    )
    
    equipo_visitante = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partidos_visitante',
        verbose_name=_("Equipo visitante (BD)")
    )
    
    nombre_equipo_visitante = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Nombre equipo visitante (manual)")
    )
    
    estadio_nombre = models.CharField(
        max_length=150,
        verbose_name=_("Nombre del estadio")
    )
    
    estadio_direccion = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Dirección del estadio")
    )
    
    fecha_hora = models.DateTimeField(
        verbose_name=_("Fecha y hora de inicio")
    )
    
    posesion_local = models.IntegerField(
        default=0,
        help_text=_("Porcentaje de posesión del equipo local"),
        verbose_name=_("Posesión local (%)")
    )
    
    posesion_visitante = models.IntegerField(
        default=0,
        help_text=_("Porcentaje de posesión del equipo visitante"),
        verbose_name=_("Posesión visitante (%)")
    )
    
    finalizado = models.BooleanField(
        default=False,
        verbose_name=_("Partido finalizado")
    )
    
    goles_local = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Goles equipo local")
    )
    
    goles_visitante = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Goles equipo visitante")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = _("Partido")
        verbose_name_plural = _("Partidos")
        indexes = [
            models.Index(fields=['equipo_local', 'fecha_hora']),
            models.Index(fields=['fecha_hora']),
        ]
    
    def __str__(self):
        equipo_visitante_nombre = self.equipo_visitante.nombre if self.equipo_visitante else self.nombre_equipo_visitante
        return f"{self.equipo_local.nombre} vs {equipo_visitante_nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def get_equipo_visitante_nombre(self):
        """Retorna el nombre del equipo visitante (de BD o manual)"""
        return self.equipo_visitante.nombre if self.equipo_visitante else self.nombre_equipo_visitante


class Entrenamiento(models.Model):
    """Modelo para registrar entrenamientos."""
    
    TIPO_CHOICES = [
        ('fuerza', _("Fuerza")),
        ('tactico', _("Táctico")),
        ('ataque', _("Ataque")),
        ('defensa', _("Defensa")),
        ('recuperacion', _("Recuperación")),
    ]
    
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='entrenamientos',
        verbose_name=_("Equipo")
    )
    
    fecha_hora = models.DateTimeField(
        verbose_name=_("Fecha y hora de inicio")
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name=_("Tipo de entrenamiento")
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_("Descripción")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = _("Entrenamiento")
        verbose_name_plural = _("Entrenamientos")
        indexes = [
            models.Index(fields=['equipo', 'fecha_hora']),
            models.Index(fields=['fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.equipo.nombre} - {self.get_tipo_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
