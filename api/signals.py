# healthlink-backend/api/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderItem, StockItem, OrderHistory, InventoryHistory, User

# Helper to get the user context for signals
def get_user_for_signal(kwargs, instance):
    """
    Attempts to get the user who triggered the signal.
    Prioritizes 'changed_by_user' from kwargs, then instance.created_by,
    then tries to find a superuser, finally falls back to any user.
    """
    user = kwargs.get('changed_by_user')
    if user:
        return user
    
    if hasattr(instance, 'created_by') and instance.created_by:
        return instance.created_by
    
    # Fallback to a superuser or any user if available (for background/system tasks)
    system_user = User.objects.filter(is_superuser=True).first()
    if system_user:
        return system_user
    
    return User.objects.first() # Last resort, might be None if no users exist

# Signal for Order model changes
@receiver(post_save, sender=Order)
def log_order_history_on_save(sender, instance, created, **kwargs):
    action = 'Created Order' if created else 'Updated Order'
    description = f'Order {instance.id} {action.lower()}. Status: {instance.status}. Total: {instance.total_amount}.'
    
    changed_by = get_user_for_signal(kwargs, instance)

    OrderHistory.objects.create(
        order=instance,
        action=action, # Assuming OrderHistory has an 'action' field
        description=description, # Assuming OrderHistory has a 'description' field
        changed_by=changed_by,
        timestamp=timezone.now()
    )

@receiver(post_delete, sender=Order)
def log_order_history_on_delete(sender, instance, **kwargs):
    changed_by = get_user_for_signal(kwargs, instance)

    OrderHistory.objects.create(
        order=None, # Order might be deleted, so link becomes null
        action='Deleted Order', # Assuming OrderHistory has an 'action' field
        description=f'Order {instance.id} was deleted.', # Assuming OrderHistory has a 'description' field
        changed_by=changed_by,
        timestamp=timezone.now()
    )

# Signal for OrderItem model changes
@receiver(post_save, sender=OrderItem)
def log_order_item_history_on_save(sender, instance, created, **kwargs):
    action = 'Created OrderItem' if created else 'Updated OrderItem'
    description = f'Order Item {instance.id} ({instance.stock_item.name}, Qty: {instance.quantity}, Price: {instance.unit_price}) for Order {instance.order.id} {action.lower()}.'

    changed_by = get_user_for_signal(kwargs, instance.order) # Use order's created_by as context if available

    OrderHistory.objects.create(
        order=instance.order,
        action=action, # Assuming OrderHistory has an 'action' field
        description=description, # Assuming OrderHistory has a 'description' field
        changed_by=changed_by,
        timestamp=timezone.now()
    )

@receiver(post_delete, sender=OrderItem)
def log_order_item_history_on_delete(sender, instance, **kwargs):
    changed_by = get_user_for_signal(kwargs, instance.order)

    OrderHistory.objects.create(
        order=instance.order,
        action='Deleted OrderItem', # Assuming OrderHistory has an 'action' field
        description=f'Order Item {instance.id} ({instance.stock_item.name}) for Order {instance.order.id} was deleted.', # Assuming OrderHistory has a 'description' field
        changed_by=changed_by,
        timestamp=timezone.now()
    )

# Signal for StockItem model changes (for InventoryHistory)
@receiver(post_save, sender=StockItem)
def log_inventory_history_on_save(sender, instance, created, **kwargs):
    changed_by_user = get_user_for_signal(kwargs, instance)
    
    transaction_type = 'Adjustment'
    quantity_change = 0.00
    reason_text = "Stock item updated."
    
    if created:
        transaction_type = 'In'
        quantity_change = instance.current_stock
        reason_text = f'Stock Item {instance.name} (ID: {instance.id}) created with initial stock: {instance.current_stock}.'
    else:
        try:
            # Retrieve the old instance to calculate the change in stock
            old_instance = sender.objects.get(pk=instance.pk)
            stock_difference = instance.current_stock - old_instance.current_stock

            if stock_difference > 0:
                transaction_type = 'In'
                quantity_change = stock_difference
                reason_text = f'Stock Item {instance.name} (ID: {instance.id}) stock increased by {abs(stock_difference)} to {instance.current_stock}.'
            elif stock_difference < 0:
                transaction_type = 'Out'
                quantity_change = stock_difference # This will be negative
                reason_text = f'Stock Item {instance.name} (ID: {instance.id}) stock decreased by {abs(stock_difference)} to {instance.current_stock}.'
            else:
                transaction_type = 'Adjustment' # No change in stock, but other fields might have changed
                quantity_change = 0.00
                reason_text = f'Stock Item {instance.name} (ID: {instance.id}) details updated (no stock change). Current Stock: {instance.current_stock}.'
        except sender.DoesNotExist:
            # This case might occur if the signal fires for an instance that somehow wasn't retrieved
            # or if initial objects are created outside typical API calls.
            transaction_type = 'Adjustment'
            quantity_change = instance.current_stock # Assume initial if old instance not found
            reason_text = f'Stock Item {instance.name} (ID: {instance.id}) saved, initial record or unexpected update.'

    InventoryHistory.objects.create(
        stock_item=instance,
        transaction_type=transaction_type, # Correctly maps to model's field
        quantity_change=quantity_change, # Correctly maps to model's field
        new_stock_level=instance.current_stock, # Correctly maps to model's field
        reason=reason_text, # Correctly maps to model's field
        processed_by=changed_by_user,
        transaction_date=timezone.now(),
    )

@receiver(post_delete, sender=StockItem)
def log_inventory_history_on_delete(sender, instance, **kwargs):
    changed_by_user = get_user_for_signal(kwargs, instance)

    InventoryHistory.objects.create(
        stock_item=None, # StockItem is deleted, so link becomes null
        transaction_type='Out', # Type for deletion
        quantity_change=-instance.current_stock, # Log the quantity removed from inventory
        new_stock_level=0.00, # After deletion, stock for this item is effectively 0
        reason=f'Stock Item {instance.name} (ID: {instance.id}) was deleted. Quantity at deletion: {instance.current_stock}.', # Correctly maps to model's field
        processed_by=changed_by_user,
        transaction_date=timezone.now(),
    )