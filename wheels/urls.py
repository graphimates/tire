from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Importa las vistas que has creado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta principal
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Vista para logout
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),  # Panel de usuario
]


