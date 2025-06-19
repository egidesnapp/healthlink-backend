# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db.models import DecimalField
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


# --- Custom User Model Definition ---
class User(AbstractUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    facility = models.ForeignKey('api.Facility', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    role = models.ForeignKey('api.Role', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


# --- Facility Model Definition ---
class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Facilities'

    def __str__(self):
        return self.name


# --- Role Model Definition ---
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# --- Stock Item Model ---
class StockItem(models.Model):
    UNIT_CHOICES = [
        ('Pill', 'Pill'),
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup'),
        ('Injection', 'Injection'),
        ('Vial', 'Vial'),
        ('Ampule', 'Ampule'),
        ('Bottle', 'Bottle'),
        ('Tube', 'Tube'),
        ('Pouch', 'Pouch'),
        ('Unit', 'Unit'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, default='Unit')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    expiry_date = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey('api.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items')
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))], help_text="Minimum stock level before reordering is triggered.")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Physical location of the stock item in the facility.")
    is_active = models.BooleanField(default=True, help_text="Is the stock item currently in use or available?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items_created')
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items_updated')

    class Meta:
        unique_together = ('name', 'supplier') # Ensures that a stock item from a specific supplier is unique
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit}s)"


# --- Supplier Model ---
class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# --- Supplier Stock Item (Junction Table for M2M with extra fields) ---
class SupplierStockItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    supplied_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    last_supplied_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('supplier', 'stock_item')
        verbose_name = 'Supplier Stock Item'
        verbose_name_plural = 'Supplier Stock Items'

    def __str__(self):
        return f"{self.supplier.name} - {self.stock_item.name}"


# --- Order Model ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    patient = models.ForeignKey('api.Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_created')
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order {self.id} - {self.status}"


# --- Order Item Model ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    stock_item = models.ForeignKey(StockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'stock_item')

    def __str__(self):
        return f"{self.quantity} x {self.stock_item.name if self.stock_item else 'N/A'}"


# --- Patient Model ---
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    national_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


# --- Allergy Model ---
class Allergy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=255, help_text="Substance causing the allergy (e.g., Penicillin, Peanuts)")
    reaction = models.TextField(blank=True, null=True, help_text="Description of the allergic reaction (e.g., Rash, Anaphylaxis)")
    severity = models.CharField(max_length=50, blank=True, null=True, help_text="Severity of the allergy (e.g., Mild, Moderate, Severe)")
    diagnosed_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Allergies'
        unique_together = ('patient', 'allergen')

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.allergen}"


# --- Medical History Model ---
class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255, help_text="Name of the medical condition (e.g., Diabetes, Hypertension)")
    diagnosis_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the condition or treatment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Medical History'

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.condition}"


# --- Past Procedure Model ---
class PastProcedure(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='past_procedures')
    procedure_name = models.CharField(max_length=255)
    procedure_date = models.DateField()
    notes = models.TextField(blank=True, null=True, help_text="Notes about the procedure and outcome")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Past Procedure'
        verbose_name_plural = 'Past Procedures'
        ordering = ['-procedure_date']

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.procedure_name}"


# --- Patient Visit Model ---
class PatientVisit(models.Model):
    VISIT_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
        ('Check-up', 'Check-up'),
        ('Other', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateTimeField(default=timezone.now)
    visit_type = models.CharField(max_length=50, choices=VISIT_TYPE_CHOICES, default='Consultation')
    reason = models.TextField(help_text="Reason for the patient's visit.")
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    attending_physician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_visits')
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_visits')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Visit'
        verbose_name_plural = 'Patient Visits'
        ordering = ['-visit_date']

    def __str__(self):
        return f"Visit for {self.patient.get_full_name()} on {self.visit_date.strftime('%Y-%m-%d')}"


# --- Vitals Model ---
class Vitals(models.Model):
    patient_visit = models.OneToOneField(PatientVisit, on_delete=models.CASCADE, related_name='vitals')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Temperature in Celsius")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, help_text="Systolic Blood Pressure (mmHg)")
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, help_text="Diastolic Blood Pressure (mmHg)")
    heart_rate = models.IntegerField(null=True, blank=True, help_text="Heart Rate (bpm)")
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="Respiratory Rate (breaths/min)")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vitals'

    def __str__(self):
        return f"Vitals for {self.patient_visit.patient.get_full_name()} on {self.recorded_at.strftime('%Y-%m-%d')}"


# --- Medication Model ---
class Medication(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    dosage_mg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Dosage in milligrams")
    unit = models.CharField(max_length=50, blank=True, null=True) # e.g., 'mg', 'ml', 'tablet'
    stock_item = models.OneToOneField(StockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='medication_details')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# --- Prescription Model ---
class Prescription(models.Model):
    patient_visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, related_name='prescriptions')
    dosage = models.CharField(max_length=255, help_text="e.g., '1 tablet', '5ml'")
    frequency = models.CharField(max_length=255, help_text="e.g., 'Twice daily', 'Every 4 hours'")
    duration_days = models.IntegerField(help_text="Duration in days")
    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions_written')
    prescription_date = models.DateTimeField(default=timezone.now)
    is_dispensed = models.BooleanField(default=False)
    dispensed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-prescription_date']

    def __str__(self):
        return f"Prescription for {self.patient_visit.patient.get_full_name()} - {self.medication.name}"


# --- Adverse Drug Reaction (ADR) Model ---
class AdverseDrugReaction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='adverse_drug_reactions')
    medication = models.ForeignKey(Medication, on_delete=models.SET_NULL, null=True, blank=True, related_name='adverse_reactions_reported')
    reaction_description = models.TextField(help_text="Detailed description of the adverse reaction.")
    reaction_date = models.DateField(default=timezone.now)
    severity = models.CharField(max_length=50, blank=True, null=True, help_text="Severity of the reaction (e.g., Mild, Moderate, Severe, Life-threatening)")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='adrs_reported')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Adverse Drug Reaction'
        verbose_name_plural = 'Adverse Drug Reactions'
        ordering = ['-reaction_date']

    def __str__(self):
        return f"ADR for {self.patient.get_full_name()} - {self.reaction_description[:50]}..."


# --- Adverse Event Following Immunization (AEFI) Model ---
class AdverseEventFollowingImmunization(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='aefis')
    immunization_name = models.CharField(max_length=255, help_text="Name of the vaccine or immunization.")
    event_description = models.TextField(help_text="Detailed description of the adverse event.")
    event_date = models.DateField(default=timezone.now)
    severity = models.CharField(max_length=50, blank=True, null=True, help_text="Severity of the event (e.g., Mild, Moderate, Severe, Life-threatening)")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aefis_reported')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Adverse Event Following Immunization'
        verbose_name_plural = 'Adverse Events Following Immunization'
        ordering = ['-event_date']

    def __str__(self):
        return f"AEFI for {self.patient.get_full_name()} - {self.immunization_name}"


# --- Order History Model ---
class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    change_date = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255, help_text="e.g., 'Created', 'Updated Status', 'Added Item'")
    description = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_history_changes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order History'
        verbose_name_plural = 'Order History'
        ordering = ['-change_date']

    def __str__(self):
        return f"Order {self.order.id} - {self.action} on {self.change_date.strftime('%Y-%m-%d %H:%M')}"


# --- Payment Transaction Model ---
class PaymentTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Mobile Money', 'Mobile Money'),
        ('Insurance', 'Insurance'),
        ('Other', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_date = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payments')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Payment of {self.amount} by {self.patient.get_full_name() if self.patient else 'N/A'} ({self.payment_method})"


# --- Inventory History Model ---
class InventoryHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('In', 'In'),
        ('Out', 'Out'),
        ('Adjustment', 'Adjustment'),
    ]

    # Modified: Allow stock_item to be null on deletion
    stock_item = models.ForeignKey(StockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_history')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    quantity_change = models.DecimalField(max_digits=10, decimal_places=2) # Positive for In, negative for Out/Adjustment
    new_stock_level = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, null=True, help_text="Reason for the inventory change")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_inventory_changes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventory History'
        verbose_name_plural = 'Inventory History'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Inventory change for {self.stock_item.name if self.stock_item else 'Deleted Item'} - {self.transaction_type} of {self.quantity_change}"