import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Gestion des Utilisateurs et Rôles ---

class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=100) # Admin, Commercial, Ingenieur...

    def __str__(self):
        return self.role_name

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    department = models.CharField(max_length=50, null=True, blank=True)
    access_level = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="users")

    def __str__(self):
        return self.username

# --- Catalogue Produits ---

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=150, unique=True) # Motor, Drive, Cable...
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.category_name

class Series(models.Model):
    series_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series_name = models.CharField(max_length=50, unique=True) # Sigma 5, 7, 10...
    start_year = models.DateTimeField()
    end_year = models.DateTimeField(null=True, blank=True)

class Product(models.Model):
    PRODUCT_TYPES = [
        ('Motor', 'Motor'),
        ('Drive', 'Drive'),
        ('Cables', 'Cables'),
        ('Accessory', 'Accessory'),
    ]
    STATUS_CHOICES = [('Active', 'Active'), ('Obsolete', 'Obsolete')]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_code = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=150)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    power_rating = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    voltage = models.CharField(max_length=20, null=True, blank=True)
    current = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')
    release_date = models.DateField(null=True, blank=True)
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"

# --- Support Technique et Compatibilité ---

class Migration(models.Model):
    MIGRATION_TYPES = [('Direct', 'Direct'), ('Equivalent', 'Equivalent'), ('Recommended', 'Recommended')]
    
    migration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    old_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="obsolete_versions")
    new_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="replacement_versions")
    migration_type = models.CharField(max_length=20, choices=MIGRATION_TYPES)
    note = models.TextField(null=True, blank=True)

class CompatibilityRule(models.Model):
    STATUS_CHOICES = [('Compatible', 'Compatible'), ('Not_Compatible', 'Not_Compatible'), ('Conditional', 'Conditional')]
    
    rule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_a = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="compatibility_a")
    product_b = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="compatibility_b")
    compatibility_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    condition = models.TextField(null=True, blank=True)
    validated = models.BooleanField(default=False)

class Error(models.Model):
    SEVERITY_CHOICES = [('Info', 'Info'), ('Warning', 'Warning'), ('Critical', 'Critical')]
    
    error_code_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="errors")
    error_code = models.CharField(max_length=20)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()
    probable_cause = models.TextField(null=True, blank=True)
    corrective_action = models.TextField()

class Solution(models.Model):
    solution_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    related_error = models.ForeignKey(Error, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    validated = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)

class TechDoc(models.Model):
    DOC_TYPES = [('Manual', 'Manual'), ('Wiring', 'Wiring'), ('Datasheet', 'Datasheet')]
    
    doc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    language = models.CharField(max_length=2) # EN, FR, DE
    doc_url = models.URLField(max_length=255)
    version = models.CharField(max_length=20)

# --- Projets de Conversion ---

class ConversionProject(models.Model):
    STATUS_CHOICES = [('Draft', 'Draft'), ('Validated', 'Validated'), ('Ordered', 'Ordered')]
    
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)

class ConversionProjectItem(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(ConversionProject, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    role = models.CharField(max_length=20) # Motor, Drive, Cable...