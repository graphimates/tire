from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Importa las vistas que has creado en el views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta principal que enlaza con la vista base
    path('login/', views.login_view, name='login'),  # Vista de login
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),  # Vista del panel de usuario
]
