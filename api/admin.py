
from django.contrib import admin
from .models import (
    User, Facility, Role, StockItem, Supplier, SupplierStockItem,
    Order, OrderItem, Patient, Allergy, MedicalHistory, PastProcedure,
    PatientVisit, Vitals, Medication, Prescription,
    AdverseDrugReaction, AdverseEventFollowingImmunization,
    OrderHistory, PaymentTransaction, InventoryHistory
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'facility', 'role', 'is_staff']
    list_filter = ['facility', 'role', 'is_staff']
    search_fields = ['username', 'email']

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'created_at']
    search_fields = ['name', 'city']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_stock', 'unit', 'reorder_level', 'expiry_date']
    list_filter = ['unit', 'is_active', 'supplier']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone_number', 'email']
    search_fields = ['name', 'contact_person']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date_of_birth', 'gender']
    search_fields = ['first_name', 'last_name', 'national_id']
    list_filter = ['gender']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_date', 'status', 'total_amount', 'patient']
    list_filter = ['status', 'order_date']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient_visit', 'medication', 'dosage', 'is_dispensed']
    list_filter = ['is_dispensed', 'prescription_date']

# Register other models with basic admin
admin.site.register(SupplierStockItem)
admin.site.register(OrderItem)
admin.site.register(Allergy)
admin.site.register(MedicalHistory)
admin.site.register(PastProcedure)
admin.site.register(PatientVisit)
admin.site.register(Vitals)
admin.site.register(Medication)
admin.site.register(AdverseDrugReaction)
admin.site.register(AdverseEventFollowingImmunization)
admin.site.register(OrderHistory)
admin.site.register(PaymentTransaction)
admin.site.register(InventoryHistory)
