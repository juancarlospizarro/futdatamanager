/**
 * Gestión de Lesiones desde la tabla de plantilla
 * Permite ver y eliminar lesiones de jugadores
 */

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.closest('[data-bs-target="#gestionar_lesiones_modal"]')) {
            const btn = event.target.closest('[data-bs-target="#gestionar_lesiones_modal"]');
            const jugadorId = btn.dataset.jugadorId;
            const jugadorNombre = btn.dataset.jugadorNombre;
            
            // Establecer el nombre del jugador en el modal
            document.getElementById('jugadorNombreLesion').textContent = jugadorNombre;
            cargarLesiones(jugadorId);
        }
    });
});

function cargarLesiones(jugadorId) {
    const url = apiUrlObtenerLesiones.replace('{jugador_id}', jugadorId);
    
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarLesiones(data.lesiones, jugadorId);
        } else {
            mostrarError('No se pudieron cargar las lesiones');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error al cargar las lesiones');
    });
}

function mostrarLesiones(lesiones, jugadorId) {
    const container = document.getElementById('lesionesListContainer');
    
    if (lesiones.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No hay lesiones registradas para este jugador.</div>';
        return;
    }
    
    let html = '<div class="list-group">';
    
    const tiposLesion = {
        'muscular': 'Lesión muscular',
        'fractura': 'Fractura',
        'distension': 'Distensión',
        'contusion': 'Contusión',
        'esguince': 'Esguince',
        'otra': 'Otra'
    };
    
    lesiones.forEach(lesion => {
        const tipoDisplay = tiposLesion[lesion.tipo] || lesion.tipo;
        const estado = lesion.activa ? '<span class="badge bg-warning text-dark">Activa</span>' : '<span class="badge bg-secondary">Recuperada</span>';
        const fechaInicio = new Date(lesion.fecha_inicio).toLocaleDateString('es-ES');
        
        html += `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center rounded-3 mb-2">
                <div class="flex-grow-1">
                    <h6 class="mb-1 fw-bold text-color-card">${tipoDisplay} ${estado}</h6>
                    <small class="text-secondary">
                        <strong>Fecha:</strong> ${fechaInicio} | 
                        <strong>Duración:</strong> ${lesion.dias_duracion} días
                    </small>
                    ${lesion.descripcion ? `<br><small class="text-secondary"><strong>Descripción:</strong> ${lesion.descripcion}</small>` : ''}
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger eliminar-lesion-btn" 
                    data-lesion-id="${lesion.id}" 
                    data-jugador-id="${jugadorId}"
                    title="Eliminar lesión">
                    <i class="bi bi-trash-fill"></i> Eliminar
                </button>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Agregar listeners a los botones de eliminar
    document.querySelectorAll('.eliminar-lesion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const lesionId = this.dataset.lesionId;
            const jugadorId = this.dataset.jugadorId;
            
            if (confirm('¿Estás seguro de que quieres eliminar esta lesión?')) {
                eliminarLesion(lesionId, jugadorId);
            }
        });
    });
}

function eliminarLesion(lesionId, jugadorId) {
    const url = apiUrlEliminarLesion.replace('{lesion_id}', lesionId);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarExito('Lesión eliminada correctamente');
            setTimeout(() => {
                cargarLesiones(jugadorId);
            }, 500);
        } else {
            mostrarError(data.error || 'Error al eliminar la lesión');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error al eliminar la lesión');
    });
}

function mostrarError(mensaje) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Error:</strong> ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.getElementById('lesionesListContainer');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function mostrarExito(mensaje) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Éxito:</strong> ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.getElementById('lesionesListContainer');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 3000);
}
