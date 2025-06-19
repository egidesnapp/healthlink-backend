# healthlink-backend/api/filters.py

import django_filters
from .models import (
    User, Facility, Role, StockItem, Supplier, SupplierStockItem, Order,
    OrderItem, Patient, PatientVisit, Vitals,
    Allergy, MedicalHistory, PastProcedure
)

# --- User Filter ---
class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    role_name = django_filters.CharFilter(field_name='role__name', lookup_expr='icontains')
    facility_name = django_filters.CharFilter(field_name='facility__name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'facility', 'role_name', 'facility_name']


# --- Facility Filter ---
class FacilityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')

    class Meta:
        model = Facility
        fields = ['name', 'city', 'country']


# --- Role Filter ---
class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Role
        fields = ['name']


# --- StockItem Filter ---
class StockItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category', lookup_expr='icontains')
    min_stock = django_filters.NumberFilter(field_name='current_stock', lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name='current_stock', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='price_per_unit', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_unit', lookup_expr='lte')

    class Meta:
        model = StockItem
        fields = [
            'name', 'category', 'unit_of_measure',
            'min_stock', 'max_stock', 'min_price', 'max_price'
        ]


# --- Supplier Filter ---
class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    contact_person = django_filters.CharFilter(field_name='contact_person', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone_number']


# --- SupplierStockItem Filter ---
class SupplierStockItemFilter(django_filters.FilterSet):
    supplier_name = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')
    stock_item_name = django_filters.CharFilter(field_name='stock_item__name', lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = SupplierStockItem
        fields = ['supplier', 'stock_item', 'supplier_name', 'stock_item_name', 'min_price', 'max_price']


# --- Order Filter ---
class OrderFilter(django_filters.FilterSet):
    min_date = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    facility_name = django_filters.CharFilter(field_name='facility__name', lookup_expr='icontains')
    supplier_name = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['status', 'facility', 'supplier', 'min_date', 'max_date', 'facility_name', 'supplier_name']


# --- OrderItem Filter ---
class OrderItemFilter(django_filters.FilterSet):
    stock_item_name = django_filters.CharFilter(field_name='stock_item__name', lookup_expr='icontains')
    order_id = django_filters.NumberFilter(field_name='order__id', lookup_expr='exact')

    class Meta:
        model = OrderItem
        fields = ['order', 'stock_item', 'stock_item_name', 'order_id']


# --- Patient Filter ---
class PatientFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    national_id = django_filters.CharFilter(field_name='national_id', lookup_expr='icontains')
    contact_number = django_filters.CharFilter(field_name='contact_number', lookup_expr='icontains')
    facility_name = django_filters.CharFilter(field_name='facility__name', lookup_expr='icontains')

    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'national_id', 'contact_number',
            'date_of_birth', 'gender', 'facility', 'facility_name'
        ]

# --- PatientVisit Filter ---
class PatientVisitFilter(django_filters.FilterSet):
    patient_name = django_filters.CharFilter(method='filter_by_patient_name', label="Patient Name (contains)")
    min_date = django_filters.DateFilter(field_name='visit_date', lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name='visit_date', lookup_expr='lte')
    reason_for_visit = django_filters.CharFilter(field_name='reason_for_visit', lookup_expr='icontains')
    diagnosis = django_filters.CharFilter(field_name='diagnosis', lookup_expr='icontains')
    visit_type = django_filters.CharFilter(field_name='visit_type', lookup_expr='icontains')
    facility_name = django_filters.CharFilter(field_name='facility__name', lookup_expr='icontains')

    class Meta:
        model = PatientVisit
        fields = [
            'patient', 'visit_date', 'reason_for_visit', 'diagnosis', 'visit_type',
            'facility', 'patient_name', 'min_date', 'max_date', 'facility_name'
        ]

    def filter_by_patient_name(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(patient__first_name__icontains=value) |
            django_filters.Q(patient__last_name__icontains=value)
        )


# --- Vitals Filter ---
class VitalsFilter(django_filters.FilterSet):
    patient_name = django_filters.CharFilter(method='filter_by_patient_name', label="Patient Name (contains)")
    min_recorded_at = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='gte')
    max_recorded_at = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='lte')
    min_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='gte')
    max_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='lte')
    min_blood_pressure_systolic = django_filters.NumberFilter(field_name='blood_pressure_systolic', lookup_expr='gte')
    max_blood_pressure_systolic = django_filters.NumberFilter(field_name='blood_pressure_systolic', lookup_expr='lte')
    min_blood_pressure_diastolic = django_filters.NumberFilter(field_name='blood_pressure_diastolic', lookup_expr='gte')
    max_blood_pressure_diastolic = django_filters.NumberFilter(field_name='blood_pressure_diastolic', lookup_expr='lte')
    min_pulse_rate = django_filters.NumberFilter(field_name='pulse_rate', lookup_expr='gte')
    max_pulse_rate = django_filters.NumberFilter(field_name='pulse_rate', lookup_expr='lte')
    min_respiratory_rate = django_filters.NumberFilter(field_name='respiratory_rate', lookup_expr='gte')
    max_respiratory_rate = django_filters.NumberFilter(field_name='respiratory_rate', lookup_expr='lte')
    min_bmi = django_filters.NumberFilter(field_name='bmi', lookup_expr='gte')
    max_bmi = django_filters.NumberFilter(field_name='bmi', lookup_expr='lte')

    class Meta:
        model = Vitals
        fields = [
            'patient', 'patient_visit', 'recorded_by', 'oxygen_saturation', 'weight', 'height',
            'patient_name', 'min_recorded_at', 'max_recorded_at',
            'min_temperature', 'max_temperature',
            'min_blood_pressure_systolic', 'max_blood_pressure_systolic',
            'min_blood_pressure_diastolic', 'max_blood_pressure_diastolic',
            'min_pulse_rate', 'max_pulse_rate', 'min_respiratory_rate', 'max_respiratory_rate',
            'min_bmi', 'max_bmi'
        ]

    def filter_by_patient_name(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(patient__first_name__icontains=value) |
            django_filters.Q(patient__last_name__icontains=value)
        )

# --- NEW FILTERS FOR ALLERGIES, MEDICAL HISTORY, PAST PROCEDURES ---

class AllergyFilter(django_filters.FilterSet):
    patient_name = django_filters.CharFilter(method='filter_by_patient_name', label="Patient Name (contains)")
    allergen = django_filters.CharFilter(field_name='allergen', lookup_expr='icontains')
    reaction = django_filters.CharFilter(field_name='reaction', lookup_expr='icontains')

    class Meta:
        model = Allergy
        fields = ['patient', 'allergen', 'reaction', 'severity', 'patient_name']

    def filter_by_patient_name(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(patient__first_name__icontains=value) |
            django_filters.Q(patient__last_name__icontains=value)
        )


class MedicalHistoryFilter(django_filters.FilterSet):
    patient_name = django_filters.CharFilter(method='filter_by_patient_name', label="Patient Name (contains)")
    condition = django_filters.CharFilter(field_name='condition', lookup_expr='icontains')
    diagnosis_date_min = django_filters.DateFilter(field_name='diagnosis_date', lookup_expr='gte')
    diagnosis_date_max = django_filters.DateFilter(field_name='diagnosis_date', lookup_expr='lte')

    class Meta:
        model = MedicalHistory
        fields = ['patient', 'condition', 'diagnosis_date', 'is_active', 'patient_name', 'diagnosis_date_min', 'diagnosis_date_max']

    def filter_by_patient_name(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(patient__first_name__icontains=value) |
            django_filters.Q(patient__last_name__icontains=value)
        )


class PastProcedureFilter(django_filters.FilterSet):
    patient_name = django_filters.CharFilter(method='filter_by_patient_name', label="Patient Name (contains)")
    procedure_name = django_filters.CharFilter(field_name='procedure_name', lookup_expr='icontains')
    performing_physician = django_filters.CharFilter(field_name='performing_physician', lookup_expr='icontains')
    procedure_date_min = django_filters.DateFilter(field_name='procedure_date', lookup_expr='gte')
    procedure_date_max = django_filters.DateFilter(field_name='procedure_date', lookup_expr='lte')

    class Meta:
        model = PastProcedure
        fields = ['patient', 'procedure_name', 'procedure_date', 'performing_physician', 'patient_name', 'procedure_date_min', 'procedure_date_max']

    def filter_by_patient_name(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(patient__first_name__icontains=value) |
            django_filters.Q(patient__last_name__icontains=value)
        )