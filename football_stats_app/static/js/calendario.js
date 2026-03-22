document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendario');
    if (!calendarEl) return;

    // Detectar el idioma actual del documento
    const currentLang = document.documentElement.lang || 'es';
    
    // Mapeo de idiomas a locales de FullCalendar
    const localeMap = {
        'es': 'es',
        'en': 'en'
    };
    
    const locale = localeMap[currentLang] || 'es';

    const calendar = new FullCalendar.Calendar(calendarEl, {
        // Configuración básica
        initialView: 'dayGridMonth',
        locale: locale,
        firstDay: 1,
        height: 'auto',
        contentHeight: 'auto',

        // Interactividad
        selectable: true,
        selectConstraint: 'businessHours',
        
        // Header y navegación
        headerToolbar: {
            left: 'prev next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
        },

        // Opciones de botones traducidas dinámicamente
        buttonText: locale === 'en' ? {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            list: 'List'
        } : {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        },

        // Estilos personalizados
        dayCellClassNames: function(arg) {
            let classes = [];
            // Puedes agregar clases personalizadas aquí
            return classes;
        },

        // Configuración del evento click
        dateClick: function(info) {
            // Aquí puedes agregar eventos al hacer click en un día
            console.log('Día seleccionado:', info.dateStr);
        },

        // Eventos
        events: [],

        // Configuración de tiempo
        nowIndicator: true,
        progressiveEventRendering: true,

        // Configuración visual
        showNonCurrentDates: false,
        fixedWeekCount: false,

        // Tooltip en eventos
        eventDidMount: function(info) {
            info.el.title = info.event.title;
        }
    });

    calendar.render();
});

