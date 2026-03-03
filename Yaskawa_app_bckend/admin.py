from django.contrib import admin
from .models import Category, Product, Compatibility

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('model_code', 'numero_SAP', 'category', 'product_type','features','specification')
    list_filter = ('category', 'product_type') # Filtres pratiques à droite
    search_fields = ('model_code', 'numero_SAP') # Barre de recherche dans l'admin

 
@admin.register(Compatibility)
class CompatibilityAdmin(admin.ModelAdmin):
    # Colonnes à afficher dans la liste
    list_display = ('source_product', 'compatible_product', 'relation_type')
    
    # Barre de recherche pour trouver un code modèle précis
    search_fields = ('source_product__model_code', 'compatible_product__model_code')
    
    # Filtre latéral pour trier par type (Moteur, Câble, etc.)
    list_filter = ('relation_type',)  