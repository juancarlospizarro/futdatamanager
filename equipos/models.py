from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from usuarios.models import PerfilJugador, PerfilEntrenador

class Equipo(models.Model):
    """
    Modelo que representa a un Equipo de Fútbol.
    Contiene información de identificación, colores, ubicación y fundación del equipo.
    """
    
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre del equipo"
    )

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    # Validador para asegurar que los colores sean códigos Hexadecimales (ej: #27a770)
    color_validator = RegexValidator(
        regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Introduce un código de color Hexadecimal válido (ej: #27a770)',
    )

    color_principal = models.CharField(
        max_length=7, 
        default="#27a770", 
        validators=[color_validator],
        verbose_name="Color Principal"
    )
    
    color_secundario = models.CharField(
        max_length=7, 
        default="#504847", 
        validators=[color_validator],
        verbose_name="Color Secundario"
    )
    
    direccion = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Dirección completa"
    )

    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Teléfono de contacto"
    )

    escudo = models.ImageField(
        upload_to='escudos_equipos/', 
        blank=True, 
        null=True, 
        verbose_name="Escudo"
    )
    
    anio_fundacion = models.PositiveIntegerField(
        verbose_name="Año de fundación",
        validators=[
            MinValueValidator(1850), 
            MaxValueValidator(timezone.now().year)
        ],
        help_text="Año en el que se fundó el club"
    )

    # Metadatos extra (opcional, pero recomendado)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EquipoJugador(models.Model):
    """
    Modelo de relación N:N entre Equipo y PerfilJugador.
    Permite que un jugador pertenezca a múltiples equipos y 
    que un equipo tenga múltiples jugadores.
    """
    equipo = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='jugadores'
    )
    
    perfil_jugador = models.ForeignKey(
        PerfilJugador, 
        on_delete=models.CASCADE, 
        related_name='equipos'
    )
    
    fecha_incorporacion = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de incorporación"
    )
    
    fecha_salida = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de salida"
    )
    
    es_activo = models.BooleanField(
        default=True,
        verbose_name="¿Está activo en el equipo?"
    )

    class Meta:
        verbose_name = "Equipo - Jugador"
        verbose_name_plural = "Equipos - Jugadores"
        ordering = ['-fecha_incorporacion', 'equipo', 'perfil_jugador']

    def __str__(self):
        return f"{self.perfil_jugador.usuario.get_full_name()} en {self.equipo.nombre}"


class EquipoEntrenador(models.Model):
    """
    Modelo de relación N:N entre Equipo y PerfilEntrenador.
    Permite que un entrenador dirija múltiples equipos y 
    que un equipo tenga múltiples entrenadores (técnico, asistente, etc.).
    """
    equipo = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='entrenadores'
    )
    
    perfil_entrenador = models.ForeignKey(
        PerfilEntrenador, 
        on_delete=models.CASCADE, 
        related_name='equipos'
    )
    
    fecha_incorporacion = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de incorporación"
    )
    
    fecha_salida = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de salida"
    )
    
    es_activo = models.BooleanField(
        default=True,
        verbose_name="¿Está activo en el equipo?"
    )

    class Meta:
        verbose_name = "Equipo - Entrenador"
        verbose_name_plural = "Equipos - Entrenadores"
        ordering = ['-fecha_incorporacion', 'equipo', 'perfil_entrenador']

    def __str__(self):
        return f"{self.perfil_entrenador.usuario.get_full_name()} en {self.equipo.nombre}"

