// Cache global para eventos y partidos
let eventosProximosCache = [];
let partidosAnterioresCache = [];

// Funciones para renderizar eventos y calcular estadísticas
function renderizarEventosProximos(eventos) {
    eventosProximosCache = eventos; // Guardar en cache
    
    if (!eventos || eventos.length === 0) {
        document.getElementById('listaEventosProximos').innerHTML = '<p class="text-secondary text-muted">{% trans "Sin próximos eventos" %}</p>';
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    
    eventos.forEach(evento => {
        let html_item = '';
        
        // Diferenciar entre entrenamientos y partidos
        if (evento.tipo) {
            // Es un entrenamiento
            const tipoTraducido = {
                'fuerza': '{% trans "Fuerza" %}',
                'tactico': '{% trans "Táctico" %}',
                'ataque': '{% trans "Ataque" %}',
                'defensa': '{% trans "Defensa" %}',
                'recuperacion': '{% trans "Recuperación" %}'
            };
            
            html_item = `
                <a href="#" class="list-group-item list-group-item-action border-start border-4 border-warning ps-3 py-2 evento-item" 
                   data-evento-id="${evento.id}" data-evento-type="entrenamiento">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1 fw-bold"><i class="bi bi-person-arms-up"></i> ${tipoTraducido[evento.tipo] || evento.tipo}</h6>
                            <small class="text-muted d-block">${evento.fecha_hora}</small>
                            ${evento.descripcion ? `<small class="text-muted d-block">${evento.descripcion}</small>` : ''}
                        </div>
                        <span class="badge bg-warning text-dark">{% trans "Entrenamiento" %}</span>
                    </div>
                </a>
            `;
        } else {
            // Es un partido
            const resultadoBadge = (evento.goles_local !== null && evento.goles_local !== undefined && evento.goles_visitante !== null && evento.goles_visitante !== undefined)
                ? `<span class="badge bg-success ms-2">${evento.goles_local} - ${evento.goles_visitante}</span>`
                : evento.finalizado 
                ? '<span class="badge bg-secondary ms-2">S/R</span>'
                : '';
            
            html_item = `
                <a href="#" class="list-group-item list-group-item-action border-start border-4 border-foot-green ps-3 py-2 evento-item" 
                   data-evento-id="${evento.id}" data-evento-type="partido">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1 fw-bold">Vs ${evento.rival}</h6>
                            <small class="text-muted d-block">${evento.fecha_hora}</small>
                            <small class="text-muted d-block"><i class="bi bi-geo-alt"></i> ${evento.estadio}</small>
                        </div>
                        <div>${resultadoBadge}</div>
                    </div>
                </a>
            `;
        }
        
        html += html_item;
    });
    
    html += '</div>';
    document.getElementById('listaEventosProximos').innerHTML = html;
    
    // Agregar event listeners
    document.querySelectorAll('.evento-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const eventoId = parseInt(this.dataset.eventoId);
            const eventoType = this.dataset.eventoType;
            abrirModalEvento(eventoId, eventoType, eventosProximosCache);
        });
    });
}

function renderizarPartidosAnteriores(partidos) {
    partidosAnterioresCache = partidos; // Guardar en cache
    
    if (!partidos || partidos.length === 0) {
        document.getElementById('listaPartidosAnteriores').innerHTML = '<p class="text-secondary text-muted">{% trans "Sin partidos anteriores" %}</p>';
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    
    partidos.forEach(partido => {
        const resultado = (partido.goles_local !== null && partido.goles_local !== undefined && partido.goles_visitante !== null && partido.goles_visitante !== undefined)
            ? `<span class="badge bg-success">${partido.goles_local} - ${partido.goles_visitante}</span>`
            : '<span class="badge bg-secondary">S/R</span>';
        
        html += `
            <a href="#" class="list-group-item list-group-item-action border-start border-4 border-foot-green ps-3 py-2 partido-anterior"
               data-partido-id="${partido.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1 fw-bold">Vs ${partido.rival}</h6>
                        <small class="text-muted d-block">${partido.fecha_hora}</small>
                        <small class="text-muted d-block"><i class="bi bi-geo-alt"></i> ${partido.estadio}</small>
                    </div>
                    <div>${resultado}</div>
                </div>
            </a>
        `;
    });
    
    html += '</div>';
    document.getElementById('listaPartidosAnteriores').innerHTML = html;
    
    // Agregar event listeners
    document.querySelectorAll('.partido-anterior').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const partidoId = parseInt(this.dataset.partidoId);
            abrirModalEvento(partidoId, 'partido', partidosAnterioresCache);
        });
    });
}

function calcularEstadisticas(partidos) {
    let victorias = 0, empates = 0, derrotas = 0;
    
    partidos.forEach(partido => {
        const golesLocal = partido.goles_local !== null && partido.goles_local !== undefined ? partido.goles_local : null;
        const golesVisitante = partido.goles_visitante !== null && partido.goles_visitante !== undefined ? partido.goles_visitante : null;
        
        if (golesLocal !== null && golesVisitante !== null) {
            if (golesLocal > golesVisitante) victorias++;
            else if (golesLocal === golesVisitante) empates++;
            else derrotas++;
        }
    });
    
    const total = victorias + empates + derrotas;
    document.getElementById('totalPartidos').textContent = total;
    document.getElementById('totalVictorias').textContent = victorias;
    document.getElementById('totalEmpates').textContent = empates;
    document.getElementById('totalDerrotas').textContent = derrotas;
}

function cargarEventosProximos() {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    const urlEntrenamientos = `${langPrefix}/events/ajax/obtener_entrenamientos/`;
    const urlPartidos = `${langPrefix}/events/ajax/obtener_partidos/`;
    
    Promise.all([
        fetch(urlEntrenamientos).then(r => r.json()),
        fetch(urlPartidos).then(r => r.json())
    ])
    .then(([entrenamientos, partidos]) => {
        // Combinar eventos
        const eventos = [...(Array.isArray(entrenamientos) ? entrenamientos : []), 
                         ...(Array.isArray(partidos) ? partidos : [])];
        
        // Filtrar solo eventos futuros
        const ahora = new Date();
        const eventosFuturos = eventos
            .filter(evt => new Date(evt.start) > ahora)
            .sort((a, b) => new Date(a.start) - new Date(b.start))
            .slice(0, 5);
        
        renderizarEventosProximos(eventosFuturos);
    })
    .catch(error => console.error('Error cargando eventos:', error));
}

function cargarPartidosAnteriores() {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    fetch(`${langPrefix}/events/ajax/obtener_partidos/`)
        .then(response => response.json())
        .then(todosLosPartidos => {
            // Filtrar partidos anteriores a la fecha/hora actual
            const ahora = new Date();
            const partidos = Array.isArray(todosLosPartidos) 
                ? todosLosPartidos.filter(p => new Date(p.start) < ahora)
                : [];
            renderizarPartidosAnteriores(partidos);
            calcularEstadisticas(partidos);
        })
        .catch(error => console.error('Error cargando partidos:', error));
}

function abrirModalEvento(eventoId, tipo, datosCache) {
    // Buscar el evento/partido en el cache
    let evento = null;
    if (datosCache && datosCache.length > 0) {
        evento = datosCache.find(e => e.id === eventoId);
    }
    
    if (!evento) {
        console.error('No se encontró el evento con ID:', eventoId);
        return;
    }
    
    // Construir un objeto event compatible con mostrarInfoEvento()
    if (tipo === 'entrenamiento') {
        const eventObj = {
            id: evento.id,
            start: evento.start,
            extendedProps: {
                id: evento.id,
                type: 'entrenamiento',
                tipo: evento.tipo,
                descripcion: evento.descripcion || '',
                fecha_hora: evento.fecha_hora
            }
        };
        mostrarInfoEvento(eventObj);
    } else {
        // Asegurar que los valores de goles existen y no son undefined
        const golesLocal = evento.goles_local !== undefined ? evento.goles_local : null;
        const golesVisitante = evento.goles_visitante !== undefined ? evento.goles_visitante : null;
        
        const eventObj = {
            id: evento.id,
            start: evento.start,
            extendedProps: {
                id: evento.id,
                type: 'partido',
                rival: evento.rival || 'Rival desconocido',
                rival_slug: evento.rival_slug || null,
                estadio: evento.estadio || 'Estadio desconocido',
                estadio_direccion: evento.estadio_direccion || '',
                fecha_hora: evento.fecha_hora,
                finalizado: evento.finalizado === true,
                competicion: evento.competicion || null,
                goles_local: golesLocal,
                goles_visitante: golesVisitante,
                equipo_local_nombre: evento.equipo_local_nombre || 'Local',
                equipo_visitante_nombre: evento.equipo_visitante_nombre || 'Visitante',
                mi_posicion: evento.mi_posicion || 'local'
            }
        };
        mostrarInfoEvento(eventObj);
    }
}

// Event listener para guardar resultado
document.addEventListener('DOMContentLoaded', () => {
    const btnGuardarResultado = document.getElementById('btnGuardarResultado');
    if (btnGuardarResultado) {
        btnGuardarResultado.addEventListener('click', function() {
            const golesLocal = document.getElementById('golesLocal').value;
            const golesVisitante = document.getElementById('golesVisitante').value;
            const btnFinalizarPartido = document.getElementById('btnFinalizarPartido');
            const partidoId = btnFinalizarPartido.dataset.partidoId;
            
            if (!partidoId) {
                showAlert('error', 'Error: No se pudo identificar el partido');
                return;
            }
            
            if (isNaN(golesLocal) || isNaN(golesVisitante) || golesLocal < 0 || golesVisitante < 0) {
                showAlert('error', 'Los goles deben ser números no negativos');
                return;
            }
            
            finalizarPartidoDesdeModal(partidoId, golesLocal, golesVisitante);
        });
    }
    
    // Cargar eventos y partidos iniciales
    setTimeout(() => {
        cargarEventosProximos();
        cargarPartidosAnteriores();
    }, 500);
});

function finalizarPartidoDesdeModal(partidoId, golesLocal, golesVisitante) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    const url = `${langPrefix}/events/ajax/finalizar_partido/${partidoId}/`;
    
    const body = {
        goles_local: parseInt(golesLocal),
        goles_visitante: parseInt(golesVisitante)
    };
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(body)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modales
            const modalResultado = bootstrap.Modal.getInstance(document.getElementById('modalAnadirResultado'));
            const modalInfoEvento = bootstrap.Modal.getInstance(document.getElementById('modalInfoEvento'));
            
            if (modalResultado) modalResultado.hide();
            if (modalInfoEvento) modalInfoEvento.hide();
            
            showAlert('success', data.mensaje);
            
            // Recargar datos
            setTimeout(() => {
                cargarEventosProximos();
                cargarPartidosAnteriores();
                location.reload();
            }, 1500);
        } else {
            showAlert('error', data.error || 'Error al finalizar partido');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error de conexión');
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}