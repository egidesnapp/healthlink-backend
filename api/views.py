# api/views.py

from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # For complex queries
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, date # Import date for filtering


from .models import (
    User, Facility, Role, StockItem, Supplier, SupplierStockItem,
    Order, OrderItem, Patient, Allergy, MedicalHistory, PastProcedure,
    PatientVisit, Vitals, Medication, Prescription,
    AdverseDrugReaction, AdverseEventFollowingImmunization,
    OrderHistory, PaymentTransaction, InventoryHistory
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    FacilitySerializer, RoleSerializer, StockItemSerializer, SupplierSerializer,
    SupplierStockItemSerializer, OrderSerializer, OrderItemSerializer,
    PatientSerializer, AllergySerializer, MedicalHistorySerializer, PastProcedureSerializer,
    PatientVisitSerializer, VitalsSerializer,
    MedicationSerializer, PrescriptionSerializer,
    AdverseDrugReactionSerializer, AdverseEventFollowingImmunizationSerializer,
    OrderHistorySerializer, PaymentTransactionSerializer, InventoryHistorySerializer
)
from .permissions import (
    IsSuperAdmin, IsFacilityAdmin, IsDoctor, IsNurse, IsPharmacist
)


# --- Authentication & User Management ---
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer # Add serializer_class for schema generation

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Delete the user's token to log them out
            request.user.auth_token.delete()
            logout(request)
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Logout failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin]


# --- Facility Views ---
class FacilityListCreateView(generics.ListCreateAPIView):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

class FacilityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


# --- Role Views ---
class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


# --- StockItem Views ---
class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin | IsDoctor | IsNurse]

    def perform_create(self, serializer):
        serializer.save(changed_by_user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(changed_by_user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-barcode/(?P<barcode_value>[^/.]+)')
    def by_barcode(self, request, barcode_value=None):
        """
        Retrieves a stock item by its barcode.
        """
        try:
            stock_item = self.queryset.get(barcode=barcode_value)
            serializer = self.get_serializer(stock_item)
            return Response(serializer.data)
        except StockItem.DoesNotExist:
            return Response({'detail': 'StockItem not found with this barcode.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Supplier Views ---
class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class SupplierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- SupplierStockItem Views ---
class SupplierStockItemListCreateView(generics.ListCreateAPIView):
    queryset = SupplierStockItem.objects.all()
    serializer_class = SupplierStockItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class SupplierStockItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SupplierStockItem.objects.all()
    serializer_class = SupplierStockItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Order Views ---
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

    def perform_create(self, serializer):
        # Automatically set created_by to the requesting user
        serializer.save(created_by=self.request.user)

class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- OrderItem Views ---
class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class OrderItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Patient Views ---
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class PatientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Allergy Views ---
class AllergyListCreateView(generics.ListCreateAPIView):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]

class AllergyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]


# --- MedicalHistory Views ---
class MedicalHistoryListCreateView(generics.ListCreateAPIView):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]

class MedicalHistoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]


# --- PastProcedure Views ---
class PastProcedureListCreateView(generics.ListCreateAPIView):
    queryset = PastProcedure.objects.all()
    serializer_class = PastProcedureSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]

class PastProcedureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PastProcedure.objects.all()
    serializer_class = PastProcedureSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]


# --- PatientVisit Views ---
class PatientVisitListCreateView(generics.ListCreateAPIView):
    queryset = PatientVisit.objects.all()
    serializer_class = PatientVisitSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]

class PatientVisitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientVisit.objects.all()
    serializer_class = PatientVisitSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]


# --- Vitals Views ---
class VitalsListCreateView(generics.ListCreateAPIView):
    queryset = Vitals.objects.all()
    serializer_class = VitalsSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]

class VitalsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vitals.objects.all()
    serializer_class = VitalsSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin]


# --- Medication Views ---
class MedicationListCreateView(generics.ListCreateAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin | IsDoctor | IsNurse]

class MedicationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin | IsDoctor | IsNurse]


# --- Prescription Views ---
class PrescriptionListCreateView(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin | IsDoctor]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(prescriber=self.request.user)
        else:
            serializer.save()

class PrescriptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin | IsDoctor]

class PatientPrescriptionListView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return Prescription.objects.filter(patient__id=patient_id).order_by('-prescribed_date')


# --- Adverse Drug Reaction (ADR) Views ---
class AdverseDrugReactionListCreateView(generics.ListCreateAPIView):
    queryset = AdverseDrugReaction.objects.all()
    serializer_class = AdverseDrugReactionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class AdverseDrugReactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdverseDrugReaction.objects.all()
    serializer_class = AdverseDrugReactionSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Adverse Event Following Immunization (AEFI) Views ---
class AdverseEventFollowingImmunizationListCreateView(generics.ListCreateAPIView):
    queryset = AdverseEventFollowingImmunization.objects.all()
    serializer_class = AdverseEventFollowingImmunizationSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class AdverseEventFollowingImmunizationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdverseEventFollowingImmunization.objects.all()
    serializer_class = AdverseEventFollowingImmunizationSerializer
    permission_classes = [IsAuthenticated, IsDoctor | IsNurse | IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Order History Views ---
class OrderHistoryListCreateView(generics.ListCreateAPIView):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class OrderHistoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Payment Transaction Views ---
class PaymentTransactionListCreateView(generics.ListCreateAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist | IsNurse]

class PaymentTransactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist | IsNurse]


# --- Inventory History Views ---
class InventoryHistoryListCreateView(generics.ListCreateAPIView):
    queryset = InventoryHistory.objects.all()
    serializer_class = InventoryHistorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

class InventoryHistoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryHistory.objects.all()
    serializer_class = InventoryHistorySerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]


# --- Smart Inventory Management ---
class ReorderSuggestionView(generics.ListAPIView):
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

    def get_queryset(self):
        # Filter for items where current_stock is below min_stock_level
        # Also consider items expiring soon (e.g., within 3 months)
        three_months_from_now = date.today() + timedelta(days=90)
        
        # Q objects allow for complex OR queries
        queryset = StockItem.objects.filter(
            Q(current_stock__lt=Q('min_stock_level')) | Q(expiry_date__lte=three_months_from_now, expiry_date__isnull=False)
        ).distinct().order_by('name') # Use distinct to avoid duplicates if an item meets both criteria
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "No reorder suggestions at this time. All stock levels are adequate or not expiring soon."}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DirectSupplierOrderingView(APIView):
    permission_classes = [IsAuthenticated, IsPharmacist | IsSuperAdmin | IsFacilityAdmin]

    def post(self, request, *args, **kwargs):
        """
        Allows authorized users to place a direct order for stock items from a supplier.
        Expects a list of items to order, each with stock_item_id and quantity.
        Example:
        {
            "supplier_id": 1,
            "items": [
                {"stock_item_id": 1, "quantity": 100},
                {"stock_item_id": 2, "quantity": 50}
            ]
        }
        """
        supplier_id = request.data.get('supplier_id')
        items_data = request.data.get('items')

        if not supplier_id or not items_data:
            return Response({"detail": "Supplier ID and items data are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(items_data, list) or not all(isinstance(item, dict) and 'stock_item_id' in item and 'quantity' in item for item in items_data):
            return Response({"detail": "Items data must be a list of objects with 'stock_item_id' and 'quantity'."}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []
        total_amount = 0
        with transaction.atomic():
            order = Order.objects.create(
                supplier=supplier,
                created_by=request.user,
                facility=request.user.facility, # Associate order with user's facility
                status='Ordered'
            )

            for item_data in items_data:
                stock_item_id = item_data['stock_item_id']
                quantity = item_data['quantity']

                try:
                    stock_item = StockItem.objects.get(id=stock_item_id)
                except StockItem.DoesNotExist:
                    transaction.set_rollback(True) # Rollback the order creation
                    return Response({"detail": f"Stock item with ID {stock_item_id} not found."}, status=status.HTTP_404_NOT_FOUND)

                # Get the price from SupplierStockItem, or use StockItem's cost_price as fallback
                supplier_stock_item_price = SupplierStockItem.objects.filter(
                    supplier=supplier, stock_item=stock_item
                ).first()

                unit_price = supplier_stock_item_price.price if supplier_stock_item_price else (stock_item.cost_price if stock_item.cost_price is not None else 0)

                if unit_price == 0:
                    transaction.set_rollback(True)
                    return Response({"detail": f"Unit price not defined for stock item {stock_item.name} from this supplier."}, status=status.HTTP_400_BAD_REQUEST)

                item_total = quantity * unit_price
                total_amount += item_total

                order_item = OrderItem.objects.create(
                    order=order,
                    stock_item=stock_item,
                    quantity=quantity,
                    unit_price=unit_price
                )
                order_items.append(order_item)

            order.total_amount = total_amount
            order.save()

            # Record Order History
            OrderHistory.objects.create(
                order=order,
                change_type='Order Placed',
                description=f"Order placed with {supplier.name} for {len(order_items)} items.",
                changed_by=request.user
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --- Dispensing and Billing ---
class MedicationDispenseView(APIView):
    permission_classes = [IsAuthenticated, IsPharmacist | IsNurse | IsSuperAdmin | IsFacilityAdmin]

    def post(self, request, *args, **kwargs):
        """
        Dispenses medication based on a prescription and handles payment.
        Decreases stock, updates prescription status, and creates a payment transaction.
        Expects:
        {
            "prescription_id": 1,
            "quantity_to_dispense": 25,
            "payment_method": "Cash", # e.g., "Cash", "Card", "Mobile Money", "Insurance"
            "amount_paid": 150.00,    # Total amount patient/insurance pays
            "amount_covered_by_insurance": 100.00, # Optional, if payment_method is 'Insurance'
            "patient_paid_amount": 50.00,         # Optional, if payment_method is 'Insurance'
            "insurance_policy_number": "INS123456" # Optional, if payment_method is 'Insurance'
        }
        """
        prescription_id = request.data.get('prescription_id')
        quantity_to_dispense = request.data.get('quantity_to_dispense')
        payment_method = request.data.get('payment_method')
        amount_paid = request.data.get('amount_paid')
        amount_covered_by_insurance = request.data.get('amount_covered_by_insurance', 0.00)
        patient_paid_amount = request.data.get('patient_paid_amount', 0.00)
        insurance_policy_number = request.data.get('insurance_policy_number')


        if not all([prescription_id, quantity_to_dispense, payment_method, amount_paid is not None]):
            return Response({"detail": "prescription_id, quantity_to_dispense, payment_method, and amount_paid are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            prescription = Prescription.objects.select_related('medication', 'patient').get(id=prescription_id)
        except Prescription.DoesNotExist:
            return Response({"detail": "Prescription not found."}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(quantity_to_dispense, (int, float)) or quantity_to_dispense <= 0:
            return Response({"detail": "quantity_to_dispense must be a positive number."}, status=status.HTTP_400_BAD_REQUEST)

        if prescription.status in ['Dispensed', 'Completed', 'Cancelled']:
            return Response({"detail": f"Prescription is already {prescription.status} and cannot be dispensed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if enough quantity is prescribed remaining
        remaining_to_dispense = prescription.quantity_prescribed - prescription.quantity_dispensed
        if quantity_to_dispense > remaining_to_dispense:
            return Response({"detail": f"Quantity to dispense ({quantity_to_dispense}) exceeds remaining prescribed quantity ({remaining_to_dispense})."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Find the stock item corresponding to the medication
        try:
            stock_item = StockItem.objects.get(name=prescription.medication.name)
        except StockItem.DoesNotExist:
            return Response({"detail": f"Medication '{prescription.medication.name}' is not found in stock."},
                            status=status.HTTP_404_NOT_FOUND)

        if stock_item.current_stock < quantity_to_dispense:
            return Response({"detail": f"Insufficient stock for {stock_item.name}. Current stock: {stock_item.current_stock}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Handle insurance specific fields
        if payment_method == 'Insurance':
            if amount_covered_by_insurance + patient_paid_amount != amount_paid:
                return Response({"detail": "For 'Insurance' payments, 'amount_covered_by_insurance' and 'patient_paid_amount' must sum up to 'amount_paid'."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # If not insurance, these fields should ideally be zero or not provided
            amount_covered_by_insurance = 0.00
            patient_paid_amount = amount_paid # Patient pays the full amount directly
            insurance_policy_number = None

        with transaction.atomic():
            # 1. Update StockItem
            stock_item.current_stock -= quantity_to_dispense
            stock_item.save(changed_by_user=request.user)

            # 2. Update Prescription
            prescription.quantity_dispensed += quantity_to_dispense
            if prescription.quantity_dispensed >= prescription.quantity_prescribed:
                prescription.status = 'Completed'
            else:
                prescription.status = 'Partially Dispensed'
            prescription.dispensed_by = request.user
            prescription.dispensed_date = timezone.now()
            prescription.save()

            # 3. Create PaymentTransaction
            payment = PaymentTransaction.objects.create(
                patient=prescription.patient,
                prescription=prescription,
                amount=amount_paid,
                payment_method=payment_method,
                processed_by=request.user,
                amount_covered_by_insurance=amount_covered_by_insurance, # Save insurance amount
                patient_paid_amount=patient_paid_amount,                 # Save patient paid amount
                insurance_policy_number=insurance_policy_number          # Save policy number
            )

            # 4. Record Inventory History
            InventoryHistory.objects.create(
                stock_item=stock_item,
                transaction_type='Out',
                quantity_change=-quantity_to_dispense, # Negative for 'Out'
                new_stock_level=stock_item.current_stock,
                reason=f"Dispensed for Prescription ID: {prescription.id}",
                processed_by=request.user
            )

        return Response({
            "detail": "Medication dispensed successfully.",
            "prescription_status": prescription.status,
            "new_stock_level": stock_item.current_stock,
            "payment_transaction_id": payment.id
        }, status=status.HTTP_200_OK)


# --- Inventory Reporting ---
class StockLevelReportView(generics.ListAPIView):
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

    def get_queryset(self):
        # By default, return all stock items
        queryset = StockItem.objects.all().order_by('name')

        # Filter by minimum stock level
        min_stock_level_param = self.request.query_params.get('min_stock_level', None)
        if min_stock_level_param:
            try:
                min_stock_level_value = float(min_stock_level_param)
                queryset = queryset.filter(current_stock__lte=min_stock_level_value)
            except ValueError:
                pass # Ignore if not a valid number

        # Filter by maximum stock level
        max_stock_level_param = self.request.query_params.get('max_stock_level', None)
        if max_stock_level_param:
            try:
                max_stock_level_value = float(max_stock_level_param)
                queryset = queryset.filter(current_stock__gte=max_stock_level_value)
            except ValueError:
                pass # Ignore if not a valid number
        
        # Filter by specific medication name (partial match)
        medication_name = self.request.query_params.get('medication_name', None)
        if medication_name:
            queryset = queryset.filter(name__icontains=medication_name)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "No stock items match the criteria."}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MedicationUsageReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist | IsDoctor]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response({"detail": "Both 'start_date' and 'end_date' query parameters are required (YYYY-MM-DD)."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Please use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Filter inventory history for 'Out' transactions within the date range
        # and group by stock item to sum up dispensed quantities
        usage_data = InventoryHistory.objects.filter(
            transaction_type='Out',
            transaction_date__date__range=[start_date, end_date]
        ).values('stock_item__name', 'stock_item__unit_of_measure').annotate(
            total_dispensed_quantity=models.Sum(models.F('quantity_change') * -1) # Convert negative to positive
        ).order_by('stock_item__name')

        if not usage_data.exists():
            return Response({"detail": "No medication usage data found for the specified period."},
                            status=status.HTTP_200_OK)

        report = []
        for item in usage_data:
            report.append({
                "medication_name": item['stock_item__name'],
                "total_dispensed_quantity": item['total_dispensed_quantity'],
                "unit_of_measure": item['stock_item__unit_of_measure']
            })

        return Response(report, status=status.HTTP_200_OK)


class ExpiringMedicationsReportView(generics.ListAPIView):
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist]

    def get_queryset(self):
        # Default to showing medications expiring within the next 6 months
        months = self.request.query_params.get('months', 6)
        try:
            months = int(months)
            if months < 0:
                months = 0 # Ensure non-negative
        except ValueError:
            months = 6 # Fallback to default

        expiry_threshold_date = date.today() + timedelta(days=months * 30) # Approximate months

        queryset = StockItem.objects.filter(
            expiry_date__lte=expiry_threshold_date,
            expiry_date__isnull=False # Ensure expiry_date is not null
        ).order_by('expiry_date')

        # Optional: filter by minimum current stock (e.g., only show if > 0)
        min_stock = self.request.query_params.get('min_stock', None)
        if min_stock is not None:
            try:
                min_stock_value = float(min_stock)
                queryset = queryset.filter(current_stock__gt=min_stock_value)
            except ValueError:
                pass # Ignore invalid min_stock parameter

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "No expiring medications found for the specified criteria."}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InsuranceDispensingReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin | IsFacilityAdmin | IsPharmacist | IsNurse]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        patient_id = request.query_params.get('patient_id')
        insurance_policy_number = request.query_params.get('policy_number')

        if not start_date_str or not end_date_str:
            return Response({"detail": "Both 'start_date' and 'end_date' query parameters are required (YYYY-MM-DD)."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Please use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Filter payment transactions where payment_method is 'Insurance'
        # and within the specified date range.
        queryset = PaymentTransaction.objects.filter(
            payment_method='Insurance',
            transaction_date__date__range=[start_date, end_date]
        ).select_related('patient', 'prescription__medication').order_by('-transaction_date')

        if patient_id:
            try:
                queryset = queryset.filter(patient__id=patient_id)
            except ValueError:
                return Response({"detail": "Invalid patient_id. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if insurance_policy_number:
            queryset = queryset.filter(insurance_policy_number__icontains=insurance_policy_number)

        if not queryset.exists():
            return Response({"detail": "No insurance dispensing records found for the specified criteria."},
                            status=status.HTTP_200_OK)

        report_data = []
        for transaction in queryset:
            report_data.append({
                "transaction_id": transaction.id,
                "transaction_date": transaction.transaction_date.isoformat(),
                "patient_name": transaction.patient.get_full_name(),
                "patient_id": transaction.patient.id,
                "medication_name": transaction.prescription.medication.name if transaction.prescription and transaction.prescription.medication else "N/A",
                "quantity_dispensed": transaction.prescription.quantity_dispensed if transaction.prescription else "N/A",
                "total_amount_billed": transaction.amount,
                "amount_covered_by_insurance": transaction.amount_covered_by_insurance,
                "patient_paid_amount": transaction.patient_paid_amount,
                "insurance_policy_number": transaction.insurance_policy_number,
                "processed_by": transaction.processed_by.username if transaction.processed_by else "N/A"
            })

        return Response(report_data, status=status.HTTP_200_OK)