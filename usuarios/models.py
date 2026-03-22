from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende de AbstractUser.
    Sustituye al modelo auth.User por defecto de Django.
    """
    
    # Definimos los roles posibles
    class Rol(models.TextChoices):
        ADMIN = 'admin', _('Administrador')
        ENTRENADOR = 'entrenador', _('Entrenador')
        JUGADOR = 'jugador', _('Jugador')
        INVITADO = 'invitado', _('Invitado')

    # Campos adicionales comunes a todos los usuarios
    email = models.EmailField(_('dirección de correo electrónico'), unique=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'), blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    tiene_equipo = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    rol = models.CharField(
        max_length=20, 
        choices=Rol.choices, 
        default=Rol.INVITADO
    )

    # Usamos el email como identificador principal en lugar del username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"


class PerfilJugador(models.Model):
    """
    Datos específicos para usuarios con rol de JUGADOR.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_jugador'
    )
    
    altura = models.PositiveIntegerField(_('altura (cm)'), null=True, blank=True)
    peso = models.DecimalField(_('peso (kg)'), max_digits=5, decimal_places=2, null=True, blank=True)
    dorsal = models.PositiveIntegerField(_('dorsal'), null=True, blank=True)
    
    class PiernaHabil(models.TextChoices):
        DERECHA = 'derecha', _('Derecha')
        IZQUIERDA = 'izquierda', _('Izquierda')
        AMBAS = 'ambas', _('Ambas')
        
    pierna_habil = models.CharField(
        max_length=10, 
        choices=PiernaHabil.choices, 
        default=PiernaHabil.DERECHA
    )
    
    class Posicion(models.TextChoices):
        PORTERO = 'portero', _('Portero')
        LATERAL_DERECHO = 'lateral_derecho', _('Lateral Derecho')
        DEFENSA_CENTRAL = 'defensa_central', _('Defensa Central')
        LATERAL_IZQUIERDO = 'lateral_izquierdo', _('Lateral Izquierdo')
        MEDIOCENTRO_DEFENSIVO = 'mediocentro_defensivo', _('Mediocentro Defensivo')
        MEDIOCENTRO = 'mediocentro', _('Mediocentro')
        MEDIOCENTRO_OFENSIVO = 'mediocentro_ofensivo', _('Mediocentro Ofensivo')
        INTERIOR_IZQUIERDA = 'interior_izquierda', _('Interior Izquierda')
        INTERIOR_DERECHA = 'interior_derecha', _('Interior Derecha')
        EXTREMO_DERECHO = 'extremo_derecho', _('Extremo Derecho')
        EXTREMO_IZQUIERDO = 'extremo_izquierdo', _('Extremo Izquierdo')
        SEGUNDO_DELANTERO = 'segundo_delantero', _('Segundo Delantero')
        DELANTERO_CENTRO = 'delantero_centro', _('Delantero Centro')
    
    posicion = models.CharField(
        max_length=25,
        choices=Posicion.choices,
        null=True,
        blank=True,
        help_text="Posición en el equipo actual (asignada por el entrenador)"
    )
    
    es_capitan = models.BooleanField(_('es capitán'), default=False)

    def get_equipos_activos(self):
        """Devuelve solo los equipos donde el jugador está activo."""
        return self.equipos.filter(es_activo=True)

    def __str__(self):
        return f"Perfil Jugador: {self.usuario.get_full_name()}"


class PerfilEntrenador(models.Model):
    """
    Datos específicos para usuarios con rol de ENTRENADOR.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_entrenador'
    )
    
    licencia = models.CharField(_('número de licencia'), max_length=50, blank=True, null=True)
    experiencia_anos = models.PositiveIntegerField(_('años de experiencia'), default=0)

    def get_equipos_activos(self):
        """Devuelve solo los equipos donde el entrenador está activo."""
        return self.equipos.filter(es_activo=True)

    def __str__(self):
        return f"Perfil Entrenador: {self.usuario.get_full_name()}"