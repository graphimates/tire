from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from django.contrib.auth.decorators import login_required

# Vista para mostrar los usuarios en una tabla
@login_required
def ver_usuarios(request):
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios/ver_usuarios.html', {'usuarios': usuarios})

# Vista para eliminar un usuario
@login_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.delete()  # Eliminar el usuario
        return redirect('ver_usuarios')  # Redirigir de nuevo a la lista de usuarios
    return render(request, 'usuarios/eliminar_confirmacion.html', {'usuario': usuario})

# Vista para la página de creación de usuarios
@login_required
def crear_usuario(request):
    return render(request, 'usuarios/crear_usuario.html')
