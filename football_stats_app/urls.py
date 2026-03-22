"""
URL configuration for football_stats_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.landing, name="landing"),
    path('auth/', include('usuarios.urls')),
    path('teams/', include('equipos.urls')),
    path("test-400/", views.error_400_test),
    path("test-403/", views.error_403_test),
    path("test-500/", views.error_500_test),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Vistas personalizadas de error
handler404 = 'football_stats_app.views.error_404'
handler500 = 'football_stats_app.views.error_500'
handler403 = 'football_stats_app.views.error_403'
handler400 = 'football_stats_app.views.error_400'
