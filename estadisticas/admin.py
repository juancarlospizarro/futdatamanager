from django.contrib import admin
from django import forms
from .models import Estadistica


class EstadisticaForm(forms.ModelForm):
    """Formulario personalizado que muestra campos según la posición del jugador."""
    
    class Meta:
        model = Estadistica
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si hay un jugador seleccionado, ajustar los campos según su posición
        if self.instance.pk:
            posicion = self.instance.jugador.posicion
            
            # Portero: solo puede registrar paradas
            if posicion == 'portero':
                # Hacer readonly los campos que no aplican
                self.fields['goles'].widget.attrs['disabled'] = True
                self.fields['asistencias'].widget.attrs['disabled'] = True
                self.fields['tiros'].widget.attrs['disabled'] = True
                self.fields['pases'].widget.attrs['disabled'] = True
                self.fields['fueras_de_juego'].widget.attrs['disabled'] = True
                self.fields['faltas'].widget.attrs['disabled'] = True
                # Mostrar paradas normalmente
                self.fields['paradas'].widget.attrs['class'] = 'required'
                
            # Defensa: sin goles ni asistencias (normalmente)
            elif posicion in ['lateral_derecho', 'lateral_izquierdo', 'defensa_central']:
                self.fields['paradas'].widget.attrs['disabled'] = True
                self.fields['tiros'].widget.attrs['disabled'] = True
                
            # Delantero: enfoque en goles y asistencias
            elif posicion in ['delantero_centro', 'segundo_delantero']:
                self.fields['paradas'].widget.attrs['disabled'] = True
                self.fields['despejes'].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        posicion = self.instance.jugador.posicion if self.instance.pk else None
        
        if posicion == 'portero':
            # Un portero no debería tener goles
            if cleaned_data.get('goles', 0) > 0:
                raise forms.ValidationError("Un portero no puede marcar goles.")
                
        return cleaned_data


@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    """Admin para gestionar estadísticas de jugadores en partidos."""
    
    form = EstadisticaForm
    
    list_display = (
        'jugador_nombre',
        'partido_display',
        'posicion_jugador',
        'titular',
        'minutos_jugados',
        'goles',
        'asistencias',
        'despejes',
        'paradas',
        'tarjeta_roja'
    )
    
    list_filter = (
        'titular',
        'partido__fecha_hora',
        'tarjeta_roja',
        'created_at'
    )
    
    search_fields = (
        'jugador__usuario__first_name',
        'jugador__usuario__last_name',
        'partido__equipo_local__nombre',
    )
    
    fieldsets = (
        ('Identificación', {
            'fields': ('partido', 'jugador')
        }),
        ('Participación', {
            'fields': ('titular', 'minutos_jugados')
        }),
        ('Estadísticas Ofensivas', {
            'fields': ('goles', 'asistencias', 'tiros', 'pases', 'fueras_de_juego'),
            'description': 'Estadísticas de ataque y generación de juego'
        }),
        ('Estadísticas Defensivas', {
            'fields': ('paradas', 'despejes', 'faltas'),
            'description': 'Estadísticas de defensa (paradas solo para porteros)'
        }),
        ('Disciplina', {
            'fields': ('tarjetas_amarillas', 'tarjeta_roja')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def jugador_nombre(self, obj):
        return obj.jugador.usuario.get_full_name()
    jugador_nombre.short_description = 'Jugador'
    
    def posicion_jugador(self, obj):
        return obj.jugador.get_posicion_display() if obj.jugador.posicion else 'No asignada'
    posicion_jugador.short_description = 'Posición'
    
    def partido_display(self, obj):
        return f"{obj.partido.equipo_local.nombre} vs {obj.partido.get_equipo_visitante_nombre()}"
    partido_display.short_description = 'Partido'
