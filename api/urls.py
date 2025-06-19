# healthlink-backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework import status # Import status for use in APIRoot if needed

from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserListView, UserDetailView,
    FacilityListCreateView, FacilityRetrieveUpdateDestroyView,
    RoleListCreateView, RoleRetrieveUpdateDestroyView,
    StockItemViewSet, # This is a ViewSet
    SupplierListCreateView, SupplierRetrieveUpdateDestroyView,
    SupplierStockItemListCreateView, SupplierStockItemRetrieveUpdateDestroyView,
    OrderListCreateView, OrderRetrieveUpdateDestroyView,
    OrderItemListCreateView, OrderItemRetrieveUpdateDestroyView,
    PatientListCreateView, PatientRetrieveUpdateDestroyView,
    AllergyListCreateView, AllergyRetrieveUpdateDestroyView,
    MedicalHistoryListCreateView, MedicalHistoryRetrieveUpdateDestroyView,
    PastProcedureListCreateView, PastProcedureRetrieveUpdateDestroyView,
    PatientVisitListCreateView, PatientVisitRetrieveUpdateDestroyView,
    VitalsListCreateView, VitalsRetrieveUpdateDestroyView,
    MedicationListCreateView, MedicationRetrieveUpdateDestroyView,
    PrescriptionListCreateView, PrescriptionRetrieveUpdateDestroyView,
    PatientPrescriptionListView,
    AdverseDrugReactionListCreateView, AdverseDrugReactionRetrieveUpdateDestroyView,
    AdverseEventFollowingImmunizationListCreateView, AdverseEventFollowingImmunizationRetrieveUpdateDestroyView,
    OrderHistoryListCreateView, OrderHistoryRetrieveUpdateDestroyView,
    PaymentTransactionListCreateView, PaymentTransactionRetrieveUpdateDestroyView,
    InventoryHistoryListCreateView, InventoryHistoryRetrieveUpdateDestroyView,
    ReorderSuggestionView, DirectSupplierOrderingView,
    MedicationDispenseView,
    StockLevelReportView, MedicationUsageReportView, ExpiringMedicationsReportView,
    InsuranceDispensingReportView
)

# Create a router and register ViewSets with it.
router = DefaultRouter()
# Register StockItemViewSet. The 'basename' is used to generate URL names like 'stockitem-list', 'stockitem-detail'.
router.register(r'stockitems', StockItemViewSet, basename='stockitem')

# A custom root API view to list all endpoints
class APIRoot(APIView):
    """
    Root of the HealthLink API. Lists all available API endpoints.
    """
    def get(self, request, format=None):
        return Response({
            'users': reverse('user-list-create', request=request, format=format),
            'register': reverse('register', request=request, format=format),
            'login': reverse('login', request=request, format=format),
            'logout': reverse('logout', request=request, format=format),
            'facilities': reverse('facility-list-create', request=request, format=format),
            'roles': reverse('role-list-create', request=request, format=format),
            'stockitems': reverse('stockitem-list', request=request, format=format), # <--- ADDED/UPDATED THIS LINE
            'suppliers': reverse('supplier-list-create', request=request, format=format),
            'supplier-stock-items': reverse('supplierstockitem-list-create', request=request, format=format),
            'orders': reverse('order-list-create', request=request, format=format),
            'order-items': reverse('orderitem-list-create', request=request, format=format),
            'patients': reverse('patient-list-create', request=request, format=format),
            'allergies': reverse('allergy-list-create', request=request, format=format),
            'medical-history': reverse('medicalhistory-list-create', request=request, format=format),
            'past-procedures': reverse('pastprocedure-list-create', request=request, format=format),
            'patient-visits': reverse('patientvisit-list-create', request=request, format=format),
            'vitals': reverse('vitals-list-create', request=request, format=format),
            'medications': reverse('medication-list-create', request=request, format=format),
            'prescriptions': reverse('prescription-list-create', request=request, format=format),
            'adrs': reverse('adversedrugreaction-list-create', request=request, format=format),
            'aefis': reverse('adverseeventfollowingimmunization-list-create', request=request, format=format),
            'order-history': reverse('orderhistory-list-create', request=request, format=format),
            'payments': reverse('paymenttransaction-list-create', request=request, format=format),
            'inventory-history': reverse('inventoryhistory-list-create', request=request, format=format),
            'reorder-suggestions': reverse('reorder-suggestions', request=request, format=format),
            'incoming-orders': reverse('direct-supplier-ordering', request=request, format=format),
            'medication-dispense': reverse('medication-dispense', request=request, format=format),
            'reports-stock-level': reverse('stock-level-report', request=request, format=format),
            'reports-medication-usage': reverse('medication-usage-report', request=request, format=format),
            'reports-expiring-medications': reverse('expiring-medications-report', request=request, format=format),
            'reports-insurance-dispensing': reverse('insurance-dispensing-report', request=request, format=format),
        })


urlpatterns = [
    path('', APIRoot.as_view(), name='api-root'), # Set the custom root view
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # These are handled by generic API views, not ViewSets, so they keep their explicit paths.
    path('users/', UserListView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    path('facilities/', FacilityListCreateView.as_view(), name='facility-list-create'),
    path('facilities/<int:pk>/', FacilityRetrieveUpdateDestroyView.as_view(), name='facility-detail'),

    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-detail'),

    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierRetrieveUpdateDestroyView.as_view(), name='supplier-detail'),

    path('supplier-stock-items/', SupplierStockItemListCreateView.as_view(), name='supplierstockitem-list-create'),
    path('supplier-stock-items/<int:pk>/', SupplierStockItemRetrieveUpdateDestroyView.as_view(), name='supplierstockitem-detail'),

    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyView.as_view(), name='order-detail'),

    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemRetrieveUpdateDestroyView.as_view(), name='orderitem-detail'),

    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientRetrieveUpdateDestroyView.as_view(), name='patient-detail'),

    path('allergies/', AllergyListCreateView.as_view(), name='allergy-list-create'),
    path('allergies/<int:pk>/', AllergyRetrieveUpdateDestroyView.as_view(), name='allergy-detail'),

    path('medical-history/', MedicalHistoryListCreateView.as_view(), name='medicalhistory-list-create'),
    path('medical-history/<int:pk>/', MedicalHistoryRetrieveUpdateDestroyView.as_view(), name='medicalhistory-detail'),

    path('past-procedures/', PastProcedureListCreateView.as_view(), name='pastprocedure-list-create'),
    path('past-procedures/<int:pk>/', PastProcedureRetrieveUpdateDestroyView.as_view(), name='pastprocedure-detail'),

    path('patient-visits/', PatientVisitListCreateView.as_view(), name='patientvisit-list-create'),
    path('patient-visits/<int:pk>/', PatientVisitRetrieveUpdateDestroyView.as_view(), name='patientvisit-detail'),

    path('vitals/', VitalsListCreateView.as_view(), name='vitals-list-create'),
    path('vitals/<int:pk>/', VitalsRetrieveUpdateDestroyView.as_view(), name='vitals-detail'),

    path('medications/', MedicationListCreateView.as_view(), name='medication-list-create'),
    path('medications/<int:pk>/', MedicationRetrieveUpdateDestroyView.as_view(), name='medication-detail'),

    path('prescriptions/', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('prescriptions/<int:pk>/', PrescriptionRetrieveUpdateDestroyView.as_view(), name='prescription-detail'),
    path('patients/<int:patient_pk>/prescriptions/', PatientPrescriptionListView.as_view(), name='patient-prescriptions-list'),

    path('adrs/', AdverseDrugReactionListCreateView.as_view(), name='adversedrugreaction-list-create'),
    path('adrs/<int:pk>/', AdverseDrugReactionRetrieveUpdateDestroyView.as_view(), name='adversedrugreaction-detail'),

    path('aefis/', AdverseEventFollowingImmunizationListCreateView.as_view(), name='adverseeventfollowingimmunization-list-create'),
    path('aefis/<int:pk>/', AdverseEventFollowingImmunizationRetrieveUpdateDestroyView.as_view(), name='adverseeventfollowingimmunization-detail'),

    path('order-history/', OrderHistoryListCreateView.as_view(), name='orderhistory-list-create'),
    path('order-history/<int:pk>/', OrderHistoryRetrieveUpdateDestroyView.as_view(), name='orderhistory-detail'),

    path('payments/', PaymentTransactionListCreateView.as_view(), name='paymenttransaction-list-create'),
    path('payments/<int:pk>/', PaymentTransactionRetrieveUpdateDestroyView.as_view(), name='paymenttransaction-detail'),

    path('inventory-history/', InventoryHistoryListCreateView.as_view(), name='inventoryhistory-list-create'),
    path('inventory-history/<int:pk>/', InventoryHistoryRetrieveUpdateDestroyView.as_view(), name='inventoryhistory-detail'),

    # Smart Inventory Management URLs (These are APIViews, not ViewSets)
    path('inventory/reorder-suggestions/', ReorderSuggestionView.as_view(), name='reorder-suggestions'),
    path('incoming-orders/', DirectSupplierOrderingView.as_view(), name='direct-supplier-ordering'),

    # Dispensing and Billing URLs (These are APIViews, not ViewSets)
    path('dispense-medication/', MedicationDispenseView.as_view(), name='medication-dispense'),

    # Inventory Reporting URLs (These are APIViews, not ViewSets)
    path('reports/stock-level/', StockLevelReportView.as_view(), name='stock-level-report'),
    path('reports/medication-usage/', MedicationUsageReportView.as_view(), name='medication-usage-report'),
    path('reports/expiring-medications/', ExpiringMedicationsReportView.as_view(), name='expiring-medications-report'),
    path('reports/insurance-dispensing/', InsuranceDispensingReportView.as_view(), name='insurance-dispensing-report'),

    # Include router URLs at the end. This will add /stockitems/ and /stockitems/<pk>/
    path('', include(router.urls)), # <--- ADDED THIS LINE
]