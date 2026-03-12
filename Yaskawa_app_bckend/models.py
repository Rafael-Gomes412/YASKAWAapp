from django.db import models

class Category(models.Model):
    name        = models.CharField(max_length=100) 
    slug        = models.SlugField(unique=True)
    image_home  = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name
    
class ProductFamily (models.Model):
    prefix         = models.CharField(max_length=10, unique=True)
    image          = models.ImageField(upload_to='families/')
    name           = models.CharField(max_length=100)
    class Meta:
        verbose_name        ="Famille Produit"
        verbose_name_plural = "Familles Produit"
        ordering            =['prefix']

    def __str__(self):
        return f"{self.prefix} - {self.name}"
    
class Product(models.Model):
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    model_code      = models.CharField(max_length=100, unique=True) 
    numero_SAP      = models.CharField(max_length=200)
    product_type    = models.CharField(max_length=100)
    features        = models.TextField(blank=True, null=True)
    specification   = models.TextField(blank=True, null=True)
    compatible      = models.TextField(blank=True, null=True)
    usable_with     = models.TextField(blank=True, null=True)
    compat_range_1  = models.TextField(blank=True, null=True)
    compat_range_2  = models.TextField(blank=True, null=True)
    compat_range_3  = models.TextField(blank=True, null=True)
    compat_range_4  = models.TextField(blank=True, null=True)
    compat_range_5  = models.TextField(blank=True, null=True)
    compat_range_6  = models.TextField(blank=True, null=True)
    compat_range_7  = models.TextField(blank=True, null=True)
    compat_range_8  = models.TextField(blank=True, null=True)
    compat_range_9  = models.TextField(blank=True, null=True)
    compat_range_10 = models.TextField(blank=True, null=True)
    compat_range_11 = models.TextField(blank=True, null=True)
    image           = models.ImageField(upload_to='products/', blank=True)
    in_stock = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.model_code} - {self.numero_SAP}"
   
    @property
    def display_image(self):
 
        if self.image:
            return self.image.url
        for length in [5, 4, 3]:
            family = ProductFamily.objects.filter(
                prefix=self.model_code[:length]
            ).first()
            if family and family.image:
                return family.image.url
        return None
    
class ProductSpec(models.Model):

    product        = models.OneToOneField(
        'Product',
        on_delete=models.CASCADE,
        related_name='spec'
    )

    series         = models.CharField(max_length=50,  blank=True, null=True)
    power_kw       = models.FloatField(null=True, blank=True)
    voltage        = models.CharField(max_length=20,  blank=True, null=True)
    protocol       = models.CharField(max_length=50,  blank=True, null=True)
    encoder_type   = models.CharField(max_length=20,  blank=True, null=True)
    option         = models.CharField(max_length=50,  blank=True, null=True)
    specification  = models.CharField(max_length=50,  blank=True, null=True)
    brake          = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Specification'

    def __str__(self):
        return f"{self.product.model_code} | {self.series} {self.power_kw}kW {self.voltage}"
    
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