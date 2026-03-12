from django.contrib import admin
from .models import Category, Product, Compatibility, ProductSpec,ProductFamily

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductSpecInline(admin.StackedInline):
    model = ProductSpec
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('model_code', 'numero_SAP', 'category', 'product_type', 'features', 'specification')
    list_filter   = ('category', 'product_type')
    search_fields = ('model_code', 'numero_SAP')
    inlines       = [ProductSpecInline]

@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display  = ('product', 'series', 'power_kw', 'voltage', 'protocol', 'encoder_type', 'brake')
    list_filter   = ('voltage', 'protocol', 'series', 'brake')
    search_fields = ('product__model_code', 'series')

@admin.register(Compatibility)
class CompatibilityAdmin(admin.ModelAdmin):
    list_display  = ('source_product', 'compatible_product', 'relation_type')
    search_fields = ('source_product__model_code', 'compatible_product__model_code')
    list_filter   = ('relation_type',)

@admin.register(ProductFamily)
class ProductFamilyAdmin(admin.ModelAdmin):
    list_display  = ('prefix', 'name', 'image')
    search_fields = ('prefix', 'name')
    ordering      = ('prefix',)