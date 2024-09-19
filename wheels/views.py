from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# Vista para el login
def login_view(request):
    if request.user.is_authenticated:
        print("Usuario ya autenticado")
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')  # Usamos 'email' en lugar de 'username'
        password = request.POST.get('password')
        print(f"Autenticando usuario con email: {email}")

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            print("Autenticación exitosa, iniciando sesión")
            login(request, user)
            # Redirigir a los usuarios según si son admin o usuarios normales
            if user.is_superuser:  # Si es un administrador
                return redirect('index')
            else:  # Si es un usuario común
                return redirect('user_dashboard')  # Página para usuarios comunes
        else:
            print("Autenticación fallida")
            return render(request, 'login.html', {'error': 'Credenciales incorrectas.'})
    
    return render(request, 'login.html')

# Vista para el index (admin panel)
@login_required
def index(request):
    return render(request, 'index.html')

# Vista para usuarios normales (user_dashboard)
@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')
