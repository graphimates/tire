from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios import views as usuarios_views
from . import views  # Importa las vistas que has creado



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta principal
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Vista para logout
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),  # Panel de usuario
    

     # Nuevas rutas
    path('usuarios/ver/', usuarios_views.ver_usuarios, name='ver_usuarios'),    
    path('usuarios/editar/<int:user_id>/', usuarios_views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', usuarios_views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/crear/', usuarios_views.crear_usuario, name='crear_usuario'),  # Nueva ruta para crear usuario
]


