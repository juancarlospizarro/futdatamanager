document.addEventListener('DOMContentLoaded', function () {
    // Variables globales
    let modalAnadirEntrenamiento;
    let modalEliminarEntrenamiento;
    let modalConfirmarEliminar;
    let calendarInstance; // Referencia al calendario
    let entrenamientoAEliminar = null; // ID del entrenamiento a eliminar

    // Obtener el idioma actual
    const currentLang = document.documentElement.lang || 'es';
    const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';

    // URLs construidas dinámicamente
    const URLS = {
        crear_entrenamiento: `${langPrefix}/events/ajax/crear_entrenamiento/`,
        obtener_entrenamientos: `${langPrefix}/events/ajax/obtener_entrenamientos/`,
        listar_entrenamientos: `${langPrefix}/events/ajax/listar_entrenamientos/`,
        eliminar_entrenamiento: (id) => `${langPrefix}/events/ajax/eliminar_entrenamiento/${id}/`
    };

    // Inicializar Modals
    modalAnadirEntrenamiento = new bootstrap.Modal(document.getElementById('modalAnadirEntrenamiento'), {
        keyboard: false,
        backdrop: 'static'
    });

    modalEliminarEntrenamiento = new bootstrap.Modal(document.getElementById('modalEliminarEntrenamiento'), {
        keyboard: false,
        backdrop: 'static'
    });

    modalConfirmarEliminar = new bootstrap.Modal(document.getElementById('modalConfirmarEliminar'), {
        keyboard: false,
        backdrop: 'static'
    });

    // Esperar a que el calendario se haya renderizado
    setTimeout(() => {
        calendarInstance = window.calendarInstance; // El calendario.js debe exponer esta variable
    }, 100);

    // Botón: Añadir Entrenamiento
    document.getElementById('btn-anadirEntrenamiento').addEventListener('click', function () {
        document.getElementById('formAnadirEntrenamiento').reset();
        modalAnadirEntrenamiento.show();
    });

    // Botón: Guardar Entrenamiento
    document.getElementById('btnGuardarEntrenamiento').addEventListener('click', function () {
        guardarEntrenamiento();
    });

    // Botón: Eliminar Entrenamiento
    document.getElementById('btn-eliminarEntrenamiento').addEventListener('click', function () {
        cargarEntrenamientos();
        modalEliminarEntrenamiento.show();
    });

    // Botón: Confirmar Eliminación
    document.getElementById('btnConfirmarEliminar').addEventListener('click', function () {
        if (entrenamientoAEliminar) {
            confirmarEliminacion(entrenamientoAEliminar);
        }
    });

    // Función: Guardar Entrenamiento
    function guardarEntrenamiento() {
        const form = document.getElementById('formAnadirEntrenamiento');
        const formData = new FormData(form);

        fetch(URLS.crear_entrenamiento, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', 'Entrenamiento creado correctamente');
                modalAnadirEntrenamiento.hide();
                form.reset();
                // Recargar lista de eventos próximos
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

    // Función: Cargar Entrenamientos para eliminar
    function cargarEntrenamientos() {
        const listaEntrenamientos = document.getElementById('listaEntrenamientos');
        listaEntrenamientos.innerHTML = '<p class="text-muted">Cargando...</p>';

        fetch(URLS.listar_entrenamientos, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                listaEntrenamientos.innerHTML = '';
                data.forEach(entrenamiento => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item d-flex justify-content-between align-items-start p-3 border-bottom';
                    item.innerHTML = `
                        <div class="flex-grow-1">
                            <strong>${entrenamiento.tipo}</strong>
                            <br>
                            <small class="text-muted">${entrenamiento.fecha_hora}</small>
                            ${entrenamiento.descripcion ? `<br><small>${entrenamiento.descripcion}</small>` : ''}
                        </div>
                        <button type="button" class="btn btn-danger btn-sm ms-2" onclick="mostrarConfirmacion(${entrenamiento.id}, '${entrenamiento.tipo}', '${entrenamiento.fecha_hora}', event)">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                    listaEntrenamientos.appendChild(item);
                });
            } else {
                listaEntrenamientos.innerHTML = '<p class="text-muted text-center">No hay entrenamientos</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            listaEntrenamientos.innerHTML = '<p class="text-danger">Error al cargar</p>';
        });
    }

    // Función: Mostrar confirmación de eliminación
    window.mostrarConfirmacion = function(entrenamientoId, tipo, fecha, event) {
        event.preventDefault();
        event.stopPropagation();
        
        entrenamientoAEliminar = entrenamientoId;
        document.getElementById('tipoEliminar').textContent = tipo;
        document.getElementById('fechaEliminar').textContent = fecha;
        
        // Cerrar modal de lista y abrir de confirmación
        modalEliminarEntrenamiento.hide();
        
        // Pequeño delay para que se cierre primero
        setTimeout(() => {
            modalConfirmarEliminar.show();
        }, 300);
    };

    // Función: Confirmar eliminación
    function confirmarEliminacion(entrenamientoId) {
        fetch(URLS.eliminar_entrenamiento(entrenamientoId), {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', 'Eliminado correctamente');
                modalConfirmarEliminar.hide();
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

    // Función: Mostrar alerta (Bootstrap toast o alert)
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
        
        // Eliminar alerta después de 5 segundos
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
