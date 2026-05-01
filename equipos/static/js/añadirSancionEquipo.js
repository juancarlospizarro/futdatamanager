document.addEventListener('DOMContentLoaded', function() {
    const formularioSancion = document.getElementById('formulario_añadir_sancion');
    
    if (formularioSancion) {
        formularioSancion.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Obtener datos del formulario
            const jugadorId = document.getElementById('jugadorSancionSelect').value;
            const tipo = document.getElementById('tipoSancionSelect').value;
            const razon = document.getElementById('razonSancionInput').value;
            const partidosDuracion = document.getElementById('partidosDuracionInput').value;
            const activa = document.getElementById('activaSancionCheck').checked;
            
            // Validación básica
            if (!jugadorId || !tipo || !razon) {
                mostrarError('Por favor completa todos los campos requeridos');
                return;
            }
            
            if (razon.trim().length < 5) {
                mostrarError('La razón debe tener al menos 5 caracteres');
                return;
            }
            
            // Preparar datos
            const datos = {
                jugador_id: jugadorId,
                tipo: tipo,
                razon: razon,
                partidos_duracion: partidosDuracion || 0,
                activa: activa ? 1 : 0
            };
            
            // Enviar petición AJAX
            enviarSancion(datos);
        });
    }
});

/**
 * Enviar la sanción al servidor
 */
function enviarSancion(datos) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = '/teams/ajax/agregar_sancion/';
    
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
            mostrarExito('Sanción registrada correctamente. Email enviado al jugador.');
            document.getElementById('formulario_añadir_sancion').reset();
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addSancionModal'));
                if (modal) {
                    modal.hide();
                }
            }, 1500);
        } else {
            mostrarError(data.message || 'Error al registrar la sanción');
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
    
    const modalBody = document.querySelector('#addSancionModal .modal-body');
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
    
    const modalBody = document.querySelector('#addSancionModal .modal-body');
    const alertaExistente = modalBody.querySelector('.alert');
    if (alertaExistente) {
        alertaExistente.remove();
    }
    modalBody.insertBefore(alerta, modalBody.firstChild);
}
