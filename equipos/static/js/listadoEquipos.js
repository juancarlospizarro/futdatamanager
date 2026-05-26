$(document).ready(function() {

    const table = $('#tablaEquipos').DataTable({
        "order": [[2, "desc"]],
        "paging": true,
        "pageLength": 5,  // Número de filas por página
        "lengthChange": false,  // Oculta el selector de filas por página
        "language": {             // Placeholder vacío
            emptyTable: "No hay equipos registrados",
            "paginate": {
                "previous": "«",
                "next": "»"
            },
            "zeroRecords": "No se encontraron equipos",
        },  
        "info": false,
        "dom": "rt"
    });

    // Buscador personalizado
    $('#buscadorEquipos').on('keyup', function() {
        table.search(this.value).draw();
    });
});