from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Génère le slug automatiquement quand tu tapes le nom

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('model_code', 'numero_SAP', 'category', 'product_type','features','specification')
    list_filter = ('category', 'product_type') # Filtres pratiques à droite
    search_fields = ('model_code', 'numero_SAP') # Barre de recherche dans l'admin