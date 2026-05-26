from django.apps import AppConfig


class ControlJugadoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control_jugadores'
    
    def ready(self):
        """
        Conectar signals cuando la app está lista.
        Las signals crean avisos automáticamente cuando se registran sanciones.
        """
        import control_jugadores.signals  # noqa
