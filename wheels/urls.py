from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios import views as usuarios_views
from . import views  # Importa las vistas que has creado
from django.conf import settings  # Importar las configuraciones
from django.conf.urls.static import static  # Importar la función para servir archivos estáticos en desarrollo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta principal
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Vista para logout
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),  # Panel de usuario

    # Nuevas rutas
    path('usuarios/ver/', usuarios_views.ver_usuarios, name='ver_usuarios'),
    path('usuarios/eliminar/<int:user_id>/', usuarios_views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/crear/', usuarios_views.crear_usuario, name='crear_usuario'),  # Nueva ruta para crear usuario

    # Ruta para modificar imagen de perfil
    path('usuarios/modificar_imagen/', usuarios_views.modificar_imagen, name='modificar_imagen'),  # Nueva ruta para modificar la imagen de perfil
    path('usuarios/perfil/', usuarios_views.perfil, name='perfil'),


]



# Configuración para servir archivos de medios en desarrollo
if settings.DEBUG:  # Solo se debe agregar en modo DEBUG (desarrollo)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
