import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)

        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirection : Admin vers Django Admin, les autres vers Home
                if user.is_superuser:
                    return redirect('/admin/')
                return redirect('home')
            else:
                return render(request, 'auth/login.html', {'error': "Compte en attente d'activation par un administrateur."})
        else:
            return render(request, 'auth/login.html', {'error': "Identifiants invalides."})
    return render(request, 'auth/login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        pwd = request.POST.get('password')
        cpwd = request.POST.get('confirm_password')

        # Validation Format Email
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return render(request, 'auth/register.html', {'error': "Format d'e-mail invalide."})

        # Validation Mot de passe (12 car, Maj, Min, Chiffre, Spécial)
        reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#.])[A-Za-z\d@$!%*?&#.]{12,}$"
        if not re.match(reg, pwd):
            return render(request, 'auth/register.html', {'error': "MDP : 12 car. min, 1 Maj, 1 Min, 1 Chiffre, 1 Spécial."})
        
        if pwd != cpwd:
            return render(request, 'auth/register.html', {'error': "Les mots de passe ne correspondent pas."})

        if User.objects.filter(username=email).exists():
            return render(request, 'auth/register.html', {'error': "Cet e-mail est déjà utilisé."})

        user = User.objects.create_user(username=email, email=email, password=pwd)
        user.is_active = False 
        user.save()
        return render(request, 'auth/login.html', {'error': "Compte créé ! Attendez l'activation admin."})
    return render(request, 'auth/register.html')

@login_required
def home_view(request):
    # Récupération des deux premières lettres pour le rond de profil
    initials = request.user.username[:2].upper()
    categories = [
        {'name': 'Drive', 'img': 'Drive.png'},
        {'name': 'Motion', 'img': 'Motion.png'},
        {'name': 'Control', 'img': 'Control.png'},
        {'name': 'Robotic', 'img': 'Robotic.png'},
    ]
    return render(request, 'home.html', {'initials': initials, 'categories': categories})

def logout_view(request):
    logout(request)
    return redirect('login')