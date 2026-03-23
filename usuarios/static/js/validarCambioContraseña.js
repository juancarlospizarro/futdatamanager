// Mensajes de validación para cada campo
const validationMessages = {
    contraseña_requisitos: document.getElementById('msg-contraseña-requisitos').textContent,
    contraseña_coinciden: document.getElementById('msg-contraseña-coinciden').textContent
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

// VALIDACIÓN TIEMPO REAL CAMPO CONTRASEÑA
const passwordRegistro = document.getElementById("id_new_password1");
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
const repetirContrasena = document.getElementById("id_new_password2");

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

// VALIDACIÓN COMPLETA DEL FORMULARIO AL ENVIARLO
const validarForm = document.getElementById("formulario_cambio_contrasena");

validarForm.setAttribute("novalidate", true);

validarForm.addEventListener("submit", function (event) {

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

    if (!(
        validarPassword &&
        validarRepetirPassword
    ) ){
        event.preventDefault();
    }
});