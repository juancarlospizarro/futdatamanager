document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendario');
    if (!calendarEl) return;

    // Detectar el idioma actual del documento
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    // Mapeo de idiomas a locales de FullCalendar
    const localeMap = {
        'es': 'es',
        'en': 'en'
    };
    
    const locale = localeMap[currentLang] || 'es';

    const calendar = new FullCalendar.Calendar(calendarEl, {
        // Configuración básica
        initialView: 'dayGridMonth',
        locale: locale,
        firstDay: 1,
        height: 'auto',
        contentHeight: 'auto',

        // Interactividad
        selectable: true,
        selectConstraint: 'businessHours',
        
        // Header y navegación
        headerToolbar: {
            left: 'prev next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
        },

        // Opciones de botones traducidas dinámicamente
        buttonText: locale === 'en' ? {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            list: 'List'
        } : {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        },

        // Estilos personalizados
        dayCellClassNames: function(arg) {
            let classes = [];
            return classes;
        },

        // Configuración del evento click
        dateClick: function(info) {
            console.log('Día seleccionado:', info.dateStr);
        },

        // Click en evento
        eventClick: function(info) {
            mostrarInfoEvento(info.event);
        },

        // Eventos - será poblado por entrenamientos.js y partidos.js
        events: [],

        // Configuración de tiempo
        nowIndicator: true,
        progressiveEventRendering: true,

        // Configuración visual
        showNonCurrentDates: false,
        fixedWeekCount: false,

        // Tooltip en eventos
        eventDidMount: function(info) {
            info.el.title = info.event.title;
            
            // Si es un partido finalizado, cambiar color a verde
            if (info.event.extendedProps.type === 'partido' && info.event.extendedProps.finalizado) {
                info.el.style.backgroundColor = '#198754'; // Verde Bootstrap
                info.el.style.borderColor = '#198754';
            }
        }
    });

    calendar.render();

    // Exponer la instancia del calendario globalmente
    window.calendarInstance = calendar;
    calendarEl._fullCalendarApi = calendar;

    // Cargar entrenamientos y partidos automáticamente
    cargarEntrenamientosEnCalendario(calendar, langPrefix);
    cargarPartidosEnCalendario(calendar, langPrefix);
});

function cargarEntrenamientosEnCalendario(calendar, langPrefix) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefixActual = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    const url = `${langPrefixActual}/events/ajax/obtener_entrenamientos/`;
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(entrenamientos => {
        if (Array.isArray(entrenamientos)) {
            entrenamientos.forEach(evento => {
                calendar.addEvent(evento);
            });
        }
    })
    .catch(error => {
        console.error('Error al cargar entrenamientos:', error);
    });
}

function cargarPartidosEnCalendario(calendar, langPrefix) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefixActual = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    const url = `${langPrefixActual}/events/ajax/obtener_partidos/`;
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(partidos => {
        if (Array.isArray(partidos)) {
            partidos.forEach(evento => {
                calendar.addEvent(evento);
            });
        }
    })
    .catch(error => {
        console.error('Error al cargar partidos:', error);
    });
}

function mostrarInfoEvento(event) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    const modalInfoEvento = new bootstrap.Modal(document.getElementById('modalInfoEvento'));
    const contenidoEvento = document.getElementById('contenidoEvento');
    const btnFinalizar = document.getElementById('btnFinalizarPartido');
    const btnAnadirResultado = document.getElementById('btnAnadirResultado');
    
    // Si ambos botones no existen, usar versión de solo lectura (para jugadores)
    if (btnFinalizar === null && btnAnadirResultado === null) {
        mostrarInfoEventoJugador(event);
        return;
    }
    
    // Limpiar eventos anteriores de los botones (solo si existen)
    if (btnFinalizar) {
        btnFinalizar.replaceWith(btnFinalizar.cloneNode(true));
    }
    if (btnAnadirResultado) {
        btnAnadirResultado.replaceWith(btnAnadirResultado.cloneNode(true));
    }
    const btnFinalizarNuevo = document.getElementById('btnFinalizarPartido');
    const btnAnadirResultadoNuevo = document.getElementById('btnAnadirResultado');
    
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
        btnFinalizarNuevo.style.display = 'none';
        btnAnadirResultadoNuevo.style.display = 'none';
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
        
        // Guardar partido ID en dataset
        if (btnFinalizarNuevo) btnFinalizarNuevo.dataset.partidoId = event.id;
        if (btnAnadirResultadoNuevo) btnAnadirResultadoNuevo.dataset.partidoId = event.id;
        
        // Determinar estado de finalización de forma segura
        const esFinalizado = event.extendedProps.finalizado === true;
        
        // Mostrar botón de finalizar solo si NO está finalizado
        if (!esFinalizado) {
            if (btnFinalizarNuevo) {
                btnFinalizarNuevo.style.display = 'block';
                btnFinalizarNuevo.onclick = function() {
                    // Abre modal para entrada de resultado
                    const modalAnadirResultado = new bootstrap.Modal(document.getElementById('modalAnadirResultado'));
                    document.getElementById('golesLocal').value = 0;
                    document.getElementById('golesVisitante').value = 0;
                    modalAnadirResultado.show();
                };
            }
            if (btnAnadirResultadoNuevo) {
                btnAnadirResultadoNuevo.style.display = 'none';
            }
        } else {
            if (btnFinalizarNuevo) {
                btnFinalizarNuevo.style.display = 'none';
            }
            // Mostrar botón "Añadir resultado" si está finalizado pero no tiene resultado
            if (event.extendedProps.goles_local === null || event.extendedProps.goles_visitante === null) {
                if (btnAnadirResultadoNuevo) {
                    btnAnadirResultadoNuevo.style.display = 'block';
                    btnAnadirResultadoNuevo.onclick = function() {
                        const modalAnadirResultado = new bootstrap.Modal(document.getElementById('modalAnadirResultado'));
                        document.getElementById('golesLocal').value = 0;
                        document.getElementById('golesVisitante').value = 0;
                        modalAnadirResultado.show();
                    };
                }
            } else {
                if (btnAnadirResultadoNuevo) {
                    btnAnadirResultadoNuevo.style.display = 'none';
                }
            }
        }
    }
    
    contenidoEvento.innerHTML = html;
    modalInfoEvento.show();
}

function finalizarPartidoDesdeModal(partidoId) {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    const url = `${langPrefix}/events/ajax/finalizar_partido/${partidoId}/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            const modalElement = document.getElementById('modalInfoEvento');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Mostrar alerta
            showAlert('success', 'Partido marcado como finalizado');
            
            // Recargar datos
            setTimeout(() => {
                cargarEventosProximos();
                cargarPartidosAnteriores();
                location.reload();
            }, 500);
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

function showAlert(type, message) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 9999;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHtml;
    document.body.appendChild(alertDiv.firstElementChild);
    
    setTimeout(() => {
        const alert = document.querySelector('.alert-' + (type === 'success' ? 'success' : 'danger'));
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function cargarEventosProximos() {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    const urlEntrenamientos = `${langPrefix}/events/ajax/obtener_entrenamientos/`;
    const urlPartidos = `${langPrefix}/events/ajax/obtener_partidos/`;
    
    console.log('cargarEventosProximos - URL Entrenamientos:', urlEntrenamientos);
    console.log('cargarEventosProximos - URL Partidos:', urlPartidos);
    
    Promise.all([
        fetch(urlEntrenamientos, {
            method: 'GET',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        }).then(r => r.json()),
        fetch(urlPartidos, {
            method: 'GET',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        }).then(r => r.json())
    ])
    .then(([entrenamientos, partidos]) => {
        console.log('Entrenamientos recibidos:', entrenamientos);
        console.log('Partidos recibidos:', partidos);
        
        // Combinar eventos
        const eventos = [...(Array.isArray(entrenamientos) ? entrenamientos : []), 
                         ...(Array.isArray(partidos) ? partidos : [])];
        
        // Filtrar eventos futuros y ordenar
        const ahora = new Date();
        console.log('Hora actual para comparación:', ahora.toISOString());
        
        const eventosFuturos = eventos.filter(evt => {
            const startDate = new Date(evt.start);
            console.log(`Evento: ${evt.title}, fecha: ${evt.start}, parseado: ${startDate.toISOString()}, es futuro: ${startDate > ahora}`);
            return startDate > ahora;
        })
            .sort((a, b) => new Date(a.start) - new Date(b.start))
            .slice(0, 5);
        
        console.log('Eventos futuros después del filtro:', eventosFuturos);
        
        // Renderizar
        const contenedor = document.getElementById('listaEventosProximos');
        
        if (!contenedor) {
            console.warn('No se encontró el contenedor listaEventosProximos');
            return;
        }
        
        if (eventosFuturos.length === 0) {
            contenedor.innerHTML = '<p class="text-secondary text-muted">{% trans "No hay eventos próximos." %}</p>';
            return;
        }
        
        let html = '<ul class="list-group list-group-flush">';
        eventosFuturos.forEach(evento => {
            const fecha = evento.fecha_hora || new Date(evento.start).toLocaleString();
            let titulo = '';
            let detalles = '';
            let borderClass = 'border-secondary';
            
            if (evento.type === 'entrenamiento') {
                titulo = `<i class="bi bi-dribbble text-info"></i> ${evento.tipo}`;
                detalles = evento.descripcion ? `<small class="text-muted d-block">📝 ${evento.descripcion}</small>` : '';
                borderClass = 'border-info';
            } else if (evento.type === 'partido') {
                // Crear enlace al equipo si existe slug
                let rivalHtml = evento.rival_slug 
                    ? `<a href="${langPrefix}/teams/${evento.rival_slug}/" class="text-decoration-none text-danger fw-bold">${evento.rival}</a>`
                    : `<span class="text-danger fw-bold">${evento.rival}</span>`;
                
                titulo = `<i class="bi bi-play-fill text-danger"></i> vs ${rivalHtml}`;
                
                // Mostrar competición si existe
                let competicionHtml = '';
                if (evento.competicion) {
                    competicionHtml = `<small class="text-muted d-block"><i class="bi bi-cup"></i> ${evento.competicion}</small>`;
                }
                
                // Crear enlace a Google Maps para la dirección
                let direccionHtml = '';
                if (evento.estadio_direccion) {
                    const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(evento.estadio_direccion)}`;
                    direccionHtml = `<a href="${mapsUrl}" target="_blank" class="text-decoration-none text-muted"><i class="bi bi-geo-alt"></i> ${evento.estadio_direccion}</a><br>`;
                }
                
                detalles = `${competicionHtml}<small class="d-block">${direccionHtml}<small class="text-muted">🏟️ ${evento.estadio || 'Estadio por confirmar'}</small></small>`;
                borderClass = 'border-danger';
            }
            
            html += `
                <li class="list-group-item border-start border-3 ${borderClass}">
                    <strong>${titulo}</strong>
                    <br>
                    <small class="text-muted"><i class="bi bi-calendar"></i> ${fecha}</small>
                    <br>
                    ${detalles}
                </li>
            `;
        });
        html += '</ul>';
        
        contenedor.innerHTML = html;
    })
    .catch(error => {
        console.error('Error al cargar eventos próximos:', error);
        const contenedor = document.getElementById('listaEventosProximos');
        if (contenedor) {
            contenedor.innerHTML = '<p class="text-danger">{% trans "Error al cargar eventos" %}</p>';
        }
    });
}

function cargarPartidosAnteriores() {
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    const url = `${langPrefix}/events/ajax/obtener_partidos/`;
    const contenedor = document.getElementById('listaPartidosAnteriores');
    
    console.log('cargarPartidosAnteriores - URL:', url);
    console.log('cargarPartidosAnteriores - Contenedor encontrado:', !!contenedor);
    
    if (!contenedor) {
        console.warn('No se encontré el contenedor listaPartidosAnteriores');
        return;
    }
    
    fetch(url, {
        method: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(todosLosPartidos => {
        console.log('Todos los partidos recibidos:', todosLosPartidos);
        
        // Filtrar partidos anteriores a la fecha/hora actual
        const ahora = new Date();
        const partidos = Array.isArray(todosLosPartidos) 
            ? todosLosPartidos.filter(p => new Date(p.start) < ahora)
            : [];
        
        console.log('Partidos anteriores después del filtro:', partidos);
        
        if (partidos.length === 0) {
            contenedor.innerHTML = '<p class="text-secondary text-muted text-center">{% trans "No hay partidos anteriores." %}</p>';
            return;
        }
        
        // Renderizar como lista clickeable
        let html = '<ul class="list-group list-group-flush">';
        partidos.forEach(partido => {
            const competicion = partido.competicion ? `<small class="text-muted d-block"><i class="bi bi-cup"></i> ${partido.competicion}</small>` : '';
            const estadio = partido.estadio ? `<small class="text-muted"><i class="bi bi-geo-alt"></i> ${partido.estadio}</small>` : '';
            
            html += `
                <li class="list-group-item border-start border-3 border-secondary partido-anterior" style="cursor: pointer;" data-partido-id="${partido.id}">
                    <strong><i class="bi bi-play-fill text-danger"></i> vs ${partido.rival}</strong>
                    <br>
                    <small class="text-muted"><i class="bi bi-calendar"></i> ${partido.fecha_hora}</small>
                    <br>
                    ${competicion}
                    ${estadio}
                </li>
            `;
        });
        html += '</ul>';
        
        contenedor.innerHTML = html;
        
        // Agregar listeners a los partidos anteriores
        document.querySelectorAll('.partido-anterior').forEach(item => {
            item.addEventListener('click', function() {
                const partidoId = parseInt(this.dataset.partidoId);
                console.log('Clic en partido anterior:', partidoId);
                abrirModalEvento(partidoId, 'partido', partidos);
            });
        });
    })
    .catch(error => {
        console.error('Error al cargar partidos anteriores:', error);
        contenedor.innerHTML = '<p class="text-danger">{% trans "Error al cargar partidos anteriores" %}</p>';
    });
}

// Cargar eventos próximos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        console.log('Ejecutando cargarEventosProximos y cargarPartidosAnteriores');
        cargarEventosProximos();
        cargarPartidosAnteriores();
    }, 500);
});

// Versión de solo lectura de mostrarInfoEvento para jugadores
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

