from django.db import models

class Category(models.Model):
    name        = models.CharField(max_length=100) 
    slug        = models.SlugField(unique=True)
    image_home  = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class Product(models.Model):
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    model_code      = models.CharField(max_length=100, unique=True) 
    numero_SAP      = models.CharField(max_length=200)
    product_type    = models.CharField(max_length=100)
    features        = models.TextField(blank=True, null=True)
    specification   = models.TextField(blank=True, null=True)
    compatible      = models.TextField(blank=True, null=True)
    usable_with     = models.TextField(blank=True, null=True)
    image           = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return f"{self.model_code} - {self.numero_SAP}"
    
class Compatibility(models.Model):
    source_product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='source_relations',
        verbose_name="Produit Maitre"
    )
    compatible_product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='compatible_relations',
        verbose_name="Equipement Compatible"
    )
    relation_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Type de liaison"
    )

    class Meta:
        verbose_name = "Compatibilité"
        verbose_name_plural = "Compatibilités"
        unique_together = ('source_product', 'compatible_product', 'relation_type')

    def __str__(self):
        return f"{self.source_product.model_code} -> {self.compatible_product.model_code} ({self.relation_type})"