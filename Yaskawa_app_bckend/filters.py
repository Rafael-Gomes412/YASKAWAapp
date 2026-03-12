import django_filters
from django.db.models import Q
from .models import Product

# ── Méthode de recherche partagée ────────────────────────────────────────────
def filter_search(queryset, name, value):
    return queryset.filter(
        Q(model_code__icontains=value)  |
        Q(numero_SAP__icontains=value)  |
        Q(product_type__icontains=value)
    )

# ── FILTRE GÉNÉRIQUE ──────────────────────────────────────────────────────────
class ProductFilter(django_filters.FilterSet):
    search  = django_filters.CharFilter(method='filter_search', label='Recherche')
    
    
    voltage = django_filters.ChoiceFilter(
        field_name='spec__voltage',
        label='Voltage',
        empty_label="All"
    )
    series  = django_filters.ChoiceFilter(
        field_name='spec__series',
        label='Série',
        empty_label="All"
    )
    power_min = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='gte')
    power_max = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='lte')

    def filter_search(self, queryset, name, value):
        return filter_search(queryset, name, value)

    class Meta:
        model  = Product
        fields = ['search', 'voltage', 'series']

# ── FILTRE SERVOPACK (SGD) ────────────────────────────────────────────────────
class ServopackFilter(django_filters.FilterSet):
    search  = django_filters.CharFilter(method='filter_search', label='Recherche')

    voltage = django_filters.ChoiceFilter(
        field_name='spec__voltage',
        label='Voltage',
        empty_label="All"
    )
    protocol = django_filters.ChoiceFilter(
        field_name='spec__protocol',
        label='Protocol',
        empty_label="All"
    )
    series = django_filters.ChoiceFilter(
        field_name='spec__series',
        label='Série',
        empty_label="All"
    )
    power_min = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='gte')
    power_max = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='lte')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On injecte les choix dynamiquement pour que ChoiceFilter fonctionne
        self.filters['voltage'].extra['choices'] = self.get_choices('voltage')
        self.filters['protocol'].extra['choices'] = self.get_choices('protocol')
        self.filters['series'].extra['choices'] = self.get_choices('series')

    def get_choices(self, field):
        values = Product.objects.filter(model_code__startswith='SGD').values_list(f'spec__{field}', flat=True).distinct()
        return [(v, v) for v in values if v and v != 'Other']

    def filter_search(self, queryset, name, value):
        return filter_search(queryset, name, value)
   
    in_stock = django_filters.BooleanFilter(field_name='in_stock')

    class Meta:
        model  = Product
        fields = ['search', 'voltage', 'protocol', 'series']

# ── FILTRE MOTOR (SGM) ────────────────────────────────────────────────────────
class MotorFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Recherche')

    voltage = django_filters.ChoiceFilter(
        field_name='spec__voltage',
        label='Voltage',
        empty_label="All"
    )
    sgm_series = django_filters.ChoiceFilter(
        field_name='spec__series',
        label='Série moteur',
        empty_label="All"
    )
    encoder_type = django_filters.ChoiceFilter(
        field_name='spec__encoder_type',
        label="Type d'encodeur",
        empty_label="All"
    )
    brake = django_filters.BooleanFilter(
        field_name='spec__brake',
        label='Frein',
    )
    power_min = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='gte')
    power_max = django_filters.NumberFilter(field_name='spec__power_kw', lookup_expr='lte')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['voltage'].extra['choices'] = self.get_choices('voltage')
        self.filters['sgm_series'].extra['choices'] = self.get_choices('series')
        self.filters['encoder_type'].extra['choices'] = self.get_choices('encoder_type')

    def get_choices(self, field):
        values = Product.objects.filter(model_code__startswith='SGM').values_list(f'spec__{field}', flat=True).distinct()
        return [(v, v) for v in values if v and v != 'Other']

    def filter_search(self, queryset, name, value):
        return filter_search(queryset, name, value)

    in_stock = django_filters.BooleanFilter(field_name='in_stock')

    class Meta:
        model  = Product
        fields = ['search', 'voltage', 'sgm_series', 'encoder_type', 'brake']