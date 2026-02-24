import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .models import Category, Product

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)

        if user is not None:
            if user.is_active:
                login(request, user)
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
        service_nom = request.POST.get('service')

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return render(request, 'auth/register.html', {'error': "Format d'e-mail invalide."})

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

        if service_nom:
            group, created = Group.objects.get_or_create(name=service_nom)
            user.groups.add(group)

        return render(request, 'auth/login.html', {'error': "Compte créé ! Attendez l'activation admin."})
    return render(request, 'auth/register.html')

@login_required
def home_view(request):
    initials = request.user.username[:2].upper()
    categories = Category.objects.all() 
    return render(request, 'home.html', {'initials': initials, 'categories': categories})

@login_required
def category_detail_view(request, slug):
    """ Vue pour afficher les produits d'une catégorie avec recherche et pagination """
    category = get_object_or_404(Category, slug=slug)
    initials = request.user.username[:2].upper()
    is_engineer = request.user.groups.filter(name='Engineer').exists()

    # 1. Récupérer le terme de recherche (?search=...)
    query = request.GET.get('search', '')

    # 2. Filtrer les produits de la catégorie
    products_list = category.products.all()

    # 3. Si une recherche est tapée, on filtre en base de données
    if query:
        # On cherche dans model_code OU numero_SAP (insensible à la casse)
        from django.db.models import Q
        products_list = products_list.filter(
            Q(model_code__icontains=query) | Q(numero_SAP__icontains=query)
        )

    # 4. Configurer la pagination (10 produits par page)
    paginator = Paginator(products_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products_list.html', {
        'category': category,
        'products': page_obj,  # On envoie l'objet paginé
        'initials': initials,
        'is_engineer': is_engineer,
        'search_query': query  # On renvoie la recherche pour la garder dans l'input
    })

def logout_view(request):
    logout(request)
    return redirect('login')