from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from equipos.models import Equipo
from usuarios.models import Usuario

def breadcrumbs(request):
    """
    Generar breadcrumbs dinámicos según la vista actual y la URL.
    """
    crumbs = [
        {"name": _("Inicio"), "url": reverse("landing")},
    ]

    try:
        resolver_match = resolve(request.path)
        view_name = resolver_match.url_name
        kwargs = resolver_match.kwargs

        # ---------- Nivel 1: sección ----------
        # if view_name in [
        #     "miperfil", "login", "signin", "logout",
        #     "eliminar_cuenta",
        #     "password_forget", "password_forget_done",
        #     "new_password", "new_password_done",
        #     "informacion_equipo"
        # ]:
        #     crumbs.append({
        #         "name": _("Área privada"),
        #         "url": "#"
        #     })

        # ---------- Nivel 2: páginas concretas ----------

        if view_name == "miperfil":
            crumbs.append({"name": _("Mi perfil"), "url": reverse("usuarios:miperfil")})

        elif view_name == "login":
            crumbs.append({"name": _("Iniciar sesión"), "url": reverse("usuarios:login")})

        elif view_name == "signin":
            crumbs.append({"name": _("Registrarse"), "url": reverse("usuarios:signin")})

        elif view_name == "logout":
            crumbs.append({"name": _("Cerrar sesión"), "url": reverse("usuarios:logout")})

        elif view_name == "eliminar_cuenta":
            crumbs.append({"name": _("Eliminar cuenta"), "url": reverse("usuarios:eliminar_cuenta")})

        elif view_name == "password_forget":
            crumbs.append({"name": _("Restablecer contraseña"), "url": reverse("usuarios:password_forget")})

        elif view_name == "password_forget_done":
            crumbs.append({"name": _("Restablecer contraseña"), "url": reverse("usuarios:password_forget_done")})

        elif view_name == "new_password":
            crumbs.append({"name": _("Nueva contraseña"), "url": reverse("usuarios:new_password")})

        elif view_name == "new_password_done":
            crumbs.append({"name": _("Nueva contraseña"), "url": reverse("usuarios:new_password_done")})

        elif view_name == "ver_perfil_usuario":
            slug = kwargs.get("slug")

            if slug:
                usuario = Usuario.objects.get(slug=slug)

                crumbs.append({
                    "name": _("Usuarios"),
                })

                crumbs.append({
                    "name": usuario.get_full_name(),
                    "url": reverse("usuarios:ver_perfil_usuario", args=[slug])
                })

        elif view_name == "informacion_equipo":
            slug = kwargs.get("slug")

            if slug:
                equipo = Equipo.objects.get(slug=slug)

                crumbs.append({
                    "name": _("Equipos"),
                })

                crumbs.append({
                    "name": equipo.nombre,   
                    "url": reverse("equipos:informacion_equipo", args=[slug])
                })

        elif view_name == "pizarra_tactica":
            slug = kwargs.get("slug")

            if slug:
                equipo = Equipo.objects.get(slug=slug)

                crumbs.append({
                    "name": _("Equipos"),
                })

                crumbs.append({
                    "name": equipo.nombre,   
                    "url": reverse("equipos:informacion_equipo", args=[slug])
                })

                crumbs.append({
                    "name": _("Pizarra Táctica"),
                    "url": reverse("equipos:pizarra_tactica", args=[slug])
                })

    except:
        # Si la URL no se resuelve correctamente, mostrar solo Inicio
        pass

    return {"breadcrumbs": crumbs}

