from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .models import Usuario, PerfilJugador, PerfilEntrenador
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext_lazy as _

def login_view(request):
    if request.method == "GET":
        return render(request, 'usuarios/login.html')

    # POST → procesar login
    email = request.POST.get('email')
    password = request.POST.get('password')

    # Autenticación
    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, _("Sesión inciada correctamente."))
        return render(request, "usuarios/login.html")  # o dashboard
    else:
        return render(request, 'usuarios/login.html', {'error': _("El usuario no existe o la contraseña es incorrecta."), "email_value": email})

def signin(request):
    if request.method == "GET":
        return render(request, 'usuarios/signin.html')
    else:
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        fechanacimiento = request.POST.get('fechanacimiento')
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')
        es_entrenador = request.POST.get('es_entrenador') 
        # Archivos: Las imágenes van en request.FILES, no en POST
        foto = request.FILES.get('foto') 

        if password_1 != password_2:
            return render(request, 'usuarios/signin.html', {'error': _("Las contraseñas no coinciden."), 'nombre_value': nombre, 'apellidos_value': apellidos, 'telefono_value': telefono, 'email_value': email, 'fechanacimiento_value': fechanacimiento, 'es_entrenador_value': es_entrenador, 'foto_value': foto})
        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'usuarios/signin.html', {'error': _("Este correo electrónico ya está registrado."), 'nombre_value': nombre, 'apellidos_value': apellidos, 'telefono_value': telefono, 'email_value': email, 'fechanacimiento_value': fechanacimiento, 'es_entrenador_value': es_entrenador, 'foto_value': foto})

        # Crear el Usuario
        try:
            # Usamos 'create_user' que se encarga de encriptar la contraseña automáticamente
            user = Usuario.objects.create_user(
                username=email, # Usamos el email como username interno
                first_name=nombre,
                last_name=apellidos,
                telefono=telefono,
                fecha_nacimiento=fechanacimiento,
                email=email,
                password=password_1,
                foto=foto
            )

            # Asignar Rol y Crear Perfil Específico
            if es_entrenador:
                user.rol = Usuario.Rol.ENTRENADOR
                # Creamos la ficha de entrenador vacía asociada a este usuario
                PerfilEntrenador.objects.create(usuario=user)
            else:
                user.rol = Usuario.Rol.JUGADOR
                # Creamos la ficha de jugador vacía asociada a este usuario
                PerfilJugador.objects.create(usuario=user)
            
            user.save()

            # Iniciar sesión automáticamente y redirigir
            login(request, user)
            messages.success(request, _("Te has registrado correctamente"))
            # Redirigir a la página de inicio
            return redirect('landing')

        except Exception as e:
            # Si pasa algo raro, mostramos el error
            return render(request, 'usuarios/signin.html', {'error': _("Error al registrar: {}").format(str(e))})

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def miperfil(request):
    """Ver y editar mi propio perfil"""
    user = request.user

    try:
        if request.method == "POST":
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.telefono = request.POST.get("telefono")
            user.fecha_nacimiento = request.POST.get("fecha_nacimiento")

            if "foto" in request.FILES:
                user.foto = request.FILES["foto"]

            user.save()
            messages.success(request, _("Perfil actualizado correctamente"))
            return redirect("usuarios:miperfil")

        context = {
            'usuario_perfil': user,
            'es_mi_perfil': True,
        }
        return render(request, "usuarios/miperfil.html", context)
    except Exception as e:
        return render(request, 'usuarios/miperfil.html', {'error': _("Error al actualizar: {}").format(str(e))})

@login_required
def ver_perfil_usuario(request, slug):
    """Ver el perfil de otro usuario usando slug"""
    usuario = get_object_or_404(Usuario, slug=slug)
    
    # Obtener información adicional según el rol
    perfil_jugador = None
    perfil_entrenador = None
    
    if usuario.rol == 'jugador':
        perfil_jugador = usuario.perfil_jugador
    elif usuario.rol == 'entrenador':
        perfil_entrenador = usuario.perfil_entrenador
    
    context = {
        'usuario_perfil': usuario,
        'perfil_jugador': perfil_jugador,
        'perfil_entrenador': perfil_entrenador,
        'es_mi_perfil': usuario == request.user,
    }
    return render(request, 'usuarios/miperfil.html', context)
    
@login_required
def eliminar_cuenta(request):
    if request.method == "POST":
        user = request.user
        logout(request)          # cerrar sesión primero
        user.delete()            # eliminar usuario
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'usuarios/password_forget.html'
    email_template_name = 'usuarios/password_forget_email.html'
    subject_template_name = 'usuarios/password_forget_subject.txt'
    success_url = reverse_lazy('usuarios:password_forget_done')
    html_email_template_name = 'usuarios/password_forget_email.html'

    def dispatch(self, request, *args, **kwargs):
        # Si el usuario YA está logueado, enviamos el correo directamente
        if request.user.is_authenticated:
            form = PasswordResetForm({'email': request.user.email})

            if form.is_valid():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    subject_template_name = self.subject_template_name,
                    email_template_name=self.email_template_name,
                    html_email_template_name=self.html_email_template_name,
                )

                messages.success(
                    request,
                    _("Te hemos enviado un correo para cambiar tu contraseña.")
                )

                return redirect("usuarios:miperfil")

        # Si NO está logueado, seguimos el flujo normal de Django
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "usuarios/new_password.html"
    success_url = reverse_lazy("usuarios:new_password_done")