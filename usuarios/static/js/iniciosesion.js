// Mensajes de validación para cada campo
const validationMessages = {
    email_requerido: document.getElementById('msg-email-requerido').textContent,
    contraseña_requerida: document.getElementById('msg-password-requerida').textContent
};

// Función para dar estilo a la validacion
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
        var mensaje = input.nextElementSibling;

        input.classList.remove("is-invalid", "is-valid");
        mensaje.textContent = "";
        mensaje.classList.remove("text-danger", "text-success");
}

// VALIDACIÓN COMPLETA DEL FORMULARIO AL ENVIARLO
const inicioSesionForm = document.getElementById("formulario_inicioSesion");
const contrasenaInicioSesion = document.getElementById("passwordInput");
const emailInicioSesion = document.getElementById("emailInput");

inicioSesionForm.setAttribute("novalidate", true);

inicioSesionForm.addEventListener("submit", function(event) {
    
    resetCampo(emailInicioSesion);
    resetCampo(contrasenaInicioSesion);
    
    let valido = true;

    if (emailInicioSesion.value.trim() === "") {
        validarCampo(
            emailInicioSesion,
            () => false,
            validationMessages.email_requerido
        );
        valido = false;
    }

    if (contrasenaInicioSesion.value.trim() === "") {
        validarCampo(
            contrasenaInicioSesion,
            () => false,
            validationMessages.contraseña_requerida
        );
        valido = false;
    }

    if (!valido) {
        event.preventDefault();
        return; 
    }
}
);

const msgExito = document.getElementById("modalInicioSesionOk");

if (msgExito) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalInicioSesionOk")
    );
    modal.show();
    setTimeout(() => {
        window.location.href = "/"; // o landing
    }, 2500);
}

const msgError = document.getElementById("modalErrorInicioSesion");

if (msgError) {
    const modal = new bootstrap.Modal(
        document.getElementById("modalErrorInicioSesion")
    );
    modal.show();
}