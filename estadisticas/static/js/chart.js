// Variables globales para las gráficas
    let chartOfensivo = null;
    let chartDefensivo = null;

    // Función para cargar datos de análisis ofensivo
    async function cargarAnalisisOfensivo() {
        try {
            const currentLang = document.documentElement.lang || 'es';
            const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
            
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-analisis-ofensivo/`);
            const resultado = await response.json();
            
            if (resultado.success) {
                const detalles = resultado.detalles;
                
                // Actualizar gráfica ofensiva
                if (chartOfensivo) {
                    chartOfensivo.data.datasets[0].data = [
                        detalles.goles_total || 0,
                        detalles.asistencias_total || 0,
                        detalles.tiros_total || 0
                    ];
                    chartOfensivo.update();
                } else {
                    crearGraficaOfensiva(detalles);
                }
            }
        } catch (error) {
            console.error('Error cargando análisis ofensivo:', error);
        }
    }

    // Función para cargar datos de análisis defensivo
    async function cargarAnalisisDefensivo() {
        try {
            const currentLang = document.documentElement.lang || 'es';
            const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
            
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-analisis-defensivo/`);
            const resultado = await response.json();
            
            if (resultado.success) {
                const detalles = resultado.detalles;
                
                // Actualizar gráfica defensiva
                if (chartDefensivo) {
                    chartDefensivo.data.datasets[0].data = [
                        detalles.goles_en_contra_promedio || 0
                    ];
                    chartDefensivo.data.datasets[1].data = [
                        detalles.despejes_promedio || 0
                    ];
                    chartDefensivo.update();
                } else {
                    crearGraficaDefensiva(detalles);
                }
            }
        } catch (error) {
            console.error('Error cargando análisis defensivo:', error);
        }
    }

    // Función para crear gráfica ofensiva (barras horizontales)
    function crearGraficaOfensiva(detalles) {
        const ctxOfensivo = document.getElementById('chartOfensivo').getContext('2d');
        chartOfensivo = new Chart(ctxOfensivo, {
            type: 'bar',
            data: {
                labels: ['Goles\nTotales', 'Asistencias\nTotales', 'Tiros\na Puerta'],
                datasets: [{
                    label: 'Goles, Asistencias y Tiros Totales',
                    data: [
                        detalles.goles_total || 0,
                        detalles.asistencias_total || 0,
                        detalles.tiros_total || 0
                    ],
                    backgroundColor: [
                        'rgba(39, 167, 112, 0.8)',
                        'rgba(52, 211, 153, 0.8)',
                        'rgba(110, 231, 183, 0.8)'
                    ],
                    borderColor: [
                        'rgba(39, 167, 112, 1)',
                        'rgba(52, 211, 153, 1)',
                        'rgba(110, 231, 183, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#6c757d',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label.replace('\n', ' ') + ': ' + Math.round(context.parsed.x);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            color: '#6c757d',
                            callback: function(value) {
                                return Math.round(value);
                            }
                        },
                        grid: {
                            color: 'rgba(108, 117, 125, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#6c757d'
                        }
                    }
                }
            }
        });
    }

    // Función para crear gráfica defensiva (comparativa)
    function crearGraficaDefensiva(detalles) {
        const ctxDefensivo = document.getElementById('chartDefensivo').getContext('2d');
        chartDefensivo = new Chart(ctxDefensivo, {
            type: 'bar',
            data: {
                labels: ['Promedio\npor Partido'],
                datasets: [{
                    label: 'Goles en Contra',
                    data: [detalles.goles_en_contra_promedio || 0],
                    backgroundColor: 'rgba(244, 67, 54, 0.8)',
                    borderColor: 'rgba(244, 67, 54, 1)',
                    borderWidth: 2,
                    borderRadius: 5
                }, {
                    label: 'Despejes',
                    data: [detalles.despejes_promedio || 0],
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#6c757d',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#6c757d'
                        },
                        grid: {
                            color: 'rgba(108, 117, 125, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#6c757d'
                        }
                    }
                }
            }
        });
    }

    // Función para abrir el modal de estadísticas del jugador
    async function abrirModalEstadisticasJugador(jugadorId, jugadorNombre) {
        const currentLang = document.documentElement.lang || 'es';
        const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
        
        // Reiniciar la alerta de sin estadísticas
        const alertaDiv = document.getElementById('alertaSinEstadisticas');
        alertaDiv.classList.add('d-none');
        alertaDiv.classList.remove('show');
        
        // Actualizar título del modal
        document.getElementById('nombreJugadorModal').textContent = jugadorNombre;
        
        // Obtener información del jugador
        try {
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-estadisticas-jugador/?jugador_id=${jugadorId}`);
            const resultado = await response.json();
            
            if (resultado.success) {
                // Actualizar datos básicos del jugador
                document.getElementById('dorsalJugadorModal').textContent = resultado.dorsal || '-';
                document.getElementById('posicionJugadorModal').textContent = resultado.posicion || '-';
                
                // Guardar el ID del jugador en el select de partidos
                const selectPartido = document.getElementById('selectPartidoEstadisticas');
                selectPartido.dataset.jugadorId = jugadorId;
                
                // Cargar partidos
                await cargarPartidosEnModal(jugadorId, langPrefix);
                
                // Cargar estadísticas por 90 minutos
                await cargarEstadisticasPor90(jugadorId, langPrefix);
                
                // Mostrar modal
                const modal = new bootstrap.Modal(document.getElementById('modalEstadisticasJugador'));
                modal.show();
            }
        } catch (error) {
            console.error('Error al abrir el modal:', error);
        }
    }
    
    // Función para cargar los partidos en el modal
    async function cargarPartidosEnModal(jugadorId, langPrefix) {
        try {
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-partidos-finalizados/`);
            const resultado = await response.json();
            
            if (resultado.success) {
                const selectPartido = document.getElementById('selectPartidoEstadisticas');
                
                // Limpiar opciones previas (excepto la primera)
                while (selectPartido.options.length > 1) {
                    selectPartido.remove(1);
                }
                
                // Agregar nuevas opciones
                resultado.partidos.forEach(partido => {
                    const option = document.createElement('option');
                    option.value = partido.id;
                    option.textContent = partido.label;
                    selectPartido.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar partidos:', error);
        }
    }
    
    // Función para cargar estadísticas totales del jugador
    async function cargarEstadisticasTotales(jugadorId) {
        const currentLang = document.documentElement.lang || 'es';
        const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
        const alertaDiv = document.getElementById('alertaSinEstadisticas');
        
        try {
            // Ocultar alerta de sin estadísticas
            alertaDiv.classList.add('d-none');
            alertaDiv.classList.remove('show');
            // Cargar estadísticas por 90 minutos
            await cargarEstadisticasPor90(jugadorId, langPrefix);
            ocultarFilasPartido();
        } catch (error) {
            console.error('Error al cargar estadísticas totales:', error);
        }
    }
    
    // Función para cargar estadísticas por 90 minutos
    async function cargarEstadisticasPor90(jugadorId, langPrefix) {
        try {
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-estadisticas-jugador-por-90/?jugador_id=${jugadorId}`);
            const resultado = await response.json();
            
            if (resultado.success) {
                const stats = resultado.stats_por_90;
                document.getElementById('golesJugadorModal').textContent = stats.goles;
                document.getElementById('asistenciasJugadorModal').textContent = stats.asistencias;
                document.getElementById('tirosJugadorModal').textContent = stats.tiros;
                document.getElementById('pasesJugadorModal').textContent = stats.pases;
                document.getElementById('fuersJugadorModal').textContent = stats.fueras_de_juego;
                document.getElementById('despejesJugadorModal').textContent = stats.despejes;
                document.getElementById('faltasJugadorModal').textContent = stats.faltas;
                document.getElementById('paradasJugadorModal').textContent = stats.paradas;
                document.getElementById('amarillasJugadorModal').textContent = stats.amarillas;
                document.getElementById('rojasJugadorModal').textContent = stats.rojas;
            }
        } catch (error) {
            console.error('Error al cargar estadísticas por 90:', error);
        }
    }
    
    // Función para cargar estadísticas en un partido específico
    async function cargarEstadisticasPartido(jugadorId, partidoId) {
        const currentLang = document.documentElement.lang || 'es';
        const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
        const alertaDiv = document.getElementById('alertaSinEstadisticas');
        
        try {
            const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-estadisticas-jugador-partido/?jugador_id=${jugadorId}&partido_id=${partidoId}`);
            const resultado = await response.json();
            
            if (resultado.success) {
                if (resultado.encontrada) {
                    // Ocultar alerta de sin estadísticas
                    alertaDiv.classList.add('d-none');
                    alertaDiv.classList.remove('show');
                    
                    // Mostrar datos del partido
                    document.getElementById('titularJugadorModal').textContent = resultado.titular ? 'Sí' : 'No';
                    document.getElementById('minutosJugadorModal').textContent = resultado.minutos_jugados;
                    mostrarFilasPartido();
                    
                    // Actualizar estadísticas
                    document.getElementById('golesJugadorModal').textContent = resultado.goles;
                    document.getElementById('asistenciasJugadorModal').textContent = resultado.asistencias;
                    document.getElementById('tirosJugadorModal').textContent = resultado.tiros;
                    document.getElementById('pasesJugadorModal').textContent = resultado.pases;
                    document.getElementById('fuersJugadorModal').textContent = resultado.fueras_de_juego;
                    document.getElementById('despejesJugadorModal').textContent = resultado.despejes;
                    document.getElementById('faltasJugadorModal').textContent = resultado.faltas;
                    document.getElementById('paradasJugadorModal').textContent = resultado.paradas;
                    document.getElementById('amarillasJugadorModal').textContent = resultado.amarillas;
                    document.getElementById('rojasJugadorModal').textContent = resultado.rojas;
                } else {
                    // El jugador no participó en este partido - mostrar alerta visual
                    alertaDiv.classList.remove('d-none');
                    alertaDiv.classList.add('show');
                    ocultarFilasPartido();
                    // Resetear valores
                    document.getElementById('selectPartidoEstadisticas').value = '';
                }
            }
        } catch (error) {
            console.error('Error al cargar estadísticas del partido:', error);
        }
    }
    
    // Función auxiliar para mostrar las filas de información del partido
    function mostrarFilasPartido() {
        document.getElementById('filaPartidoInfo').style.display = '';
        document.getElementById('filaMinutosInfo').style.display = '';
    }
    
    // Función auxiliar para ocultar las filas de información del partido
    function ocultarFilasPartido() {
        document.getElementById('filaPartidoInfo').style.display = 'none';
        document.getElementById('filaMinutosInfo').style.display = 'none';
    }

    // Cargar gráficas cuando el documento esté listo
    document.addEventListener('DOMContentLoaded', function() {
        cargarAnalisisOfensivo();
        cargarAnalisisDefensivo();
        
        // Agregar listener al filtro de posición del once
        const filtroOnce = document.getElementById('filtroOnceposicion');
        if (filtroOnce) {
            filtroOnce.addEventListener('change', async function() {
                const posicionSeleccionada = this.value;
                const currentLang = document.documentElement.lang || 'es';
                const langPrefix = currentLang === 'es' ? '/es' : currentLang === 'en' ? '/en' : '';
                
                try {
                    const response = await fetch(`${langPrefix}/estadisticas/ajax/obtener-once-filtrado/?posicion=${posicionSeleccionada}`);
                    const resultado = await response.json();
                    
                    if (resultado.success) {
                        const contenedor = document.getElementById('contenedorOnce');
                        contenedor.innerHTML = '';
                        
                        if (resultado.jugadores.length === 0) {
                            contenedor.innerHTML = '<div class="col-12"><p class="text-muted text-center">{% trans "No hay jugadores disponibles" %}</p></div>';
                        } else {
                            resultado.jugadores.forEach(jugador => {
                                const jugadorHTML = `
                                    <div class="col-md-4 col-lg-3 jugador-once" data-posicion="${jugador.posicion_clave}" data-jugador-id="${jugador.id}" data-jugador-nombre="${jugador.nombre}" style="cursor: pointer;">
                                        <div class="card bg-light-dark text-center rounded-3 p-3 h-100 transition-hover position-relative" style="transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 0.5rem 1rem rgba(39, 167, 112, 0.3)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';">
                                            <!-- Indicadores de lesión/sanción -->
                                            <div style="position: absolute; top: 8px; right: 8px; display: flex; gap: 5px;">
                                                ${jugador.tiene_lesion ? '<span class="badge bg-warning" title="Jugador lesionado" data-bs-toggle="tooltip"><i class="bi bi-bandaid"></i></span>' : ''}
                                                ${jugador.tiene_sancion ? '<span class="badge bg-danger" title="Jugador sancionado" data-bs-toggle="tooltip"><i class="bi bi-exclamation-triangle"></i></span>' : ''}
                                            </div>
                                            <div class="mb-2">
                                                <span class="display-6 fw-bold" style="color: #27a770;">
                                                    ${jugador.dorsal || '-'}
                                                </span>
                                            </div>
                                            <h6 class="fw-bold mb-1">${jugador.nombre}</h6>
                                            <small class="text-secondary">${jugador.posicion}</small>
                                            <div class="mt-2">
                                                <small class="badge bg-success">Valoración: ${jugador.valoracion}</small>
                                            </div>
                                        </div>
                                    </div>
                                `;
                                contenedor.innerHTML += jugadorHTML;
                            });
                        }
                        
                        // Re-agregar listeners a los jugadores
                        document.querySelectorAll('.jugador-once').forEach(jugador => {
                            jugador.addEventListener('click', function() {
                                const jugadorId = this.dataset.jugadorId;
                                const jugadorNombre = this.dataset.jugadorNombre;
                                abrirModalEstadisticasJugador(jugadorId, jugadorNombre);
                            });
                        });
                    }
                } catch (error) {
                    console.error('Error al cargar once filtrado:', error);
                }
            });
        }
        
        // Agregar listeners a los jugadores para abrir el modal
        const juagdoresOnce = document.querySelectorAll('.jugador-once');
        juagdoresOnce.forEach(jugador => {
            jugador.addEventListener('click', function() {
                const jugadorId = this.dataset.jugadorId;
                const jugadorNombre = this.dataset.jugadorNombre;
                abrirModalEstadisticasJugador(jugadorId, jugadorNombre);
            });
        });
        
        // Listener para el cambio de partido en el modal
        const selectPartido = document.getElementById('selectPartidoEstadisticas');
        if (selectPartido) {
            selectPartido.addEventListener('change', function() {
                const jugadorId = this.dataset.jugadorId;
                if (this.value) {
                    cargarEstadisticasPartido(jugadorId, this.value);
                } else {
                    cargarEstadisticasTotales(jugadorId);
                }
            });
        }
        
        // Listener para el botón cerrar de la alerta de sin estadísticas
        const btnCerrarAlerta = document.getElementById('btnCerrarAlertaEstadisticas');
        if (btnCerrarAlerta) {
            btnCerrarAlerta.addEventListener('click', function() {
                const alertaDiv = document.getElementById('alertaSinEstadisticas');
                alertaDiv.classList.add('d-none');
                alertaDiv.classList.remove('show');
            });
        }
    });