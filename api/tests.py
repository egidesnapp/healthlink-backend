# healthlink-backend/api/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from datetime import date, timedelta

from .models import User, Facility, Role, StockItem, InventoryHistory # Import InventoryHistory
from .serializers import StockItemSerializer
# Ensure permissions are correctly imported if used in tests
from .permissions import IsFacilityAdmin, IsPharmacist # Example imports, adjust if your views use others


class StockItemTests(APITestCase):

    def setUp(self):
        """
        Set up test data: roles, facilities, and users with different roles.
        """
        # Create roles
        self.super_admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.facility_admin_role, _ = Role.objects.get_or_create(name='Facility Admin')
        self.pharmacist_role, _ = Role.objects.get_or_create(name='Pharmacist')
        self.doctor_role, _ = Role.objects.get_or_create(name='Doctor')
        self.nurse_role, _ = Role.objects.get_or_create(name='Nurse')
        self.patient_role, _ = Role.objects.get_or_create(name='Patient')
        self.supplier_role, _ = Role.objects.get_or_create(name='Supplier')

        # Create facilities
        self.facility1 = Facility.objects.create(name='Central Hospital', address='123 Main St')
        self.facility2 = Facility.objects.create(name='Community Clinic', address='456 Oak Ave')

        # Create users
        self.super_admin = User.objects.create_user(username='superadmin', email='super@example.com', password='password', role=self.super_admin_role)
        self.facility_admin1 = User.objects.create_user(username='fadmin1', email='fadmin1@example.com', password='password', facility=self.facility1, role=self.facility_admin_role)
        self.pharmacist1 = User.objects.create_user(username='pharmacist1', email='pharma1@example.com', password='password', facility=self.facility1, role=self.pharmacist_role)
        self.doctor1 = User.objects.create_user(username='doctor1', email='doctor1@example.com', password='password', facility=self.facility1, role=self.doctor_role)
        self.facility_admin2 = User.objects.create_user(username='fadmin2', email='fadmin2@example.com', password='password', facility=self.facility2, role=self.facility_admin_role)
        self.supplier_user = User.objects.create_user(username='supplier1', email='supplier1@example.com', password='password', role=self.supplier_role)


        # Create StockItems for testing
        # Corrected StockItem creation based on new model fields
        self.stock_item1 = StockItem.objects.create(
            name='Paracetamol 500mg',
            current_stock=100.00,
            unit='Tablets', # Changed from unit_of_measure
            reorder_level=20.00, # Changed from min_stock_level
            expiry_date=date.today() + timedelta(days=365),
            location=self.facility1, # Changed from facility, assuming location links to Facility
            purchase_price=5.00,
            sale_price=10.00,
            created_by=self.pharmacist1 # Added created_by as it's a new field and likely required
        )
        self.stock_item_expired = StockItem.objects.create(
            name='Amoxicillin 250mg',
            current_stock=10.00,
            unit='Capsules',
            reorder_level=5.00,
            expiry_date=date.today() - timedelta(days=30), # Expired item
            location=self.facility1,
            purchase_price=15.00,
            sale_price=25.00,
            created_by=self.pharmacist1
        )
        self.stock_item_facility2 = StockItem.objects.create(
            name='Ibuprofen 400mg',
            current_stock=50.00,
            unit='Tablets',
            reorder_level=10.00,
            expiry_date=date.today() + timedelta(days=180),
            location=self.facility2, # Item for another facility
            purchase_price=7.00,
            sale_price=12.00,
            created_by=self.facility_admin2
        )

        # Clients for different user types
        self.client = APIClient()
        self.facility_admin_client = APIClient()
        self.facility_admin_client.force_authenticate(user=self.facility_admin1)
        self.pharmacist_client = APIClient()
        self.pharmacist_client.force_authenticate(user=self.pharmacist1)
        self.doctor_client = APIClient()
        self.doctor_client.force_authenticate(user=self.doctor1)
        self.unauthenticated_client = APIClient() # No authentication


    def test_stock_item_creation_by_facility_admin(self):
        """
        Ensure a Facility Admin can create a new StockItem.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        data = {
            'name': 'New Test Item',
            'current_stock': 50.00,
            'unit': 'Packs', # Use 'unit'
            'reorder_level': 10.00, # Use 'reorder_level'
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'location': self.facility1.id, # Link to facility using 'location'
            'purchase_price': 20.00,
            'sale_price': 30.00,
            'created_by': self.facility_admin1.id # Ensure created_by is provided
        }
        response = self.client.post(reverse('stockitem-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StockItem.objects.count(), 4) # 3 initial + 1 new
        self.assertEqual(StockItem.objects.get(name='New Test Item').current_stock, 50.00)
        self.assertEqual(StockItem.objects.get(name='New Test Item').location, self.facility1)
        self.assertEqual(StockItem.objects.get(name='New Test Item').created_by, self.facility_admin1)

    def test_stock_item_creation_by_pharmacist(self):
        """
        Ensure a Pharmacist can create a new StockItem.
        """
        self.client.force_authenticate(user=self.pharmacist1)
        data = {
            'name': 'Pharmacist Item',
            'current_stock': 25.00,
            'unit': 'Bottles',
            'reorder_level': 5.00,
            'expiry_date': (date.today() + timedelta(days=180)).isoformat(),
            'location': self.facility1.id,
            'purchase_price': 10.00,
            'sale_price': 18.00,
            'created_by': self.pharmacist1.id
        }
        response = self.client.post(reverse('stockitem-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StockItem.objects.count(), 4)
        self.assertEqual(StockItem.objects.get(name='Pharmacist Item').current_stock, 25.00)

    def test_stock_item_creation_unauthorized(self):
        """
        Ensure users without appropriate roles (e.g., Doctor, unauthenticated) cannot create StockItems.
        """
        # Test with a Doctor user
        self.client.force_authenticate(user=self.doctor1)
        data = {
            'name': 'Unauthorized Item',
            'current_stock': 10.00,
            'unit': 'Vials',
            'reorder_level': 2.00,
            'expiry_date': (date.today() + timedelta(days=90)).isoformat(),
            'location': self.facility1.id,
            'purchase_price': 5.00,
            'sale_price': 8.00,
            'created_by': self.doctor1.id
        }
        response = self.client.post(reverse('stockitem-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Doctors should not create StockItems

        # Test with unauthenticated user
        self.client.force_authenticate(user=None) # Unauthenticate
        response = self.client.post(reverse('stockitem-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # Unauthenticated users should not create StockItems

    def test_list_stock_items_by_facility_admin(self):
        """
        Ensure a Facility Admin only sees stock items from their facility.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        response = self.client.get(reverse('stockitem-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Facility Admin 1 should see stock_item1 and stock_item_expired
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.stock_item1.name, [item['name'] for item in response.data])
        self.assertIn(self.stock_item_expired.name, [item['name'] for item in response.data])
        self.assertNotIn(self.stock_item_facility2.name, [item['name'] for item in response.data])

    def test_list_stock_items_by_pharmacist(self):
        """
        Ensure a Pharmacist only sees stock items from their facility.
        """
        self.client.force_authenticate(user=self.pharmacist1)
        response = self.client.get(reverse('stockitem-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pharmacist 1 should see stock_item1 and stock_item_expired
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.stock_item1.name, [item['name'] for item in response.data])
        self.assertIn(self.stock_item_expired.name, [item['name'] for item in response.data])
        self.assertNotIn(self.stock_item_facility2.name, [item['name'] for item in response.data])

    def test_list_stock_items_other_facility_admin_sees_only_their_items(self):
        """
        Ensure an admin from Facility 2 only sees items for Facility 2.
        """
        self.client.force_authenticate(user=self.facility_admin2)
        response = self.client.get(reverse('stockitem-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(self.stock_item_facility2.name, [item['name'] for item in response.data])
        self.assertNotIn(self.stock_item1.name, [item['name'] for item in response.data])

    def test_retrieve_stock_item_by_facility_admin(self):
        """
        Ensure a Facility Admin can retrieve a specific stock item from their facility.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        url = reverse('stockitem-detail', args=[self.stock_item1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.stock_item1.name)

    def test_retrieve_stock_item_from_other_facility_unauthorized(self):
        """
        Ensure a Facility Admin cannot retrieve a stock item from another facility.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        url = reverse('stockitem-detail', args=[self.stock_item_facility2.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Should not be found if filtered by facility

    def test_delete_stock_item_by_facility_admin(self):
        """
        Ensure a Facility Admin can delete a stock item from their facility.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        stock_item_to_delete_id = self.stock_item_expired.id # Use the expired item for deletion test
        stock_item_name = self.stock_item_expired.name
        
        url = reverse('stockitem-detail', args=[stock_item_to_delete_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that an InventoryHistory entry was created for deletion
        # When a StockItem is deleted (CASCADE), its foreign key in InventoryHistory records
        # that referred to it might become null. The signal handles this by setting stock_item=None.
        deleted_history_entry = InventoryHistory.objects.filter(
            stock_item__isnull=True, # Look for records where stock_item is null after deletion
            description__icontains=f'Stock Item {stock_item_name} (ID: {stock_item_to_delete_id}) was deleted'
        ).first()
        
        self.assertIsNotNone(deleted_history_entry, "No InventoryHistory entry found for StockItem deletion.")
        self.assertEqual(deleted_history_entry.transaction_type, 'Out') # Or 'Adjustment' depending on signal logic
        self.assertEqual(deleted_history_entry.quantity_change, -10.00) # Quantity at deletion was 10, so -10
        self.assertEqual(deleted_history_entry.processed_by, self.facility_admin1) # The user who deleted it
        self.assertEqual(StockItem.objects.filter(id=stock_item_to_delete_id).exists(), False) # Ensure it's deleted

    def test_delete_stock_item_unauthorized(self):
        """
        Ensure unauthorized users (e.g., Pharmacist, other Facility Admin) cannot delete stock items.
        """
        stock_item_to_delete = self.stock_item1 # Attempt to delete an item
        initial_stock_item_count = StockItem.objects.count()

        # Test with Pharmacist (should not have delete permission)
        self.client.force_authenticate(user=self.pharmacist1)
        url = reverse('stockitem-detail', args=[stock_item_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StockItem.objects.count(), initial_stock_item_count) # Item should not be deleted

        # Test with a Facility Admin from a different facility
        self.client.force_authenticate(user=self.facility_admin2)
        url = reverse('stockitem-detail', args=[stock_item_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Should not find item to delete

        # Test with unauthenticated user
        self.client.force_authenticate(user=None)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(StockItem.objects.count(), initial_stock_item_count) # Item should not be deleted

    def test_inventory_history_creation_on_stock_item_creation(self):
        """
        Verify that an InventoryHistory entry is created when a StockItem is initially created.
        """
        self.client.force_authenticate(user=self.pharmacist1)
        initial_history_count = InventoryHistory.objects.count()
        data = {
            'name': 'Newly Added Stock',
            'current_stock': 75.00,
            'unit': 'Units',
            'reorder_level': 15.00,
            'expiry_date': (date.today() + timedelta(days=200)).isoformat(),
            'location': self.facility1.id,
            'purchase_price': 10.00,
            'sale_price': 15.00,
            'created_by': self.pharmacist1.id
        }
        response = self.client.post(reverse('stockitem-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryHistory.objects.count(), initial_history_count + 1)

        new_stock_item = StockItem.objects.get(name='Newly Added Stock')
        history_entry = InventoryHistory.objects.filter(stock_item=new_stock_item, action='Created StockItem').first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.quantity_change, new_stock_item.current_stock)
        self.assertEqual(history_entry.processed_by, self.pharmacist1)

    def test_inventory_history_creation_on_stock_item_update(self):
        """
        Verify that an InventoryHistory entry is created when a StockItem's stock is updated.
        """
        self.client.force_authenticate(user=self.facility_admin1)
        initial_history_count = InventoryHistory.objects.count()
        
        # Update current_stock
        update_data = {'current_stock': self.stock_item1.current_stock + 20.00}
        url = reverse('stockitem-detail', args=[self.stock_item1.id])
        response = self.client.patch(url, update_data, format='json') # Use PATCH for partial update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.stock_item1.refresh_from_db() # Refresh instance to get updated values
        self.assertEqual(self.stock_item1.current_stock, 120.00)
        
        self.assertEqual(InventoryHistory.objects.count(), initial_history_count + 1)
        history_entry = InventoryHistory.objects.filter(stock_item=self.stock_item1, action='Updated StockItem').order_by('-timestamp').first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.quantity_change, 20.00)
        self.assertEqual(history_entry.processed_by, self.facility_admin1)

    def test_inventory_history_creation_on_stock_item_deletion(self):
        """
        Verify that an InventoryHistory entry is created when a StockItem is deleted.
        (This test is similar to test_delete_stock_item_by_facility_admin but focuses on history)
        """
        self.client.force_authenticate(user=self.facility_admin1)
        initial_history_count = InventoryHistory.objects.count()
        stock_item_to_delete_id = self.stock_item_expired.id
        stock_item_name = self.stock_item_expired.name
        stock_item_quantity_at_deletion = self.stock_item_expired.current_stock

        url = reverse('stockitem-detail', args=[stock_item_to_delete_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(InventoryHistory.objects.count(), initial_history_count + 1)
        deleted_history_entry = InventoryHistory.objects.filter(
            stock_item__isnull=True, # StockItem foreign key becomes null on CASCADE delete
            description__icontains=f'Stock Item {stock_item_name} (ID: {stock_item_to_delete_id}) was deleted'
        ).first()
        self.assertIsNotNone(deleted_history_entry, "No InventoryHistory entry found for StockItem deletion.")
        self.assertEqual(deleted_history_entry.action, 'Deleted StockItem')
        self.assertEqual(deleted_history_entry.quantity_change, -stock_item_quantity_at_deletion) # Negative of quantity at deletion
        self.assertEqual(deleted_history_entry.processed_by, self.facility_admin1)


    def test_stock_item_list_filter_by_category(self):
        """
        Test filtering stock items by category.
        NOTE: 'category' field was removed from StockItem. This test will now
        need to be adapted or removed if category filtering is no longer supported
        or if category is managed differently (e.g., via a related model).
        For now, this test will be modified to expect an empty list or an error
        if the filtering by a non-existent field is attempted in the viewset,
        or it should be updated to filter by a *new* relevant field if one exists.
        Given 'category' was removed, we should remove this test or refactor.
        For demonstration, I'll remove it as the field doesn't exist.
        """
        pass # This test is no longer valid due to 'category' field removal.

    def test_stock_item_list_filter_by_current_stock_min_max(self):
        """
        Test filtering by minimum and maximum current stock levels.
        """
        self.client.force_authenticate(user=self.facility_admin1)

        # Test min_stock filter
        response = self.client.get(reverse('stockitem-list'), {'min_stock': 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Only stock_item1 (100)
        self.assertEqual(response.data[0]['name'], self.stock_item1.name)

        # Test max_stock filter
        response = self.client.get(reverse('stockitem-list'), {'max_stock': 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # stock_item_expired (10) and stock_item_facility2 (50) if accessible
        # If facility filtering is applied first, then only stock_item_expired (10) from facility1
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.stock_item_expired.name)

        # Test min_stock and max_stock combined
        # If stock_item1 has 100, stock_item_expired has 10, stock_item_facility2 has 50
        # For facility_admin1, only stock_item1 (100) and stock_item_expired (10) are relevant.
        response = self.client.get(reverse('stockitem-list'), {'min_stock': 15, 'max_stock': 150}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Only stock_item1 (100) within range for facility_admin1
        self.assertEqual(response.data[0]['name'], self.stock_item1.name)