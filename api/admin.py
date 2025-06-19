# api/admin.py

from django.contrib import admin
from .models import (
    User, Facility, Role, StockItem,
    Supplier, SupplierStockItem, Order, OrderItem,
    Patient, PatientVisit, Vitals, # Existing models
    Allergy, MedicalHistory, PastProcedure # NEW models added
)

# Register your models here so they appear in the Django admin panel.

admin.site.register(User)
admin.site.register(Facility)
admin.site.register(Role)
admin.site.register(StockItem)
admin.site.register(Supplier)
admin.site.register(SupplierStockItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Patient)
admin.site.register(PatientVisit) # Register PatientVisit
admin.site.register(Vitals)       # Register Vitals

# Register the new models for medical history management
admin.site.register(Allergy)
admin.site.register(MedicalHistory)
admin.site.register(PastProcedure)

# Optional: You can customize how models appear in the admin
# by defining Admin classes (e.g., list_display, search_fields)
# For example:
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'facility', 'supplier', 'order_date', 'status', 'total_amount')
#     list_filter = ('status', 'order_date', 'facility', 'supplier')
#     search_fields = ('facility__name', 'supplier__name')
#     date_hierarchy = 'order_date'