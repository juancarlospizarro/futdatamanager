document.addEventListener('DOMContentLoaded', function() {
    console.log('=== Script estadisticas.js cargado ===');
    
    let modalAnadirEstadistica;
    let modalEliminarEstadistica;
    let currentLang = document.documentElement.lang || 'es';
    let langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
    
    console.log('Idioma detectado:', currentLang, 'Prefijo:', langPrefix);
    
    // Inicializar modales
    let modalElementAnadir = document.getElementById('modalAnadirEstadistica');
    console.log('Modal Añadir encontrado:', !!modalElementAnadir);
    if (modalElementAnadir) {
        modalAnadirEstadistica = new bootstrap.Modal(modalElementAnadir, {
            keyboard: false,
            backdrop: 'static'
        });
    }
    
    let modalElementEliminar = document.getElementById('modalEliminarEstadistica');
    console.log('Modal Eliminar encontrado:', !!modalElementEliminar);
    if (modalElementEliminar) {
        modalEliminarEstadistica = new bootstrap.Modal(modalElementEliminar, {
            keyboard: false,
            backdrop: 'static'
        });
    }
    
    let modalElementImportarCSV = document.getElementById('modalImportarCSV');
    let modalImportarCSV;
    console.log('Modal Importar CSV encontrado:', !!modalElementImportarCSV);
    if (modalElementImportarCSV) {
        modalImportarCSV = new bootstrap.Modal(modalElementImportarCSV, {
            keyboard: false,
            backdrop: 'static'
        });
    }
    
    // Botón para abrir modal de añadir
    let btnAnadirEstadistica = document.getElementById('btnAnadirEstadistica');
    console.log('Botón Añadir encontrado:', !!btnAnadirEstadistica);
    if (btnAnadirEstadistica) {
        btnAnadirEstadistica.addEventListener('click', function() {
            console.log('Click en botón Añadir Estadística');
            abrirModalAnadirEstadistica();
        });
    }
    
    // Botón guardar estadística
    let btnGuardarEstadistica = document.getElementById('btnGuardarEstadistica');
    console.log('Botón Guardar encontrado:', !!btnGuardarEstadistica);
    if (btnGuardarEstadistica) {
        btnGuardarEstadistica.addEventListener('click', function() {
            console.log('Click en botón Guardar');
            guardarEstadistica();
        });
    }
    
    // Botón eliminar estadística
    let btnEliminarEstadistica = document.getElementById('btnEliminarEstadistica');
    console.log('Botón Eliminar encontrado:', !!btnEliminarEstadistica);
    if (btnEliminarEstadistica) {
        btnEliminarEstadistica.addEventListener('click', function() {
            console.log('Click en botón Eliminar Estadística');
            abrirModalEliminarEstadistica();
        });
    }
    
    // Botón importar CSV
    let btnImportarCSV = document.getElementById('btnImportarCSV');
    console.log('Botón Importar CSV encontrado:', !!btnImportarCSV);
    if (btnImportarCSV) {
        btnImportarCSV.addEventListener('click', function() {
            console.log('Click en botón Importar CSV');
            abrirModalImportarCSV();
        });
    }
    
    // Botón cargar CSV
    let btnCargarCSV = document.getElementById('btnCargarCSV');
    console.log('Botón Cargar CSV encontrado:', !!btnCargarCSV);
    if (btnCargarCSV) {
        btnCargarCSV.addEventListener('click', function() {
            console.log('Click en botón Cargar CSV');
            importarCSV();
        });
    }
    
    // Cambio de posición del jugador
    let selectJugador = document.getElementById('estadistica_jugador');
    if (selectJugador) {
        selectJugador.addEventListener('change', function() {
            actualizarCamposPorPosicion();
        });
    }
    
    // Cambio de partido en modal de añadir
    let selectPartido = document.getElementById('estadistica_partido');
    if (selectPartido) {
        selectPartido.addEventListener('change', function() {
            cargarEstadisticasPartido();
        });
    }
    
    // Cambio de partido en modal de eliminar
    let selectPartidoEliminar = document.getElementById('partido_eliminar');
    if (selectPartidoEliminar) {
        selectPartidoEliminar.addEventListener('change', function() {
            cargarEstadisticasParaEliminar();
        });
    }
    
    // Funciones
    function abrirModalAnadirEstadistica() {
        console.log('Abriendo modal Añadir Estadística');
        document.getElementById('formAnadirEstadistica').reset();
        cargarJugadoresEquipo();
        if (modalAnadirEstadistica) {
            console.log('Mostrando modal');
            modalAnadirEstadistica.show();
        } else {
            console.error('Modal Añadir no está inicializado');
        }
    }
    
    function abrirModalEliminarEstadistica() {
        console.log('Abriendo modal Eliminar Estadística');
        document.getElementById('formEliminarEstadistica').reset();
        document.getElementById('listaEstadisticasEliminar').innerHTML = '<p class="text-muted">Selecciona un partido para ver las estadísticas</p>';
        if (modalEliminarEstadistica) {
            console.log('Mostrando modal');
            modalEliminarEstadistica.show();
        } else {
            console.error('Modal Eliminar no está inicializado');
        }
    }
    
    function abrirModalImportarCSV() {
        console.log('Abriendo modal Importar CSV');
        document.getElementById('formImportarCSV').reset();
        if (modalImportarCSV) {
            console.log('Mostrando modal Importar CSV');
            modalImportarCSV.show();
        } else {
            console.error('Modal Importar CSV no está inicializado');
        }
    }
    
    function cargarJugadoresEquipo() {
        fetch(`${langPrefix}/estadisticas/ajax/obtener-jugadores/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let selectJugador = document.getElementById('estadistica_jugador');
                selectJugador.innerHTML = '<option value="">Selecciona un jugador</option>';
                
                data.jugadores.forEach(jugador => {
                    let option = document.createElement('option');
                    option.value = jugador.perfil_jugador__id;
                    option.textContent = `${jugador.perfil_jugador__usuario__first_name} ${jugador.perfil_jugador__usuario__last_name} (${jugador.perfil_jugador__dorsal || '-'})`;
                    option.dataset.posicion = jugador.perfil_jugador__posicion || '';
                    selectJugador.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    function actualizarCamposPorPosicion() {
        let selectJugador = document.getElementById('estadistica_jugador');
        let option = selectJugador.options[selectJugador.selectedIndex];
        let posicion = option.dataset.posicion;
        
        // Habilitar todos los campos
        let campos = ['goles', 'asistencias', 'tiros', 'pases', 'despejes', 'faltas', 'paradas'];
        campos.forEach(campo => {
            let elemento = document.getElementById('estadistica_' + campo);
            if (elemento) {
                elemento.disabled = false;
            }
        });
        
        // Deshabilitar según posición
        if (posicion === 'portero') {
            // Portero: solo paradas
            ['goles', 'asistencias', 'tiros', 'pases', 'despejes', 'faltas'].forEach(campo => {
                let elemento = document.getElementById('estadistica_' + campo);
                if (elemento) {
                    elemento.disabled = true;
                    elemento.value = 0;
                }
            });
        } else if (['lateral_derecho', 'lateral_izquierdo', 'defensa_central'].includes(posicion)) {
            // Defensa: sin paradas y tiros limitados
            let elementos = ['paradas'];
            elementos.forEach(campo => {
                let elemento = document.getElementById('estadistica_' + campo);
                if (elemento) {
                    elemento.disabled = true;
                    elemento.value = 0;
                }
            });
        } else if (['delantero_centro', 'segundo_delantero'].includes(posicion)) {
            // Delantero: sin paradas
            let elemento = document.getElementById('estadistica_paradas');
            if (elemento) {
                elemento.disabled = true;
                elemento.value = 0;
            }
        }
    }
    
    function guardarEstadistica() {
        let jugadorId = document.getElementById('estadistica_jugador').value;
        let partidoId = document.getElementById('estadistica_partido').value;
        
        if (!jugadorId || !partidoId) {
            showAlert('error', 'Selecciona jugador y partido');
            return;
        }
        
        let datos = {
            jugador_id: jugadorId,
            partido_id: partidoId,
            titular: document.getElementById('estadistica_titular').checked,
            minutos_jugados: parseInt(document.getElementById('estadistica_minutos_jugados').value) || 0,
            goles: parseInt(document.getElementById('estadistica_goles').value) || 0,
            asistencias: parseInt(document.getElementById('estadistica_asistencias').value) || 0,
            tiros: parseInt(document.getElementById('estadistica_tiros').value) || 0,
            pases: parseInt(document.getElementById('estadistica_pases').value) || 0,
            fueras_de_juego: parseInt(document.getElementById('estadistica_fueras_de_juego').value) || 0,
            paradas: parseInt(document.getElementById('estadistica_paradas').value) || 0,
            despejes: parseInt(document.getElementById('estadistica_despejes').value) || 0,
            faltas: parseInt(document.getElementById('estadistica_faltas').value) || 0,
            tarjetas_amarillas: parseInt(document.getElementById('estadistica_tarjetas_amarillas').value) || 0,
            tarjeta_roja: document.getElementById('estadistica_tarjeta_roja').checked
        };
        
        fetch(`${langPrefix}/estadisticas/ajax/guardar-estadistica/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', 'Estadística guardada correctamente');
                modalAnadirEstadistica.hide();
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert('error', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error al guardar estadística');
        });
    }
    
    function abrirModalEliminarEstadistica() {
        document.getElementById('formEliminarEstadistica').reset();
        document.getElementById('listaEstadisticasEliminar').innerHTML = '<p class="text-muted">Selecciona un partido para ver las estadísticas</p>';
        if (modalEliminarEstadistica) {
            modalEliminarEstadistica.show();
        }
    }
    
    function cargarEstadisticasParaEliminar() {
        let partidoId = document.getElementById('partido_eliminar').value;
        
        if (!partidoId) return;
        
        fetch(`${langPrefix}/estadisticas/ajax/obtener-estadisticas/${partidoId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            let listaEstadisticas = document.getElementById('listaEstadisticasEliminar');
            if (data.estadisticas && data.estadisticas.length > 0) {
                let html = '<div class="list-group">';
                data.estadisticas.forEach(est => {
                    html += `
                        <div class="list-group-item">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${est.jugador__usuario__first_name} ${est.jugador__usuario__last_name}</strong>
                                    <br>
                                    <small class="text-muted">Goles: ${est.goles} | Asistencias: ${est.asistencias} | Despejes: ${est.despejes}</small>
                                </div>
                                <button class="btn btn-sm btn-danger" onclick="eliminarEstadistica(${est.id})">
                                    Eliminar
                                </button>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                listaEstadisticas.innerHTML = html;
            } else {
                listaEstadisticas.innerHTML = '<p class="text-muted">No hay estadísticas registradas para este partido</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('listaEstadisticasEliminar').innerHTML = '<p class="text-danger">Error al cargar estadísticas</p>';
        });
    }
    
    function cargarEstadisticasPartido() {
        let partidoId = document.getElementById('estadistica_partido').value;
        
        if (!partidoId) return;
        
        fetch(`${langPrefix}/estadisticas/ajax/obtener-estadisticas/${partidoId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            let tablaEstadisticas = document.getElementById('tablaEstadisticasPartido');
            if (tablaEstadisticas && data.estadisticas) {
                let html = '';
                data.estadisticas.forEach(est => {
                    html += `
                        <tr>
                            <td>${est.jugador__usuario__first_name} ${est.jugador__usuario__last_name}</td>
                            <td>${est.goles}</td>
                            <td>${est.asistencias}</td>
                            <td>${est.despejes}</td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="eliminarEstadistica(${est.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                });
                
                if (html) {
                    tablaEstadisticas.innerHTML = html;
                    document.getElementById('contenedorTablaEstadisticas').style.display = 'block';
                } else {
                    document.getElementById('contenedorTablaEstadisticas').style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    window.eliminarEstadistica = function(estadisticaId) {
        if (confirm('¿Estás seguro de que quieres eliminar esta estadística?')) {
            fetch(`${langPrefix}/estadisticas/ajax/eliminar-estadistica/${estadisticaId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Estadística eliminada');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showAlert('error', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    };
    
    function importarCSV() {
        console.log('Iniciando importar CSV');
        
        let archivoCSV = document.getElementById('archivo_csv').files[0];
        let partidoId = document.getElementById('partido_csv').value;
        
        if (!archivoCSV) {
            showAlert('error', 'Por favor selecciona un archivo CSV');
            return;
        }
        
        if (!partidoId) {
            showAlert('error', 'Por favor selecciona un partido');
            return;
        }
        
        console.log('Archivo:', archivoCSV.name, 'Partido:', partidoId);
        
        // Mostrar progreso
        document.getElementById('progreso_import').style.display = 'block';
        document.getElementById('btnCargarCSV').disabled = true;
        
        let formData = new FormData();
        formData.append('archivo', archivoCSV);
        formData.append('partido_id', partidoId);
        
        fetch(`${langPrefix}/estadisticas/ajax/importar-csv/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data);
            
            if (data.success) {
                let mensaje = `✓ ${data.creadas} estadísticas importadas correctamente`;
                if (data.advertencias && data.advertencias.length > 0) {
                    console.warn('Advertencias:', data.advertencias);
                    mensaje += ` (${data.advertencias.length} advertencias)`;
                }
                showAlert('success', mensaje);
                setTimeout(() => {
                    modalImportarCSV.hide();
                    location.reload();
                }, 2000);
            } else {
                showAlert('error', data.error || 'Error al importar CSV');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error al procesar el CSV');
        })
        .finally(() => {
            document.getElementById('progreso_import').style.display = 'none';
            document.getElementById('btnCargarCSV').disabled = false;
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
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        document.body.appendChild(alertDiv.firstElementChild);
    }
});
