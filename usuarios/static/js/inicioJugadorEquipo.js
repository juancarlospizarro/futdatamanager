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
        const resultadoBadge = evento.goles_local !== null && evento.goles_visitante !== null 
            ? `<span class="badge bg-success ms-2">${evento.goles_local} - ${evento.goles_visitante}</span>`
            : evento.finalizado 
            ? '<span class="badge bg-secondary ms-2">S/R</span>'
            : '';
        
        html += `
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
    });
    
    html += '</div>';
    document.getElementById('listaEventosProximos').innerHTML = html;
    
    // Agregar event listeners
    document.querySelectorAll('.evento-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const eventoId = parseInt(this.dataset.eventoId);
            abrirModalEvento(eventoId, 'partido', eventosProximosCache);
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
        const resultado = partido.goles_local !== null && partido.goles_visitante !== null
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
        if (partido.goles_local !== null && partido.goles_visitante !== null) {
            if (partido.goles_local > partido.goles_visitante) victorias++;
            else if (partido.goles_local === partido.goles_visitante) empates++;
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
    const eventObj = {
        id: evento.id,
        extendedProps: {
            id: evento.id,
            type: 'partido',
            rival: evento.rival,
            rival_slug: evento.rival_slug || null,
            estadio: evento.estadio,
            estadio_direccion: evento.estadio_direccion || '',
            fecha_hora: evento.fecha_hora,
            finalizado: evento.finalizado,
            competicion: evento.competicion || null,
            goles_local: evento.goles_local,
            goles_visitante: evento.goles_visitante
        }
    };
    
    mostrarInfoEventoJugador(eventObj);
}

// Versión de solo lectura para jugadores
function mostrarInfoEventoJugador(event) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    const modalInfoEvento = new bootstrap.Modal(document.getElementById('modalInfoEvento'));
    const contenidoEvento = document.getElementById('contenidoEvento');
    
    let html = '';
    
    if (event.extendedProps.type === 'entrenamiento') {
        html = `
            <div class="card border-start border-4 border-info">
                <div class="card-body">
                    <h5 class="card-title"><i class="bi bi-dribbble text-info"></i> ${event.extendedProps.tipo}</h5>
                    <p class="card-text small">
                        <strong>Fecha:</strong> ${event.extendedProps.fecha_hora || event.start.toLocaleString()}<br>
                        ${event.extendedProps.descripcion ? `<strong>Descripción:</strong> ${event.extendedProps.descripcion}<br>` : ''}
                    </p>
                </div>
            </div>
        `;
    } else if (event.extendedProps.type === 'partido') {
        // Crear enlace al equipo si existe slug
        let rivalHtml = event.extendedProps.rival_slug 
            ? `<a href="${langPrefix}/teams/${event.extendedProps.rival_slug}/" class="text-decoration-none">${event.extendedProps.rival}</a>`
            : event.extendedProps.rival;
        
        // Crear enlace a Google Maps para la dirección
        let direccionHtml = event.extendedProps.estadio_direccion
            ? `<a href="https://www.google.com/maps/search/${encodeURIComponent(event.extendedProps.estadio_direccion)}" target="_blank" class="text-decoration-none"><i class="bi bi-geo-alt"></i> ${event.extendedProps.estadio_direccion}</a>`
            : '';
        
        // Mostrar resultado si existe
        let resultadoHtml = '';
        if (event.extendedProps.goles_local !== null && event.extendedProps.goles_visitante !== null) {
            resultadoHtml = `<div class="mb-2"><span class="badge bg-success fs-6">${event.extendedProps.goles_local} - ${event.extendedProps.goles_visitante}</span></div>`;
        }
        
        // Mostrar estado si está finalizado
        let estadoHtml = event.extendedProps.finalizado 
            ? '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Finalizado</span>'
            : '';
        
        // Mostrar competición si existe
        let competicionHtml = event.extendedProps.competicion 
            ? `<strong>Competición:</strong> ${event.extendedProps.competicion}<br>`
            : '';
        
        html = `
            <div class="border-start border-4 ${event.extendedProps.finalizado ? 'border-success' : 'border-danger'} ps-3">
                <h5 class="mb-2"><i class="bi ${event.extendedProps.finalizado ? 'bi-check-circle text-success' : 'bi-play-fill text-danger'}"></i> vs ${rivalHtml} ${estadoHtml}</h5>
                ${resultadoHtml}
                <p class="text-muted small">
                    ${competicionHtml}
                    <strong>Fecha:</strong> ${event.extendedProps.fecha_hora || event.start.toLocaleString()}<br>
                    <strong>Estadio:</strong> ${event.extendedProps.estadio}<br>
                    ${direccionHtml ? `<strong>Dirección:</strong> ${direccionHtml}<br>` : ''}
                </p>
            </div>
        `;
    }
    
    contenidoEvento.innerHTML = html;
    modalInfoEvento.show();
}

// Event listener inicial
document.addEventListener('DOMContentLoaded', () => {
    // Cargar eventos y partidos iniciales
    setTimeout(() => {
        cargarEventosProximos();
        cargarPartidosAnteriores();
    }, 500);
});