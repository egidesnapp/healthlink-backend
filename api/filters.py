import django_filters
from .models import StockItem, Patient, Order, Prescription

class StockItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    current_stock_gte = django_filters.NumberFilter(field_name='current_stock', lookup_expr='gte')
    current_stock_lte = django_filters.NumberFilter(field_name='current_stock', lookup_expr='lte')
    expiry_date_gte = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expiry_date_lte = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')

    class Meta:
        model = StockItem
        fields = ['name', 'unit', 'supplier', 'is_active']

class PatientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            first_name__icontains=value
        ) | queryset.filter(
            last_name__icontains=value
        )

    class Meta:
        model = Patient
        fields = ['gender', 'name']

class OrderFilter(django_filters.FilterSet):
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'patient']

class PrescriptionFilter(django_filters.FilterSet):
    prescription_date_gte = django_filters.DateFilter(field_name='prescription_date', lookup_expr='gte')
    prescription_date_lte = django_filters.DateFilter(field_name='prescription_date', lookup_expr='lte')

    class Meta:
        model = Prescription
        fields = ['is_dispensed', 'medication', 'patient_visit__patient']