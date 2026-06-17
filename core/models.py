import datetime
from decimal import Decimal
from django.db import models


class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('REAGENT', 'Reagent'),
        ('CONSUMABLE', 'Consumable'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=50)
    quantity_in_stock = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0'))
    reorder_threshold = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0'))
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True,
                                    help_text='Cost per unit (used for inventory valuation and test costing)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low(self):
        return self.quantity_in_stock <= self.reorder_threshold

    @property
    def is_deficit(self):
        return self.quantity_in_stock < Decimal('0')

    @property
    def status(self):
        if self.is_deficit:
            return 'DEFICIT'
        if self.is_low:
            return 'LOW'
        return 'OK'

    @property
    def stock_value(self):
        if self.unit_cost is None:
            return None
        return self.unit_cost * self.quantity_in_stock


class LabTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True,
                                        help_text='Revenue charged per test run')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TestConsumption(models.Model):
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='consumptions')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='test_consumptions')
    quantity_consumed_per_test = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        unique_together = [('lab_test', 'inventory_item')]

    def __str__(self):
        return f"{self.lab_test} — {self.inventory_item} x{self.quantity_consumed_per_test}"


class DailyLog(models.Model):
    date = models.DateField(unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Log {self.date}"


class DailyLogEntry(models.Model):
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='entries')
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    quantity_performed = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.lab_test} x{self.quantity_performed} ({self.daily_log.date})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self._deduct_inventory()

    def _deduct_inventory(self):
        for consumption in self.lab_test.consumptions.select_related('inventory_item').all():
            item = consumption.inventory_item
            deduction = consumption.quantity_consumed_per_test * self.quantity_performed
            item.quantity_in_stock -= deduction
            item.save(update_fields=['quantity_in_stock', 'updated_at'])
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='DEDUCT',
                quantity=deduction,
                reason=f"Daily log {self.daily_log.date}: {self.lab_test.name} x{self.quantity_performed}",
            )


class StockMovement(models.Model):
    MOVEMENT_CHOICES = [
        ('ADD', 'Add'),
        ('DEDUCT', 'Deduct'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    reason = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.movement_type} {self.quantity} of {self.inventory_item}"


class PurchaseOrder(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='purchase_orders')
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4)
    supplier = models.CharField(max_length=200, blank=True)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"PO {self.date}: {self.inventory_item} x{self.quantity} @ {self.unit_cost}"

    @property
    def total_cost(self):
        return self.unit_cost * self.quantity
