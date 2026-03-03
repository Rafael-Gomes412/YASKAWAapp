from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('product/<str:model_code>/', views.product_detail_view, name='product_detail'),

    # 1. Action de réinitialisation (en haut pour éviter les conflits)
    path('solution/clear/', views.clear_solution, name='clear_solution'),

    # 2. Action d'ajout (avec les deux paramètres : accessoire et parent)
    path('solution/add/<str:model_code>/<str:source_code>/', views.add_to_solution, name='add_to_solution'),

    # 3. Action de suppression (C'est cette ligne qui manquait pour corriger ton erreur !)
    path('solution/remove/<str:model_code>/<str:source_code>/', views.remove_from_solution, name='remove_from_solution'),

    # 4. Page principale du configurateur (en dernier car elle est la plus générique)
    path('solution/<str:model_code>/', views.my_solution_view, name='my_solution'),
    
    # 5. la BOM
    path('solution/export/excel/', views.export_bom_excel, name='export_bom'),
]