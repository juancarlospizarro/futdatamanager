// Mensajes de validación para cada campo
const validationMessages = {
    email: document.getElementById('msg-email').textContent
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


// VALIDACIÓN COMPLETA DEL FORMULARIO AL ENVIARLO
const validarForm = document.getElementById("emailCambioContraseña");

validarForm.setAttribute("novalidate", true);

validarForm.addEventListener("submit", function (event) {

    var validarEmail = validarCampo(
        emailRegistro,
        function () {
            return /^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(emailRegistro.value);
        },
        validationMessages.email
    );

    if (!
        validarEmail
        ){
        event.preventDefault();
    }
});