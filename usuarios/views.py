from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from django.contrib.auth.decorators import login_required
from .forms import UsuarioForm, ModificarImagenForm  # Asegúrate de importar ModificarImagenForm
from .forms import ProfileForm

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

# Vista para modificar la imagen de perfil
@login_required
def modificar_imagen(request):
    if request.method == 'POST':
        form = ModificarImagenForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')  # Redirige a la página de perfil
    else:
        form = ModificarImagenForm(instance=request.user)
    return render(request, 'usuarios/modificar_imagen.html', {'form': form})

# Vista para mostrar el perfil del usuario
@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

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