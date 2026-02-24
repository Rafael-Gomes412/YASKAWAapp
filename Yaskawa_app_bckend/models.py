from django.db import models

class Category(models.Model):
    name        = models.CharField(max_length=100) 
    slug        = models.SlugField(unique=True)
    image_home  = models.ImageField(upload_to='categories/') # Image pour la page d'accueil

    def __str__(self):
        return self.name

class Product(models.Model):
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Tes champs spécifiques (d'après ton image)
    model_code      = models.CharField(max_length=100) 
    numero_SAP      = models.CharField(max_length=200)
    product_type    = models.CharField(max_length=100)
    features        = models.CharField(max_length=100)
    specification   = models.CharField(max_length=200)
    compatible      = models.CharField(max_length=200)
    usable_with     = models.CharField(max_length=200)
    image           = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return f"{self.model_code} - {self.numero_SAP}"