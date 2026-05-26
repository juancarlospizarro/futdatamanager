from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from usuarios.models import PerfilJugador
from eventos.models import Partido


class Estadistica(models.Model):
    """
    Modelo de entidad débil que almacena las estadísticas de un jugador en un partido específico.
    Depende de Partido y PerfilJugador para su identificación única.
    
    Relaciones identificadoras:
    - se recogen: PerfilJugador 1:N Estadistica
    - pertenecen: Partido 1:N Estadistica
    """
    
    # Claves foráneas identificadoras (entidad débil)
    partido = models.ForeignKey(
        Partido,
        on_delete=models.CASCADE,
        related_name='estadisticas',
        verbose_name=_('Partido')
    )
    
    jugador = models.ForeignKey(
        PerfilJugador,
        on_delete=models.CASCADE,
        related_name='estadisticas',
        verbose_name=_('Jugador')
    )
    
    # Atributos de participación
    titular = models.BooleanField(
        default=False,
        verbose_name=_('¿Fue titular?')
    )
    
    minutos_jugados = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Minutos jugados'),
        help_text=_('Minutos que jugó en el partido')
    )
    
    # Estadísticas ofensivas
    goles = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Goles')
    )
    
    asistencias = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Asistencias')
    )
    
    tiros = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tiros a puerta'),
        help_text=_('Tiros que fueron a puerta')
    )
    
    pases = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Pases completados')
    )
    
    fueras_de_juego = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Fueras de juego')
    )
    
    # Estadísticas defensivas
    paradas = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Paradas'),
        help_text=_('Solo para porteros')
    )
    
    despejes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Despejes')
    )
    
    faltas = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Faltas cometidas')
    )
    
    # Tarjetas
    tarjetas_amarillas = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tarjetas amarillas'),
        validators=[MaxValueValidator(2)]
    )
    
    tarjeta_roja = models.BooleanField(
        default=False,
        verbose_name=_('¿Recibió tarjeta roja?')
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Estadística')
        verbose_name_plural = _('Estadísticas')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['partido', 'jugador']),
            models.Index(fields=['jugador', '-created_at']),
        ]
        unique_together = ['partido', 'jugador']
        constraints = [
            models.UniqueConstraint(
                fields=['partido', 'jugador'],
                name='estadistica_unica_por_jugador_partido'
            )
        ]
    
    def __str__(self):
        return f"{self.jugador.usuario.get_full_name()} - {self.partido.equipo_local.nombre} vs {self.partido.get_equipo_visitante_nombre()}"
