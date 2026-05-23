$(document).ready(function() {
    // Existe el elemento
    if (document.getElementById('tablaJugadores') === null) {
        return;
    }

    // jQuery lo encuentra
    const $tabla = $('#tablaJugadores');
    if ($tabla.length === 0) {
        return;
    }

    // Si llegamos aquí, la tabla existe y podemos inicializar DataTables
    try {
        // Contar el número real de columnas en el thead
        const numColumnas = $tabla.find('thead th').length;
        
        // Definir columnDefs dinámicamente
        const columnDefs = [
            {
                "targets": [0, 3, 4], // Dorsal, Altura, Peso (ordenables)
                "orderable": true
            },
            {
                "targets": [1, 2, 5], // Jugador, Pierna, Capitán (no ordenables)
                "orderable": false
            }
        ];

        // Si existe la columna de Acciones (columna 6), hacerla no ordenable
        if (numColumnas > 6) {
            columnDefs.push({
                "targets": numColumnas - 1, // Última columna (Acciones)
                "orderable": false,
                "searchable": false
            });
        }

        const tableJugadores = $tabla.DataTable({
            "order": [[0, "asc"]],
            "paging": true,
            "pageLength": 10,
            "lengthChange": false,
            "language": {
                "emptyTable": "No hay jugadores en la plantilla",
                "paginate": {
                    "previous": "«",
                    "next": "»"
                },
                "zeroRecords": "No se encontraron jugadores",
            },
            "info": false,
            "dom": "rt",
            "columnDefs": columnDefs
        });

        // Buscador personalizado
        $('#buscadorJugadores').on('keyup', function() {
            tableJugadores.search(this.value).draw();
        });
    } catch (error) {
        console.error('Error inicializando DataTables:', error);
    }
});