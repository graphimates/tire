from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UsuarioForm
from django.views.decorators.cache import never_cache  # Importamos el decorador para deshabilitar la caché
from .forms import ModificarImagenForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm


# Función para verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

# Vista para mostrar los usuarios en una tabla
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def ver_usuarios(request):
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios/ver_usuarios.html', {'usuarios': usuarios})

# Vista para eliminar un usuario
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        usuario.delete()  # Eliminar el usuario
        return redirect('ver_usuarios')  # Redirigir de nuevo a la lista de usuarios
    return render(request, 'usuarios/eliminar_confirmacion.html', {'usuario': usuario})

# Vista para la página de creación de usuarios
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)  # Agregar request.FILES
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])  # Encriptar la contraseña
            usuario.save()
            return redirect('ver_usuarios')  # Redirigir a la lista de usuarios después de la creación
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

# Vista para editar un usuario
@login_required
@user_passes_test(is_admin)  # Solo administradores pueden acceder
@never_cache  # Deshabilitar la caché
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)  # Obtener el usuario por ID
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)  # Cargar el formulario con los datos existentes
        if form.is_valid():
            form.save()
            return redirect('ver_usuarios')  # Redirigir a la lista de usuarios después de la edición
    else:
        form = UsuarioForm(instance=usuario)  # Precargar el formulario con los datos del usuario
    return render(request, 'usuarios/crear_usuario.html', {'form': form, 'titulo': f'Editando al usuario {usuario.first_name}'})



@login_required
def modificar_imagen(request):
    if request.method == 'POST':
        form = ModificarImagenForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')  # Redirige a una página de perfil o donde prefieras
    else:
        form = ModificarImagenForm(instance=request.user)
    return render(request, 'usuarios/modificar_imagen.html', {'form': form})


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')


@login_required
def perfil_usuario(request):
    usuario = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = ProfileForm(instance=usuario)
    return render(request, 'usuarios/perfil_usuario.html', {'form': form})