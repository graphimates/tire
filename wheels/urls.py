from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Importa las vistas que has creado en el views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta principal que enlaza con la vista base
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

