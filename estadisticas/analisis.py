"""
Módulo de análisis de estadísticas de jugadores.
Calcula valoraciones basadas en posición y estadísticas.
"""

import pandas as pd
from django.db.models import Q, Sum, Count, Avg
from estadisticas.models import Estadistica
from usuarios.models import PerfilJugador
from eventos.models import Partido


def calcular_valoracion_jugador(jugador_id, equipo_id):
    """
    Calcula la valoración de un jugador (0-10) basada en sus estadísticas
    y su posición en el campo.
    
    Args:
        jugador_id: ID del PerfilJugador
        equipo_id: ID del Equipo del entrenador
        
    Returns:
        float: Valoración de 0 a 10 con dos decimales
    """
    try:
        jugador = PerfilJugador.objects.get(id=jugador_id)
        posicion = jugador.posicion
        
        # Obtener estadísticas del jugador en partidos finalizados del equipo
        estadisticas = Estadistica.objects.filter(
            jugador=jugador,
            partido__equipo_local_id=equipo_id,
            partido__finalizado=True
        ).aggregate(
            goles=Sum('goles'),
            asistencias=Sum('asistencias'),
            tiros=Sum('tiros'),
            pases=Sum('pases'),
            despejes=Sum('despejes'),
            paradas=Sum('paradas'),
            faltas=Sum('faltas'),
            tarjetas_amarillas=Sum('tarjetas_amarillas'),
            tarjeta_roja=Count('id', filter=Q(tarjeta_roja=True)),  # Contar cuántas veces True
            fueras_de_juego=Sum('fueras_de_juego'),
            minutos_jugados=Sum('minutos_jugados'),
            partidos=Count('id')
        )
        
        # Usar 1 como mínimo para evitar división por cero
        partidos = max(estadisticas['partidos'] or 0, 1)
        
        # Convertir valores None a 0
        for key in estadisticas:
            if estadisticas[key] is None:
                estadisticas[key] = 0
        
        # Calcular promedios por partido
        promedios = {
            'goles': estadisticas['goles'] / partidos,
            'asistencias': estadisticas['asistencias'] / partidos,
            'tiros': estadisticas['tiros'] / partidos,
            'pases': estadisticas['pases'] / partidos,
            'despejes': estadisticas['despejes'] / partidos,
            'paradas': estadisticas['paradas'] / partidos,
            'faltas': estadisticas['faltas'] / partidos,
            'tarjetas_amarillas': estadisticas['tarjetas_amarillas'] / partidos,
            'tarjeta_roja': estadisticas['tarjeta_roja'],  # Total, no promedio
            'fueras_de_juego': estadisticas['fueras_de_juego'] / partidos,
            'minutos_jugados': estadisticas['minutos_jugados'] / partidos if estadisticas['minutos_jugados'] else 0
        }
        
        # Aplicar sistema de puntuación según posición
        if posicion == 'portero':
            valoracion = _calcular_valoracion_portero(promedios)
        elif posicion in ['lateral_derecho', 'lateral_izquierdo', 'defensa_central']:
            valoracion = _calcular_valoracion_defensa(promedios)
        elif posicion in ['mediocentro_defensivo', 'mediocentro', 'mediocentro_ofensivo']:
            valoracion = _calcular_valoracion_centrocampista(promedios)
        elif posicion in ['interior_izquierda', 'interior_derecha', 'extremo_derecho', 'extremo_izquierdo', 'segundo_delantero']:
            valoracion = _calcular_valoracion_extremo(promedios)
        elif posicion == 'delantero_centro':
            valoracion = _calcular_valoracion_delantero(promedios)
        else:
            # Posición desconocida, usar promedio general
            valoracion = _calcular_valoracion_general(promedios)
        
        return round(valoracion, 2)
    
    except PerfilJugador.DoesNotExist:
        return 0.0


def _calcular_valoracion_portero(promedios):
    """Valoración para porteros."""
    puntuacion = 0.0
    
    # Paradas (máximo esperado: 5 por partido = 10 puntos)
    puntuacion += min((promedios['paradas'] / 5) * 10, 10) * 0.30
    
    # Despejes (máximo esperado: 8 por partido = 10 puntos)
    puntuacion += min((promedios['despejes'] / 8) * 10, 10) * 0.25
    
    # Pocas faltas (máximo = 0, si tiene faltas resta)
    faltas_penalty = max(0, 10 - (promedios['faltas'] * 5))
    puntuacion += faltas_penalty * 0.15
    
    # Sin tarjetas (cada tarjeta amarilla resta, roja resta más)
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.20
    
    # Juego con los pies (pases, mínimo 20 por partido)
    pases_bonus = min((promedios['pases'] / 20) * 10, 10) * 0.10
    puntuacion += pases_bonus
    
    return min(puntuacion, 10.0)


def _calcular_valoracion_defensa(promedios):
    """Valoración para defensas (centrales y laterales)."""
    puntuacion = 0.0
    
    # Despejes (máximo esperado: 6 por partido = 10 puntos)
    puntuacion += min((promedios['despejes'] / 6) * 10, 10) * 0.25
    
    # Paradas/Intercepciones (máximo: 4 por partido)
    puntuacion += min((promedios['paradas'] / 4) * 10, 10) * 0.20
    
    # Pocas faltas (máximo = 0, si tiene muchas resta)
    faltas_penalty = max(0, 10 - (promedios['faltas'] * 3))
    puntuacion += faltas_penalty * 0.15
    
    # Sin tarjetas
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.15
    
    # Pocos fueras de juego (máximo = 0)
    fuera_juego_penalty = max(0, 10 - (promedios['fueras_de_juego'] * 5))
    puntuacion += fuera_juego_penalty * 0.10
    
    # Algunos pases (mínimo 30 por partido)
    pases_bonus = min((promedios['pases'] / 30) * 10, 10) * 0.15
    puntuacion += pases_bonus
    
    return min(puntuacion, 10.0)


def _calcular_valoracion_centrocampista(promedios):
    """Valoración para centrocampistas."""
    puntuacion = 0.0
    
    # Pases (máximo: 60 por partido = 10 puntos)
    puntuacion += min((promedios['pases'] / 60) * 10, 10) * 0.35
    
    # Asistencias (máximo: 2 por partido = 10 puntos)
    puntuacion += min((promedios['asistencias'] / 2) * 10, 10) * 0.20
    
    # Goles (máximo: 1 por partido = 10 puntos)
    puntuacion += min((promedios['goles'] / 1) * 10, 10) * 0.15
    
    # Pocas faltas
    faltas_penalty = max(0, 10 - (promedios['faltas'] * 3))
    puntuacion += faltas_penalty * 0.15
    
    # Sin tarjetas
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.10
    
    # Pocos fueras de juego
    fuera_juego_penalty = max(0, 10 - (promedios['fueras_de_juego'] * 3))
    puntuacion += fuera_juego_penalty * 0.05
    
    return min(puntuacion, 10.0)


def _calcular_valoracion_extremo(promedios):
    """Valoración para extremos e interiores."""
    puntuacion = 0.0
    
    # Goles (máximo: 1.5 por partido = 10 puntos)
    puntuacion += min((promedios['goles'] / 1.5) * 10, 10) * 0.30
    
    # Asistencias (máximo: 1 por partido = 10 puntos)
    puntuacion += min((promedios['asistencias'] / 1) * 10, 10) * 0.25
    
    # Tiros (máximo: 4 por partido = 10 puntos)
    puntuacion += min((promedios['tiros'] / 4) * 10, 10) * 0.20
    
    # Pases (mínimo: 30 por partido)
    pases_bonus = min((promedios['pases'] / 30) * 10, 10) * 0.10
    puntuacion += pases_bonus
    
    # Pocas faltas
    faltas_penalty = max(0, 10 - (promedios['faltas'] * 3))
    puntuacion += faltas_penalty * 0.10
    
    # Sin tarjetas
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.05
    
    return min(puntuacion, 10.0)


def _calcular_valoracion_delantero(promedios):
    """Valoración para delanteros centro."""
    puntuacion = 0.0
    
    # Goles (máximo: 1.5 por partido = 10 puntos)
    puntuacion += min((promedios['goles'] / 1.5) * 10, 10) * 0.40
    
    # Asistencias (máximo: 0.5 por partido = 10 puntos)
    puntuacion += min((promedios['asistencias'] / 0.5) * 10, 10) * 0.20
    
    # Tiros (máximo: 4 por partido = 10 puntos)
    puntuacion += min((promedios['tiros'] / 4) * 10, 10) * 0.20
    
    # Pocas faltas
    faltas_penalty = max(0, 10 - (promedios['faltas'] * 3))
    puntuacion += faltas_penalty * 0.10
    
    # Sin tarjetas
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.05
    
    # Pocos fueras de juego
    fuera_juego_penalty = max(0, 10 - (promedios['fueras_de_juego'] * 2))
    puntuacion += fuera_juego_penalty * 0.05
    
    return min(puntuacion, 10.0)


def _calcular_valoracion_general(promedios):
    """Valoración general para posiciones desconocidas."""
    puntuacion = 0.0
    
    # Goles
    puntuacion += min((promedios['goles'] / 1) * 10, 10) * 0.25
    
    # Asistencias
    puntuacion += min((promedios['asistencias'] / 1) * 10, 10) * 0.20
    
    # Despejes
    puntuacion += min((promedios['despejes'] / 4) * 10, 10) * 0.20
    
    # Pases
    puntuacion += min((promedios['pases'] / 40) * 10, 10) * 0.20
    
    # Sin tarjetas
    tarjetas_penalty = max(0, 10 - (promedios['tarjetas_amarillas'] * 2) - (promedios['tarjeta_roja'] * 5))
    puntuacion += tarjetas_penalty * 0.15
    
    return min(puntuacion, 10.0)


def obtener_jugadores_en_forma(equipo_id, limite=5):
    """
    Obtiene los mejores jugadores según su valoración usando pandas.
    
    Args:
        equipo_id: ID del Equipo
        limite: Cantidad de jugadores a devolver (por defecto 5)
        
    Returns:
        list: Lista de diccionarios con info del jugador y su valoración
    """
    from equipos.models import EquipoJugador
    
    # Obtener jugadores activos del equipo
    jugadores_ids = list(EquipoJugador.objects.filter(
        equipo_id=equipo_id,
        es_activo=True
    ).values_list('perfil_jugador_id', flat=True))
    
    if not jugadores_ids:
        return []
    
    # Calcular valoración para cada jugador
    jugadores_valorados = []
    
    for jugador_id in jugadores_ids:
        valoracion = calcular_valoracion_jugador(jugador_id, equipo_id)
        jugador = PerfilJugador.objects.get(id=jugador_id)
        
        jugadores_valorados.append({
            'id': jugador_id,
            'nombre': jugador.usuario.get_full_name(),
            'posicion': jugador.get_posicion_display() if jugador.posicion else 'N/A',
            'posicion_clave': jugador.posicion if jugador.posicion else '',
            'dorsal': jugador.dorsal,
            'valoracion': valoracion
        })
    
    # Convertir a DataFrame para operaciones vectorizadas
    df = pd.DataFrame(jugadores_valorados)
    
    # Ordenar por valoración descendente
    df_ordenado = df.sort_values('valoracion', ascending=False)
    
    # Convertir de vuelta a lista de dicts
    resultado = df_ordenado.head(limite).to_dict('records')
    
    return resultado


def obtener_jugadores_pobre_forma(equipo_id, limite=5):
    """
    Obtiene los peores jugadores según su valoración usando pandas.
    
    Args:
        equipo_id: ID del Equipo
        limite: Cantidad de jugadores a devolver (por defecto 5)
        
    Returns:
        list: Lista de diccionarios con info del jugador y su valoración
    """
    from equipos.models import EquipoJugador
    
    # Obtener jugadores activos del equipo
    jugadores_ids = list(EquipoJugador.objects.filter(
        equipo_id=equipo_id,
        es_activo=True
    ).values_list('perfil_jugador_id', flat=True))
    
    if not jugadores_ids:
        return []
    
    # Calcular valoración para cada jugador
    jugadores_valorados = []
    
    for jugador_id in jugadores_ids:
        valoracion = calcular_valoracion_jugador(jugador_id, equipo_id)
        jugador = PerfilJugador.objects.get(id=jugador_id)
        
        jugadores_valorados.append({
            'id': jugador_id,
            'nombre': jugador.usuario.get_full_name(),
            'posicion': jugador.get_posicion_display() if jugador.posicion else 'N/A',
            'posicion_clave': jugador.posicion if jugador.posicion else '',
            'dorsal': jugador.dorsal,
            'valoracion': valoracion
        })
    
    # Convertir a DataFrame para operaciones vectorizadas
    df = pd.DataFrame(jugadores_valorados)
    
    # Ordenar por valoración ascendente (peores primero)
    df_ordenado = df.sort_values('valoracion', ascending=True)
    
    # Convertir de vuelta a lista de dicts
    resultado = df_ordenado.head(limite).to_dict('records')
    
    return resultado


def obtener_once_recomendado(equipo_id, posicion_filtro=None):
    """
    Obtiene el once recomendado usando pandas para agrupación eficiente.
    - Si posicion_filtro es None: retorna el mejor jugador de cada posición
    - Si posicion_filtro tiene valor: retorna los 3 mejores de esa posición
    
    Incluye información sobre lesiones y sanciones activas.
    
    Args:
        equipo_id: ID del Equipo
        posicion_filtro: Posición a filtrar (ej: 'portero', 'lateral_derecho', etc.)
        
    Returns:
        list: Lista de diccionarios con info del jugador (valoración, lesiones, sanciones)
    """
    from equipos.models import EquipoJugador
    from control_jugadores.models import Lesion, Sancion
    
    # Obtener jugadores activos del equipo
    jugadores_ids = list(EquipoJugador.objects.filter(
        equipo_id=equipo_id,
        es_activo=True
    ).values_list('perfil_jugador_id', flat=True))
    
    if not jugadores_ids:
        return []
    
    # Obtener lesiones y sanciones activas (sets para búsqueda rápida)
    lesiones_ids = set(Lesion.objects.filter(
        jugador_id__in=jugadores_ids,
        activa=True
    ).values_list('jugador_id', flat=True))
    
    sanciones_ids = set(Sancion.objects.filter(
        jugador_id__in=jugadores_ids,
        activa=True
    ).values_list('jugador_id', flat=True))
    
    # Calcular valoración para cada jugador
    jugadores_datos = []
    
    for jugador_id in jugadores_ids:
        jugador = PerfilJugador.objects.get(id=jugador_id)
        
        if not jugador.posicion:
            continue
        
        # Si hay filtro, saltar si no coincide
        if posicion_filtro and jugador.posicion != posicion_filtro:
            continue
        
        valoracion = calcular_valoracion_jugador(jugador_id, equipo_id)
        
        jugadores_datos.append({
            'id': jugador_id,
            'nombre': jugador.usuario.get_full_name(),
            'posicion': jugador.get_posicion_display(),
            'posicion_clave': jugador.posicion,
            'dorsal': jugador.dorsal,
            'valoracion': valoracion,
            'tiene_lesion': jugador_id in lesiones_ids,
            'tiene_sancion': jugador_id in sanciones_ids
        })
    
    # Convertir a DataFrame
    df = pd.DataFrame(jugadores_datos)
    
    if df.empty:
        return []
    
    # Procesar según si hay filtro o no
    if posicion_filtro:
        # Devolver los 3 mejores de la posición filtrada
        resultado = df.sort_values('valoracion', ascending=False).head(3).to_dict('records')
    else:
        # Devolver el mejor de cada posición
        df_mejores = df.sort_values('valoracion', ascending=False).drop_duplicates(
            subset=['posicion_clave'],
            keep='first'
        )
        
        # Ordenar por el orden de posiciones
        orden_posiciones = [
            'portero',
            'lateral_derecho', 'defensa_central', 'lateral_izquierdo',
            'mediocentro_defensivo', 'mediocentro', 'mediocentro_ofensivo',
            'interior_izquierda', 'interior_derecha', 'extremo_derecho', 'extremo_izquierdo',
            'segundo_delantero', 'delantero_centro'
        ]
        
        # Crear un mapeo de orden
        posicion_orden = {pos: i for i, pos in enumerate(orden_posiciones)}
        df_mejores['orden'] = df_mejores['posicion_clave'].map(posicion_orden)
        
        # Ordenar por el orden definido
        df_mejores = df_mejores.sort_values('orden')
        
        # Tomar máximo 11 jugadores
        resultado = df_mejores.drop('orden', axis=1).head(11).to_dict('records')
    
    return resultado
