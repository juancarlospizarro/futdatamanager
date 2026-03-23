// Mensajes de validación para cada campo
const validationMessages = {
    nombre: document.getElementById('msg-nombre').textContent,
    apellidos: document.getElementById('msg-apellidos').textContent,
    email: document.getElementById('msg-email').textContent,
    telefono_exacto: document.getElementById('msg-telefono-exacto').textContent,
    fecha: document.getElementById('msg-fecha').textContent
};

/* Funcion que valida cada campo y da estilo */
function validarCampo(input, condicion, mensajeError) {
    const mensaje = input.nextElementSibling;

    if (condicion()) {
        mensaje.classList.remove("text-danger");
        mensaje.classList.add("text-success");
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
        mensaje.textContent = "";
        return true;
    } else {
        mensaje.textContent = mensajeError;
        mensaje.classList.add("text-danger");
        mensaje.classList.remove("text-success");
        input.classList.add("is-invalid");
        input.classList.remove("is-valid");
        return false;
    }
}

/* Función para resetear los estilos de los campos */
function resetCampo(input) {
    const mensaje = input.nextElementSibling;

    input.classList.remove("is-invalid", "is-valid");
    mensaje.textContent = "";
    mensaje.classList.remove("text-danger", "text-success");
}

// VALIDACIÓN TIEMPO REAL CAMPO NOMBRE
const nombreRegistro = document.getElementById("nombre");

nombreRegistro.addEventListener("input", function () {

    if (nombreRegistro.value.trim().length === 0) {
        resetCampo(nombreRegistro);
        return;
    }

    validarCampo(
        nombreRegistro,
        function () { 
            return nombreRegistro.value.trim().length >= 2 && /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(nombreRegistro.value.trim()); 
        },
        validationMessages.nombre
    );
});

// VALIDACIÓN TIEMPO REAL CAMPO APELLIDOS
const apellidosRegistro = document.getElementById("apellidos");

apellidosRegistro.addEventListener("input", function () {

    if (apellidosRegistro.value.trim().length === 0) {
        resetCampo(apellidosRegistro);
        return;
    }

    validarCampo(
        apellidosRegistro,
        function () { 
            return apellidosRegistro.value.trim().length >= 2 && /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(apellidosRegistro.value.trim()); 
        },
        validationMessages.apellidos
    );
});

// VALIDACIÓN TIEMPO REAL CAMPO EMAIL
const emailRegistro = document.getElementById("email");

emailRegistro.addEventListener("input", function () {

    if (emailRegistro.value.trim().length === 0) {
        resetCampo(emailRegistro);
        return;
    }

    validarCampo(
        emailRegistro,
        function () { 
            return /^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(emailRegistro.value); 
        },
        validationMessages.email
    );
});

// VALIDACIÓN TIEMPO REAL CAMPO TELÉFONO
const telefonoRegistro = document.getElementById("telefono");

telefonoRegistro.addEventListener("input", () => {
    const valor = telefonoRegistro.value;

    if (valor === "") {
        resetCampo(telefonoRegistro);
        return;
    }

    validarCampo(
        telefonoRegistro,
        () => /^\d{0,9}$/.test(telefonoRegistro.value),
        validationMessages.telefono_exacto
    );
});

// VALIDACIÓN TIEMPO REAL CAMPO FECHA DE NACIMIENTO
const fechaNacimiento = document.getElementById("fechanacimiento");

/* Función que valida si la fecha introducida como parámetro es válida */
function esFechaValida(fecha) {
    if (!fecha) return false;

    let hoy = new Date();
    let nacimiento = new Date(fecha);

    let fechaMinima = new Date(1900, 0, 1);

    if (nacimiento < fechaMinima) {
        return false;
    }

    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    let mes = hoy.getMonth() - nacimiento.getMonth();

    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
        edad--;
    }

    return edad >= 12;
}

/* Función que valida que el formato de la fecha sea correcto, es decir YYYY-MM-DD */
function validarFormatoFecha(fecha) {

    if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
        return false;
    }

    // Comprobar que es una fecha que existe
    const date = new Date(fecha);
    if (isNaN(date.getTime())) {
        return false;
    }

    return true;
}

fechaNacimiento.addEventListener("input", function () {

    let valor = fechaNacimiento.value;

    if (valor === "") {
        resetCampo(fechaNacimiento);
        return;
    }

    if (fechaNacimiento.value.length > 10) {
        fechaNacimiento.value = fechaNacimiento.value.slice(0, 10);
    }
    

    validarCampo(
        fechaNacimiento,
        function () {
            return validarFormatoFecha(fechaNacimiento.value) && esFechaValida(fechaNacimiento.value);
        },
        validationMessages.fecha
    );
});

// VALIDACIÓN COMPLETA DEL FORMULARIO AL ENVIARLO
const editarDatosForm = document.getElementById("formulario_editar_datos");

editarDatosForm.setAttribute("novalidate", true);

editarDatosForm.addEventListener("submit", function (event) {

    var validarNombre = validarCampo(
        nombreRegistro,
        function () { return nombreRegistro.value.trim().length >= 2 && /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(nombreRegistro.value.trim()); },
        validationMessages.nombre
    );

    var validarApellidos = validarCampo(
        apellidosRegistro,
        function () { return apellidosRegistro.value.trim().length >= 2 && /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(apellidosRegistro.value.trim()); },
        validationMessages.apellidos
    );

    var validarEmail = validarCampo(
        emailRegistro,
        function () {
            return /^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(emailRegistro.value);
        },
        validationMessages.email
    );

    const validarTelefono = validarCampo(
        telefonoRegistro,
        () => /^\d{9}$/.test(telefonoRegistro.value),
        validationMessages.telefono_exacto
    );

    var validarPassword = validarCampo(
        passwordRegistro,
        function () {
            var valor = passwordRegistro.value;
            return valor.length >= 6 &&
                /[A-Z]/.test(valor) &&
                /[0-9]/.test(valor) &&
                /[!@#$%^&*()_+\-=[\]{};:'",.<>/?\\|]/.test(valor);
        },
        "La contraseña no cumple los requisitos."
    );

    var validarRepetirPassword = 
        repetirContrasena.value.length > 0 &&
        repetirContrasena.value === passwordRegistro.value;

    if (!validarRepetirPassword) {
        const mensaje = repetirContrasena.nextElementSibling;
        repetirContrasena.classList.add("is-invalid");
        mensaje.textContent = "Las contraseñas no coinciden.";
        mensaje.classList.remove("d-none");
    }

    var validarFecha = validarCampo(
        fechaNacimiento,
        function () {
            return validarFormatoFecha(fechaNacimiento.value) && esFechaValida(fechaNacimiento.value);
        },
        validationMessages.fecha
    );

    if (!(
        validarNombre &&
        validarApellidos &&
        validarEmail &&
        validarTelefono &&
        validarPassword &&
        validarRepetirPassword &&
        validarFecha
    ) ){
        event.preventDefault();
    }
});

const msgExito = document.getElementById("modalRegistroOk");

if (msgExito) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalRegistroOk")
    );
    modal.show();
    setTimeout(() => {
        modal.hide();
    }, 2500);
}

const msgEmailRegistrado = document.getElementById("modalErrorActualizar");

if (msgEmailRegistrado) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalErrorActualizar")
    );
    modal.show();
}

document.addEventListener("DOMContentLoaded", function () {
    const deleteBtn = document.getElementById("confirmDeleteBtn");

    deleteBtn.addEventListener("click", function () {
        const url = deleteBtn.dataset.url;

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const confirmModal = bootstrap.Modal.getInstance(
                    document.getElementById("confirmDeleteModal")
                );
                confirmModal.hide();

                const successModal = new bootstrap.Modal(
                    document.getElementById("deletedSuccessModal")
                );
                successModal.show();

                setTimeout(() => {
                    window.location.href = "/";
                }, 2000);
            }
        });
    });
});

const updateModal = document.getElementById('updateProfileModal');

updateModal.addEventListener('hidden.bs.modal', function () {
    const form = updateModal.querySelector('form');
    form.reset();
    resetCampo(nombreRegistro);
    resetCampo(apellidosRegistro);
    resetCampo(telefonoRegistro);
    resetCampo(fechaNacimiento);
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

