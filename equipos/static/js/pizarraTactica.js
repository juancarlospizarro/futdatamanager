let selectedPlayer = null;
    let offset = { x: 0, y: 0 };

    const board = document.getElementById('tacticalBoard');
    const players = document.querySelectorAll('.player');
    const resetBtn = document.getElementById('resetBtn');
    const saveBtn = document.getElementById('saveBtn');

    /**
     * Obtiene las dimensiones del tablero táctico.
     * @returns {Object} Objeto con width, height, left y top del tablero en píxeles
     */
    function getBoardDimensions() {
        const rect = board.getBoundingClientRect();
        return {
            width: rect.width,
            height: rect.height,
            left: rect.left,
            top: rect.top
        };
    }

    /**
     * Extrae las coordenadas (x, y) de un evento de mouse o touch.
     * @param {Event} e - Evento de mouse o touch
     * @returns {Object} Objeto con propiedades x e y
     */
    function getCoordinates(e) {
        if (e.touches) {
            return {
                x: e.touches[0].clientX,
                y: e.touches[0].clientY
            };
        }
        return {
            x: e.clientX,
            y: e.clientY
        };
    }

    /**
     * Actualiza la posición de un jugador en el tablero.
     * Convierte coordenadas de píxeles a porcentajes y los limita al rango válido (0-100%).
     * @param {HTMLElement} player - Elemento del jugador a mover
     * @param {Object} coords - Objeto con propiedades x e y en píxeles
     */
    function updatePlayerPosition(player, coords) {
        const dims = getBoardDimensions();
        let x = coords.x - dims.left;
        let y = coords.y - dims.top;

        let xPercent = (x / dims.width * 100);
        let yPercent = (y / dims.height * 100);

        xPercent = Math.max(0, Math.min(xPercent, 100));
        yPercent = Math.max(0, Math.min(yPercent, 100));

        player.style.left = xPercent + '%';
        player.style.top = yPercent + '%';
    }

    /**
     * Configura drag and drop nativo para navegadores que lo soporten.
     */
    players.forEach(player => {
        player.addEventListener('dragstart', (e) => {
            selectedPlayer = player;
            player.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });

        player.addEventListener('dragend', (e) => {
            if (selectedPlayer) {
                player.classList.remove('dragging');
                selectedPlayer = null;
            }
        });
    });

    board.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });

    board.addEventListener('drop', (e) => {
        e.preventDefault();
        if (selectedPlayer) {
            updatePlayerPosition(selectedPlayer, getCoordinates(e));
            selectedPlayer.classList.remove('dragging');
            selectedPlayer = null;
        }
    });

    // Click y arrastrar compatible con mouse y touch
    players.forEach(player => {
        function startDrag(e) {
            selectedPlayer = player;
            player.classList.add('dragging');
            e.preventDefault();

            function onMove(moveEvent) {
                if (!selectedPlayer) return;
                updatePlayerPosition(selectedPlayer, getCoordinates(moveEvent));
            }

            function stopDrag() {
                if (selectedPlayer) {
                    selectedPlayer.classList.remove('dragging');
                    selectedPlayer = null;
                }
                if (e.type === 'mousedown') {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', stopDrag);
                } else {
                    document.removeEventListener('touchmove', onMove);
                    document.removeEventListener('touchend', stopDrag);
                }
            }

            if (e.type === 'mousedown') {
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', stopDrag);
            } else {
                document.addEventListener('touchmove', onMove, { passive: false });
                document.addEventListener('touchend', stopDrag);
            }
        }

        player.addEventListener('mousedown', startDrag);
        player.addEventListener('touchstart', startDrag, { passive: true });
    });

    /**
     * Configura los botones de control del tablero (reiniciar y descargar).
     * - Reiniciar: Recarga la página para volver a las posiciones iniciales
     * - Descargar: Exporta el tablero a imagen PNG y guarda posiciones en localStorage
     */
    resetBtn.addEventListener('click', () => {
        location.reload();
    });

    saveBtn.addEventListener('click', async () => {
        try {
            saveBtn.disabled = true;
            
            const canvas = await html2canvas(board, {
                backgroundColor: '#2d5016',
                scale: 2,
                useCORS: true,
                allowTaint: true
            });
            
            // Descargar como imagen
            const link = document.createElement('a');
            link.href = canvas.toDataURL('image/jpeg', 0.95);
            link.download = `pizarra-tactica-${new Date().getTime()}.jpg`;
            link.click();
            
            // Guardar en localStorage también
            const positions = {};
            players.forEach(player => {
                const team = player.classList.contains('player-team1') ? '1' : '2';
                positions[`${team}-${player.dataset.number}`] = {
                    left: player.style.left,
                    top: player.style.top
                };
            });
            localStorage.setItem('tacticalPositions', JSON.stringify(positions));
            
            saveBtn.disabled = false;
        } catch (error) {
            console.error('Error al descargar:', error);
            alert('Error al descargar la imagen');
            saveBtn.disabled = false;
        }
    });

    /**
     * Restaura las posiciones de los jugadores guardadas en localStorage cuando la página carga.
     * Las posiciones se guardan automáticamente al descargar la imagen.
     */
    window.addEventListener('load', () => {
        const saved = localStorage.getItem('tacticalPositions');
        if (saved) {
            try {
                const positions = JSON.parse(saved);
                players.forEach(player => {
                    const team = player.classList.contains('player-team1') ? '1' : '2';
                    const key = `${team}-${player.dataset.number}`;
                    if (positions[key]) {
                        player.style.left = positions[key].left;
                        player.style.top = positions[key].top;
                    }
                });
            } catch (e) {
                console.error('Error al cargar posiciones:', e);
            }
        }
    });