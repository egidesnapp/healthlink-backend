# api/serializers.py

from rest_framework import serializers
from .models import (
    User, Facility, Role, StockItem, Supplier, SupplierStockItem,
    Order, OrderItem, Patient, Allergy, MedicalHistory, PastProcedure,
    PatientVisit, Vitals, Medication, Prescription,
    AdverseDrugReaction, AdverseEventFollowingImmunization,
    OrderHistory, PaymentTransaction, InventoryHistory
)

# --- User Serializers ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'address', 'facility', 'role', 'first_name', 'last_name']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone_number', 'address', 'facility', 'role', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()
            if not user:
                raise serializers.ValidationError("User with this username does not exist.")
            if not user.check_password(password):
                raise serializers.ValidationError("Incorrect password.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        data['user'] = user
        return data


# --- Facility Serializers ---
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Role Serializers ---
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- StockItem Serializers ---
class StockItemSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    class Meta:
        model = StockItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'changed_by']


# --- Supplier Serializers ---
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- SupplierStockItem Serializers ---
class SupplierStockItemSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stock_item_name = serializers.CharField(source='stock_item.name', read_only=True)
    class Meta:
        model = SupplierStockItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Order Serializers ---
class OrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


# --- OrderItem Serializers ---
class OrderItemSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source='stock_item.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Patient Serializers ---
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Allergy Serializers ---
class AllergySerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Allergy
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- MedicalHistory Serializers ---
class MedicalHistorySerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- PastProcedure Serializers ---
class PastProcedureSerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PastProcedure
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- PatientVisit Serializers ---
class PatientVisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    attending_physician_username = serializers.CharField(source='attending_physician.username', read_only=True)
    class Meta:
        model = PatientVisit
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Vitals Serializers ---
class VitalsSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    class Meta:
        model = Vitals
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- MEDICATION SERIALIZER ---
class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'


# --- PRESCRIPTION SERIALIZER ---
class PrescriptionSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    patient_full_name = serializers.SerializerMethodField(read_only=True)
    prescriber_username = serializers.CharField(source='prescriber.username', read_only=True)
    dispensed_by_username = serializers.CharField(source='dispensed_by.username', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'dispensed_by', 'dispensed_date']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- Adverse Drug Reaction (ADR) Serializer ---
class AdverseDrugReactionSerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)

    class Meta:
        model = AdverseDrugReaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- Adverse Event Following Immunization (AEFI) Serializer ---
class AdverseEventFollowingImmunizationSerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)

    class Meta:
        model = AdverseEventFollowingImmunization
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- Order History Serializer ---
class OrderHistorySerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.id', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = OrderHistory
        fields = '__all__'
        read_only_fields = ['id', 'change_date']


# --- Payment Transaction Serializer ---
class PaymentTransactionSerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField(read_only=True)
    prescription_id = serializers.CharField(source='prescription.id', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = '__all__' # Include all fields from the model
        read_only_fields = ['id', 'transaction_date', 'created_at', 'updated_at']

    def get_patient_full_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None


# --- Inventory History Serializer ---
class InventoryHistorySerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(source='stock_item.name', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True)

    class Meta:
        model = InventoryHistory
        fields = '__all__'
        read_only_fields = ['id', 'transaction_date', 'created_at', 'updated_at']