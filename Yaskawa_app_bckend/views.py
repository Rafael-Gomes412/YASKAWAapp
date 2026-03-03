#-------------------------------------------------------------------
# YASKAWAapp_bckend/views.py
#-------------------------------------------------------------------
import re
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Compatibility
from django.http import HttpResponse
from datetime import datetime

#-------------------------------------------------------------------
# 1. Vue de connexion
#-------------------------------------------------------------------
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

#-------------------------------------------------------------------
# 2. Vue d'inscription avec validation
#-------------------------------------------------------------------
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

#-------------------------------------------------------------------
# 3. Vues protégées (accès après connexion)
#-------------------------------------------------------------------
@login_required
def home_view(request):
    initials = request.user.username[:2].upper()
    categories = Category.objects.all() 
    return render(request, 'home.html', {'initials': initials, 'categories': categories})

@login_required
def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    initials = request.user.username[:2].upper()
    is_engineer = request.user.groups.filter(name='Engineer').exists()

    query = request.GET.get('search', 'SGD')

    products_list = category.products.all()

    if query:
        from django.db.models import Q
        products_list = products_list.filter(
            Q(model_code__icontains=query) | Q(numero_SAP__icontains=query)
        )

    paginator = Paginator(products_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products_list.html', {
        'category': category,
        'products': page_obj,
        'initials': initials,
        'is_engineer': is_engineer,
        'search_query': query
    })

def product_detail_view(request, model_code):
    product = get_object_or_404(Product, model_code=model_code)
    return render(request, 'product_detail.html', {'product': product})

#-------------------------------------------------------------------
# 4. Gestion du Configurateur (BOM)
#-------------------------------------------------------------------
def my_solution_view(request, model_code):

    # ── Produit source ──────────────────────────────────────────────────────
    main_product = get_object_or_404(Product, model_code=model_code)
    main_ref     = main_product.model_code.upper()

    # ── Gestion session (BOM) ───────────────────────────────────────────────
    current_source = request.session.get('current_source_code')
    if current_source != model_code:
        request.session['bom_list']           = []
        request.session['current_source_code'] = model_code
        request.session.modified               = True

    bom_list = request.session.get('bom_list', [])

    # ── Produits compatibles (hors BOM déjà ajoutés) ───────────────────────
    all_compatibilities = Compatibility.objects.filter(
        source_product=main_product
    ).select_related('compatible_product').exclude(
        compatible_product__model_code__in=bom_list
    )

    # ── Initialisation ──────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = [], [], [], []
    titles = {"t1": "", "t2": "", "t3": "", "t4": ""}

    # ────────────────────────────────────────────────────────────────────────
    # FONCTION DE CLASSIFICATION HYBRIDE
    # Priorité 1 : product_type   → rapide et sémantique
    # Priorité 2 : model_code     → nomenclature Yaskawa précise (fallback)
    # ────────────────────────────────────────────────────────────────────────
    def classify(comp):
        """
        Retourne : 'motor' | 'servopack' | 'encoder_cable'
                   | 'power_cable' | 'accessory'
        """
        ref  = comp.compatible_product.model_code.upper()
        ptype = (getattr(comp.compatible_product, 'product_type', '') or '').lower()

        # ── Priorité 1 : product_type ────────────────────────────────────
        if 'motor' in ptype:
            return 'motor'
        if 'servopack' in ptype:
            return 'servopack'
        if 'encoder' in ptype:
            return 'encoder_cable'
        if 'power' in ptype:
            return 'power_cable'

        # ── Priorité 2 : model_code (nomenclature Yaskawa) ───────────────
        # Moteur
        if ref.startswith('SGM'):
            return 'motor'
        # Servopack
        if ref.startswith('SGD'):
            return 'servopack'
        # Câble codeur — JZSP-CS / JZSP-S uniquement (exclut JZSP-CV)
        if ref.startswith('JZSP-CS') or ref.startswith('JZSP-S'):
            return 'encoder_cable'
        # Câble puissance
        if ref.startswith('JZSP-M') or ref.startswith('JZSP-U') or 'CBK' in ref:
            return 'power_cable'

        # Tout le reste (JZSP-CV, SGDXS, KLBUE, modules…) → Accessories
        return 'accessory'

    # ── CAS A : Source = SERVOPACK (SGD…) ──────────────────────────────────
    if main_ref.startswith('SGD'):
        titles = {
            "t1": "Motor",
            "t2": "Encoder Cable",
            "t3": "Power Cable",
            "t4": "Accessories",
        }
        for comp in all_compatibilities:
            category = classify(comp)
            if category == 'motor':
                tab1.append(comp)
            elif category == 'encoder_cable':
                tab2.append(comp)
            elif category == 'power_cable':
                tab3.append(comp)
            else:                          # servopack inattendu + accessory
                tab4.append(comp)

    # ── CAS B : Source = MOTEUR (SGM…) ─────────────────────────────────────
    elif main_ref.startswith('SGM'):
        titles = {
            "t1": "Servopack",
            "t2": "Encoder Cable",
            "t3": "Power Cable",
            "t4": "Accessories",
        }
        for comp in all_compatibilities:
            category = classify(comp)
            if category == 'servopack':
                tab1.append(comp)
            elif category == 'encoder_cable':
                tab2.append(comp)
            elif category == 'power_cable':
                tab3.append(comp)
            else:                          # motor inattendu + accessory
                tab4.append(comp)

    # ── CAS C : Autre type de produit source ────────────────────────────────
    else:
        titles = {"t1": "Compatibles", "t2": "-", "t3": "-", "t4": "-"}
        tab1   = list(all_compatibilities)

    # ── Rendu ───────────────────────────────────────────────────────────────
    return render(request, 'my_solution.html', {
        'main_product': main_product,
        'tab1': tab1,
        'tab2': tab2,
        'tab3': tab3,
        'tab4': tab4,
        'titles': titles,
    })
#-------------------------------------------------------------------
# 5. BOM
#-------------------------------------------------------------------


def export_bom_excel(request):
    # 1. Récupérer les codes produits (Source + BOM)
    main_code = request.session.get('current_source_code')
    bom_list = request.session.get('bom_list', [])
    
    if not main_code:
        return HttpResponse("Aucune configuration à exporter.")

    # 2. Créer le classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BOM Yaskawa"

    # 3. Design : En-têtes
    headers = ['Modèle', 'Type de Produit', 'Description / Spécification']
    ws.append(['LISTE DE MATÉRIEL (BOM) - CONFIGURATEUR YASKAWA']) # Titre
    ws.append([f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    ws.append([]) # Ligne vide
    ws.append(headers)

    # 4. Récupérer les données en base
    all_codes = [main_code] + bom_list
    products = Product.objects.filter(model_code__in=all_codes)

    # 5. Remplir le tableau
    for prod in products:
        ws.append([
            prod.model_code,
            prod.product_type,
            prod.specification if hasattr(prod, 'specification') else ""
        ])

    # 6. Mise en forme rapide (Largeur des colonnes)
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 50

    # 7. Préparer la réponse HTTP pour le téléchargement
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="BOM_{main_code}.xlsx"'
    
    wb.save(response)
    return response
#-------------------------------------------------------------------
# 6. Gestion ADD
#-------------------------------------------------------------------

def add_to_solution(request, model_code, source_code):
    """ Ajoute un accessoire et redirige vers le parent pour continuer la sélection """
    if 'bom_list' not in request.session:
        request.session['bom_list'] = []
    
    bom_list = request.session['bom_list']
    if model_code not in bom_list:
        bom_list.append(model_code)
        request.session.modified = True
        
    return redirect('my_solution', model_code=source_code)

def remove_from_solution(request, model_code, source_code):
    """ Supprime un élément spécifique de la BOM (croix rouge) """
    if 'bom_list' in request.session:
        bom_list = request.session['bom_list']
        if model_code in bom_list:
            bom_list.remove(model_code)
            request.session.modified = True
    return redirect('my_solution', model_code=source_code)

def clear_solution(request):
    """ Réinitialise complètement la configuration en cours """
    if 'bom_list' in request.session:
        del request.session['bom_list']
    if 'current_source_code' in request.session:
        del request.session['current_source_code']
    return redirect('home')

#-------------------------------------------------------------------
# 5. Déconnexion
#-------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')