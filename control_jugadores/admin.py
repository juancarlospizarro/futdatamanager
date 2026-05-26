from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Lesion, Sancion, Aviso


@admin.register(Lesion)
class LesionAdmin(admin.ModelAdmin):
    list_display = [
        'jugador_nombre',
        'get_tipo_display',
        'fecha_inicio',
        'dias_duracion',
        'activa',
    ]
    list_filter = [
        'tipo',
        'activa',
        'fecha_inicio',
    ]
    search_fields = [
        'jugador__usuario__first_name',
        'jugador__usuario__last_name',
    ]
    readonly_fields = ['created_at', 'updated_at', 'fecha_inicio']
    
    fieldsets = (
        (_('Información del Jugador'), {
            'fields': ('jugador',)
        }),
        (_('Datos de la Lesión'), {
            'fields': ('tipo', 'fecha_inicio', 'dias_duracion', 'descripcion')
        }),
        (_('Estado'), {
            'fields': ('activa',)
        }),
        (_('Metadatos'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jugador_nombre(self, obj):
        return obj.jugador.usuario.get_full_name()
    jugador_nombre.short_description = _('Jugador')


@admin.register(Sancion)
class SancionAdmin(admin.ModelAdmin):
    list_display = [
        'jugador_nombre',
        'get_tipo_display',
        'fecha',
        'partidos_duracion',
        'activa',
    ]
    list_filter = [
        'tipo',
        'activa',
        'fecha',
    ]
    search_fields = [
        'jugador__usuario__first_name',
        'jugador__usuario__last_name',
        'razon',
    ]
    readonly_fields = ['created_at', 'updated_at', 'fecha']
    
    fieldsets = (
        (_('Información del Jugador'), {
            'fields': ('jugador',)
        }),
        (_('Datos de la Sanción'), {
            'fields': ('tipo', 'fecha', 'razon', 'partidos_duracion')
        }),
        (_('Estado'), {
            'fields': ('activa',)
        }),
        (_('Metadatos'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jugador_nombre(self, obj):
        return obj.jugador.usuario.get_full_name()
    jugador_nombre.short_description = _('Jugador')


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = [
        'jugador_nombre',
        'get_tipo_display',
        'fecha_envio',
        'leido',
        'enviado_email',
    ]
    list_filter = [
        'tipo',
        'leido',
        'enviado_email',
        'fecha_envio',
    ]
    search_fields = [
        'jugador__usuario__first_name',
        'jugador__usuario__last_name',
        'asunto',
    ]
    readonly_fields = ['created_at', 'updated_at', 'fecha_envio']
    
    fieldsets = (
        (_('Información del Jugador'), {
            'fields': ('jugador', 'sancion')
        }),
        (_('Contenido del Aviso'), {
            'fields': ('tipo', 'asunto', 'mensaje')
        }),
        (_('Estado de Envío'), {
            'fields': ('leido', 'enviado_email', 'fecha_envio')
        }),
        (_('Metadatos'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jugador_nombre(self, obj):
        return obj.jugador.usuario.get_full_name()
    jugador_nombre.short_description = _('Jugador')
