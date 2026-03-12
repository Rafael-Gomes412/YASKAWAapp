from django.urls import path
from . import views

urlpatterns = [
    #──────────────────────────────────────────────────────────────
    #Auth
    #──────────────────────────────────────────────────────────────
    path('',          views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('home/',     views.home_view,     name='home'),
    path('logout/',   views.logout_view,   name='logout'),

    #──────────────────────────────────────────────────────────────
    #Import : Mise à jours de la base de données
    #──────────────────────────────────────────────────────────────
    path('import_data/', views.import_data_view, name='import_data'),
    #──────────────────────────────────────────────────────────────
    #Catalogue produit
    #──────────────────────────────────────────────────────────────
    path('category/<slug:slug>/',        views.category_detail_view, name='category_detail'),
    path('product/<str:model_code>/',    views.product_detail_view,  name='product_detail'),
    #──────────────────────────────────────────────────────────────
    #Sélection session
    #──────────────────────────────────────────────────────────────
    path('select-servopack/<str:sp_code>/',       views.select_servopack_view, name='select_servopack'),
    path('select-motor-direct/<str:m_code>/',     views.select_motor_view,     name='select_motor'),
    #──────────────────────────────────────────────────────────────
    #Choix produit manquant
    #──────────────────────────────────────────────────────────────
     path('pick-pair/<str:model_code>/', views.pick_pair_view, name='pick_pair'),
    #──────────────────────────────────────────────────────────────
    #Validation servopack + servomotor
    #──────────────────────────────────────────────────────────────
     path('resume/<str:sp_code>/<str:mt_code>/', views.resume_view, name='resume'),

    
    #──────────────────────────────────────────────────────────────
    #Actions BOM — on n'a besoin que de source_code pour la redirection
    #──────────────────────────────────────────────────────────────
    path('solution/export/excel/', views.export_bom_excel, name='export_bom'),
    path('solution/clear/',        views.clear_solution,   name='clear_solution'),

    #──────────────────────────────────────────────────────────────
    #Configurateur BOM
    #──────────────────────────────────────────────────────────────
    # Route principale : servopack + moteur connus
    path('solution/<str:sp_code>/<str:mt_code>/', views.my_solution_view, name='my_solution'),
    # Route depuis la fiche produit : un seul code (SGD ou SGM)
    path('solution/<str:sp_code>/',               views.my_solution_view, name='my_solution_single'),
    path('solution/add/<str:model_code>/<str:source_code>/',    views.add_to_solution,      name='add_to_solution'),
    path('solution/remove/<str:model_code>/<str:source_code>/', views.remove_from_solution, name='remove_from_solution'),
 
    
]