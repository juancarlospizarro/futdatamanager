document.addEventListener('DOMContentLoaded', function () {
    // Variables globales
    let modalAnadirPartido;
    let modalEliminarPartido;
    let modalConfirmarEliminarPartido;
    let calendarInstance; // Referencia al calendario
    let partidoAEliminar = null; // ID del partido a eliminar

    // Obtener el idioma actual
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';

    // URLs construidas dinámicamente
    const URLS = {
        crear_partido: `${langPrefix}/events/ajax/crear_partido/`,
        obtener_partidos: `${langPrefix}/events/ajax/obtener_partidos/`,
        listar_partidos: `${langPrefix}/events/ajax/listar_partidos/`,
        eliminar_partido: (id) => `${langPrefix}/events/ajax/eliminar_partido/${id}/`,
        obtener_equipos: `${langPrefix}/events/ajax/obtener_equipos/`
    };

    // Inicializar Modals
    modalAnadirPartido = new bootstrap.Modal(document.getElementById('modalAnadirPartido'), {
        keyboard: false,
        backdrop: 'static'
    });

    modalEliminarPartido = new bootstrap.Modal(document.getElementById('modalEliminarPartido'), {
        keyboard: false,
        backdrop: 'static'
    });

    modalConfirmarEliminarPartido = new bootstrap.Modal(document.getElementById('modalConfirmarEliminarPartido'), {
        keyboard: false,
        backdrop: 'static'
    });

    // Esperar a que el calendario se haya renderizado
    setTimeout(() => {
        calendarInstance = window.calendarInstance;
    }, 100);

    // Botón Añadir Partido
    document.getElementById('btn-anadirPartido').addEventListener('click', function () {
        document.getElementById('formAnadirPartido').reset();
        cargarEquiposDispositivos();
        modalAnadirPartido.show();
    });

    // Botón Guardar Partido
    document.getElementById('btnGuardarPartido').addEventListener('click', function () {
        guardarPartido();
    });

    // Botón Eliminar Partido
    document.getElementById('btn-eliminarPartido').addEventListener('click', function () {
        cargarPartidos();
        modalEliminarPartido.show();
    });

    // Botón Confirmar Eliminación
    document.getElementById('btnConfirmarEliminarPartido').addEventListener('click', function () {
        if (partidoAEliminar) {
            confirmarEliminacionPartido(partidoAEliminar);
        }
    });

    // Sincronizar campos de equipo
    const selectEquipo = document.getElementById('equipoVisitantePartido');
    const inputEquipo = document.getElementById('nombreEquipoPartido');

    selectEquipo.addEventListener('change', function() {
        if (this.value) {
            inputEquipo.value = '';
            inputEquipo.disabled = true;
        } else {
            inputEquipo.disabled = false;
        }
    });

    inputEquipo.addEventListener('input', function() {
        if (this.value) {
            selectEquipo.value = '';
            selectEquipo.disabled = true;
        } else {
            selectEquipo.disabled = false;
        }
    });

    // Función: Cargar equipos disponibles
    function cargarEquiposDispositivos() {
        const selectEquipo = document.getElementById('equipoVisitantePartido');
        selectEquipo.innerHTML = '<option value="">Selecciona un equipo (opcional)</option>';
        selectEquipo.disabled = false;
        document.getElementById('nombreEquipoPartido').disabled = false;

        fetch(URLS.obtener_equipos, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(equipos => {
            if (Array.isArray(equipos)) {
                equipos.forEach(equipo => {
                    const option = document.createElement('option');
                    option.value = equipo.id;
                    option.textContent = equipo.nombre;
                    selectEquipo.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error cargando equipos:', error);
        });
    }

    // Función: Guardar Partido
    function guardarPartido() {
        const form = document.getElementById('formAnadirPartido');
        const formData = new FormData(form);

        fetch(URLS.crear_partido, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', 'Partido creado correctamente');
                modalAnadirPartido.hide();
                form.reset();
                setTimeout(() => {
                    cargarEventosProximos();
                }, 500);
            } else {
                showAlert('error', data.error || 'Error al crear');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error de conexión');
        });
    }

    // Función: Cargar Partidos para eliminar
    function cargarPartidos() {
        const listaPartidos = document.getElementById('listaPartidos');
        listaPartidos.innerHTML = '<p class="text-muted">Cargando...</p>';

        fetch(URLS.listar_partidos, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                listaPartidos.innerHTML = '';
                data.forEach(partido => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item d-flex justify-content-between align-items-start p-3 border-bottom';
                    item.innerHTML = `
                        <div class="flex-grow-1">
                            <strong>vs ${partido.rival}</strong>
                            <br>
                            <small class="text-muted">${partido.fecha_hora}</small>
                            <br>
                            <small class="text-secondary"><i class="bi bi-geo-alt"></i> ${partido.estadio}</small>
                        </div>
                        <button type="button" class="btn btn-danger btn-sm ms-2" onclick="mostrarConfirmacionPartido(${partido.id}, '${partido.rival.replace(/'/g, "\\'")}', '${partido.fecha_hora}', '${partido.estadio.replace(/'/g, "\\'")}', event)">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                    listaPartidos.appendChild(item);
                });
            } else {
                listaPartidos.innerHTML = '<p class="text-muted text-center">No hay partidos</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listaPartidos.innerHTML = '<p class="text-danger">Error al cargar</p>';
        });
    }

    // Función: Mostrar confirmación de eliminación
    window.mostrarConfirmacionPartido = function(partidoId, rival, fecha, estadio, event) {
        event.preventDefault();
        event.stopPropagation();
        
        partidoAEliminar = partidoId;
        document.getElementById('rivalEliminar').textContent = 'vs ' + rival;
        document.getElementById('fechaEliminarPartido').textContent = fecha;
        document.getElementById('estadioEliminarPartido').textContent = estadio;
        
        modalEliminarPartido.hide();
        
        setTimeout(() => {
            modalConfirmarEliminarPartido.show();
        }, 300);
    };

    // Función: Confirmar eliminación
    function confirmarEliminacionPartido(partidoId) {
        fetch(URLS.eliminar_partido(partidoId), {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', 'Eliminado correctamente');
                modalConfirmarEliminarPartido.hide();
                setTimeout(() => {
                    cargarEventosProximos();
                }, 500);
            } else {
                showAlert('error', data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error de conexión');
        });
    }

    // Función: Mostrar alerta
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

    // Función auxiliar: Obtener CSRF token
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
});
