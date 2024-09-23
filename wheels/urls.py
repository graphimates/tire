from django.contrib import admin
from django.urls import path, include  # Agregamos include
from django.contrib.auth import views as auth_views
from usuarios import views as usuarios_views
from . import views  # Importa las vistas que has creado
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    # Rutas de usuarios
    path('usuarios/ver/', usuarios_views.ver_usuarios, name='ver_usuarios'),    
    path('usuarios/editar/<int:user_id>/', usuarios_views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', usuarios_views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/crear/', usuarios_views.crear_usuario, name='crear_usuario'),

    # Incluir las rutas de vehículos
    path('vehiculos/', include('vehiculos.urls')),  # Incluye las rutas de la app vehiculos
    path('usuarios/perfil/', usuarios_views.perfil, name='perfil'),
    path('usuarios/modificar_imagen/', usuarios_views.modificar_imagen, name='modificar_imagen'),
    path('perfil/', usuarios_views.perfil_usuario, name='perfil_usuario'),

]

if settings.DEBUG:  # Solo se debe agregar en modo DEBUG (desarrollo)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)