document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.closest('[data-bs-target="#gestionar_sanciones_modal"]')) {
            const btn = event.target.closest('[data-bs-target="#gestionar_sanciones_modal"]');
            const jugadorId = btn.dataset.jugadorId;
            const jugadorNombre = btn.dataset.jugadorNombre;
            
            // Establecer el nombre del jugador en el modal
            document.getElementById('jugadorNombreSancion').textContent = jugadorNombre;
            cargarSanciones(jugadorId);
        }
    });
});

function cargarSanciones(jugadorId) {
    const url = apiUrlObtenerSanciones.replace('{jugador_id}', jugadorId);
    
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
            mostrarSanciones(data.sanciones, jugadorId);
        } else {
            mostrarError('No se pudieron cargar las sanciones');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error al cargar las sanciones');
    });
}

function mostrarSanciones(sanciones, jugadorId) {
    const container = document.getElementById('sancionesListContainer');
    
    if (sanciones.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="bi bi-info-circle"></i> No hay sanciones registradas para este jugador.</div>';
        return;
    }
    
    let html = '<div class="list-group">';
    
    const tiposSancion = {
        'amarilla': 'Tarjeta amarilla',
        'roja': 'Tarjeta roja',
        'suspension': 'Suspensión',
        'amonestacion': 'Amonestación'
    };
    
    sanciones.forEach(sancion => {
        const tipoDisplay = tiposSancion[sancion.tipo] || sancion.tipo;
        const estado = sancion.activa ? '<span class="badge bg-danger">Activa</span>' : '<span class="badge bg-secondary">Cumplida</span>';
        const fecha = new Date(sancion.fecha).toLocaleDateString('es-ES');
        const partidosInfo = sancion.partidos_duracion > 0 ? `| <strong>Partidos:</strong> ${sancion.partidos_duracion}` : '';
        
        html += `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center rounded-3 mb-2">
                <div class="flex-grow-1">
                    <h6 class="mb-1 fw-bold text-color-card">${tipoDisplay} ${estado}</h6>
                    <small class="text-secondary">
                        <strong>Fecha:</strong> ${fecha} ${partidosInfo}
                    </small>
                    ${sancion.razon ? `<br><small class="text-secondary"><strong>Razón:</strong> ${sancion.razon}</small>` : ''}
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger eliminar-sancion-btn" 
                    data-sancion-id="${sancion.id}" 
                    data-jugador-id="${jugadorId}"
                    title="Eliminar sanción">
                    <i class="bi bi-trash-fill"></i> Eliminar
                </button>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Agregar listeners a los botones de eliminar
    document.querySelectorAll('.eliminar-sancion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const sancionId = this.dataset.sancionId;
            const jugadorId = this.dataset.jugadorId;
            
            if (confirm('¿Estás seguro de que quieres eliminar esta sanción?')) {
                eliminarSancion(sancionId, jugadorId);
            }
        });
    });
}

function eliminarSancion(sancionId, jugadorId) {
    const url = apiUrlEliminarSancion.replace('{sancion_id}', sancionId);
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
            mostrarExito('Sanción eliminada correctamente');
            setTimeout(() => {
                cargarSanciones(jugadorId);
            }, 500);
        } else {
            mostrarError(data.error || 'Error al eliminar la sanción');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error al eliminar la sanción');
    });
}

function mostrarError(mensaje) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Error:</strong> ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.getElementById('sancionesListContainer');
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
    
    const container = document.getElementById('sancionesListContainer');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 3000);
}
