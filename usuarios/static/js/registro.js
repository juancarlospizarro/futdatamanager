// Mensajes de validación
const validationMessages = {
        nombre: document.getElementById('msg-nombre').textContent,
        apellidos: document.getElementById('msg-apellidos').textContent,
        email: document.getElementById('msg-email').textContent,
        telefono_rango: document.getElementById('msg-telefono-rango').textContent,
        telefono_exacto: document.getElementById('msg-telefono-exacto').textContent,
        contraseña_requisitos: document.getElementById('msg-contraseña-requisitos').textContent,
        contraseña_coinciden: document.getElementById('msg-contraseña-coinciden').textContent,
        fecha: document.getElementById('msg-fecha').textContent,
        terminos: document.getElementById('msg-terminos').textContent
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
const emailRegistro = document.getElementById("emailInput");

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
        validationMessages.telefono_rango
    );
});

// VALIDACIÓN TIEMPO REAL CAMPO CONTRASEÑA
const passwordRegistro = document.getElementById("passwordInput1");
const reglasPassword = document.getElementById("reglasPassword");
const reglaLongitud = document.getElementById("reglaLongitud");
const reglaMayuscula = document.getElementById("reglaMayuscula");
const reglaNumero = document.getElementById("reglaNumero");
const reglaEspecial = document.getElementById("reglaEspecial");

passwordRegistro.addEventListener("input", function () {
    const valor = passwordRegistro.value;
    const textoSubmit = document.getElementById("textoSubmit");

    if (valor.length === 0) {
        resetCampo(passwordRegistro);

        reglasPassword.classList.add("d-none");
        textoSubmit.classList.add("d-none");

        [reglaLongitud, reglaMayuscula, reglaNumero, reglaEspecial].forEach(function (regla) {
            regla.classList.remove("text-success");
            regla.classList.add("text-danger");
        });

        return;
    }

    if (passwordRegistro.value.length > 20) {
        passwordRegistro.value = passwordRegistro.value.slice(0, 20);
    }

    reglasPassword.classList.remove("d-none");

    const okLongitud = valor.length >= 6;
    const okMayuscula = /[A-Z]/.test(valor);
    const okNumero = /[0-9]/.test(valor);
    const okEspecial = /[!@#$%^&*()_+\-=[\]{};:'",.<>/?\\|]/.test(valor);

    reglaLongitud.classList.toggle("text-success", okLongitud);
    reglaLongitud.classList.toggle("text-danger", !okLongitud);

    reglaMayuscula.classList.toggle("text-success", okMayuscula);
    reglaMayuscula.classList.toggle("text-danger", !okMayuscula);

    reglaNumero.classList.toggle("text-success", okNumero);
    reglaNumero.classList.toggle("text-danger", !okNumero);

    reglaEspecial.classList.toggle("text-success", okEspecial);
    reglaEspecial.classList.toggle("text-danger", !okEspecial);

    if (okLongitud && okMayuscula && okNumero && okEspecial) {
        passwordRegistro.classList.add("is-valid");
        passwordRegistro.classList.remove("is-invalid");
        textoSubmit.classList.add("d-none");
    } else {
        passwordRegistro.classList.add("is-invalid");
        passwordRegistro.classList.remove("is-valid");
    }
});

// VALIDACIÓN TIEMPO REAL CAMPO REPETIR CONTRASEÑA
const repetirContrasena = document.getElementById("passwordInput2");

repetirContrasena.addEventListener("input", function () {
    const valor = repetirContrasena.value;
    const original = passwordRegistro.value;
    const mensaje = repetirContrasena.nextElementSibling;

    if (valor.length === 0) {
        resetCampo(repetirContrasena);
        return;
    }

    if (repetirContrasena.value.length > 20) {
        repetirContrasena.value = repetirContrasena.value.slice(0, 20);
    }

    if (valor === original) {
        repetirContrasena.classList.add("is-valid");
        repetirContrasena.classList.remove("is-invalid");
        mensaje.textContent = "";
        mensaje.classList.add("d-none");
    } else {
        repetirContrasena.classList.add("is-invalid");
        repetirContrasena.classList.remove("is-valid");
        mensaje.textContent = validationMessages.contraseña_coinciden;
        mensaje.classList.remove("d-none");
    }
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

// VALIDACIÓN TIEMPO REAL CAMPO TÉRMINOS Y CONDICIONES
const terminosCheckbox = document.getElementById("terminos");
const errorTerminos = document.getElementById("errorTerminos");
const btnAceptarTerminos = document.getElementById("aceptarTerminos");

/* Aceptación de los términos desde el modal */
btnAceptarTerminos.addEventListener("click", function () {
    terminosCheckbox.checked = true;
    errorTerminos.textContent = "";
    terminosCheckbox.classList.remove("is-invalid");
    terminosCheckbox.classList.add("is-valid");
    
    const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalTerminos")
    );
    modal.hide();
});

terminosCheckbox.addEventListener("change", function () {
    if (terminosCheckbox.checked) {
        errorTerminos.textContent = "";
        terminosCheckbox.classList.remove("is-invalid");
        terminosCheckbox.classList.add("is-valid");
    } else {
        errorTerminos.textContent = validationMessages.terminos;
        terminosCheckbox.classList.add("is-invalid");
        terminosCheckbox.classList.remove("is-valid");
    }
});

// VALIDACIÓN COMPLETA DEL FORMULARIO AL ENVIARLO
const registroForm = document.getElementById("formulario_registro");

registroForm.setAttribute("novalidate", true);

registroForm.addEventListener("submit", function (event) {

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
        validationMessages.contraseña_requisitos
    );

    var validarRepetirPassword = 
        repetirContrasena.value.length > 0 &&
        repetirContrasena.value === passwordRegistro.value;

    if (!validarRepetirPassword) {
        const mensaje = repetirContrasena.nextElementSibling;
        repetirContrasena.classList.add("is-invalid");
        mensaje.textContent = validationMessages.contraseña_coinciden;
        mensaje.classList.remove("d-none");
    }

    var validarFecha = validarCampo(
        fechaNacimiento,
        function () {
            return validarFormatoFecha(fechaNacimiento.value) && esFechaValida(fechaNacimiento.value);
        },
        validationMessages.fecha
    );

    const validarTerminos = terminosCheckbox.checked;

    if (!validarTerminos) {
        errorTerminos.textContent = validationMessages.terminos;
    }

    if (!(
        validarNombre &&
        validarApellidos &&
        validarEmail &&
        validarTelefono &&
        validarPassword &&
        validarRepetirPassword &&
        validarFecha &&
        validarTerminos
    ) ){
        event.preventDefault();
    }
});

const msgExito = document.getElementById("msgRegistro");

if (msgExito) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalRegistroOk")
    );
    modal.show();
    setTimeout(() => {
        window.location.href = "/"; // o landing
    }, 2500);
}

const msgEmailRegistrado = document.getElementById("modalEmailExiste");

if (msgEmailRegistrado) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalEmailExiste")
    );
    modal.show();
}