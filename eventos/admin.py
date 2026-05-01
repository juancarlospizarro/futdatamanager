from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Partido, Entrenamiento, Competicion


@admin.register(Competicion)
class CompeticionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'ano',
        'tipo',
        'activa',
        'get_num_partidos',
    ]
    list_filter = [
        'tipo',
        'ano',
        'activa',
    ]
    search_fields = [
        'nombre',
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_("Información básica"), {
            'fields': ('nombre', 'ano', 'tipo', 'activa')
        }),
        (_("Descripción"), {
            'fields': ('descripcion',),
        }),
        (_("Fechas"), {
            'fields': ('fecha_inicio', 'fecha_fin'),
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_num_partidos(self, obj):
        return obj.partidos.count()
    get_num_partidos.short_description = _("Nº Partidos")


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = [
        'competicion',
        'equipo_local',
        'get_equipo_visitante',
        'estadio_nombre',
        'fecha_hora',
        'finalizado',
    ]
    list_filter = [
        'competicion',
        'finalizado',
        'fecha_hora',
        'equipo_local',
    ]
    search_fields = [
        'equipo_local__nombre',
        'equipo_visitante__nombre',
        'nombre_equipo_visitante',
        'estadio_nombre',
        'competicion__nombre',
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    # Usar autocomplete_fields para competicion (dropdown más eficiente)
    autocomplete_fields = ['competicion']
    
    fieldsets = (
        (_("Competición (OBLIGATORIO)"), {
            'fields': ('competicion',),
            'description': _("Selecciona la competición a la que pertenece este partido")
        }),
        (_("Información del Partido"), {
            'fields': ('equipo_local', 'fecha_hora', 'finalizado')
        }),
        (_("Equipo Visitante"), {
            'fields': ('equipo_visitante', 'nombre_equipo_visitante'),
            'description': _("Selecciona un equipo de la BD o introduce su nombre manualmente")
        }),
        (_("Estadio"), {
            'fields': ('estadio_nombre', 'estadio_direccion')
        }),
        (_("Estadísticas"), {
            'fields': ('posesion_local', 'posesion_visitante')
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_equipo_visitante(self, obj):
        return obj.get_equipo_visitante_nombre()
    get_equipo_visitante.short_description = _("Equipo Visitante")


@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = [
        'equipo',
        'get_tipo_display',
        'fecha_hora',
    ]
    list_filter = [
        'tipo',
        'fecha_hora',
        'equipo',
    ]
    search_fields = [
        'equipo__nombre',
        'descripcion',
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_("Información"), {
            'fields': ('equipo', 'fecha_hora', 'tipo')
        }),
        (_("Descripción"), {
            'fields': ('descripcion',),
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
