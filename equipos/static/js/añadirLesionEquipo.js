document.addEventListener('DOMContentLoaded', function() {
    const formularioLesion = document.getElementById('formulario_añadir_lesion');
    
    if (formularioLesion) {
        formularioLesion.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Obtener datos del formulario
            const jugadorId = document.getElementById('jugadorLesionSelect').value;
            const tipo = document.getElementById('tipoLesionSelect').value;
            const diasDuracion = document.getElementById('diasDuracionInput').value;
            const descripcion = document.getElementById('descripcionLesionInput').value;
            const activa = document.getElementById('activaLesionCheck').checked;
            
            // Validación básica
            if (!jugadorId || !tipo || !diasDuracion) {
                mostrarError('Por favor completa todos los campos requeridos');
                return;
            }
            
            if (parseInt(diasDuracion) < 1 || parseInt(diasDuracion) > 365) {
                mostrarError('La duración debe estar entre 1 y 365 días');
                return;
            }
            
            // Preparar datos
            const datos = {
                jugador_id: jugadorId,
                tipo: tipo,
                dias_duracion: diasDuracion,
                descripcion: descripcion,
                activa: activa ? 1 : 0
            };
            
            // Enviar petición AJAX
            enviarLesion(datos);
        });
    }
});

/**
 * Enviar la lesión al servidor
 */
function enviarLesion(datos) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = '/teams/ajax/agregar_lesion/'; // Endpoint en el backend
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarExito('Lesión registrada correctamente');
            document.getElementById('formulario_añadir_lesion').reset();
            
            // Cerrar modal después de unos segundos
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addLesionModal'));
                if (modal) {
                    modal.hide();
                }
            }, 1500);
        } else {
            mostrarError(data.message || 'Error al registrar la lesión');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error de conexión. Intenta de nuevo.');
    });
}

/**
 * Mostrar mensaje de error
 */
function mostrarError(mensaje) {
    const alerta = document.createElement('div');
    alerta.className = 'alert alert-danger alert-dismissible fade show';
    alerta.innerHTML = `
        <i class="bi bi-exclamation-circle-fill"></i> ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const modalBody = document.querySelector('#addLesionModal .modal-body');
    const alertaExistente = modalBody.querySelector('.alert');
    if (alertaExistente) {
        alertaExistente.remove();
    }
    modalBody.insertBefore(alerta, modalBody.firstChild);
}

/**
 * Mostrar mensaje de éxito
 */
function mostrarExito(mensaje) {
    const alerta = document.createElement('div');
    alerta.className = 'alert alert-success alert-dismissible fade show';
    alerta.innerHTML = `
        <i class="bi bi-check-circle-fill"></i> ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const modalBody = document.querySelector('#addLesionModal .modal-body');
    const alertaExistente = modalBody.querySelector('.alert');
    if (alertaExistente) {
        alertaExistente.remove();
    }
    modalBody.insertBefore(alerta, modalBody.firstChild);
}
