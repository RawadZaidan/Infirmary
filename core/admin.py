from django.contrib import admin
from .models import DailyLog, DailyLogEntry, InventoryItem, LabTest, StockMovement, TestConsumption


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'quantity_in_stock', 'reorder_threshold', 'status']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(TestConsumption)
class TestConsumptionAdmin(admin.ModelAdmin):
    list_display = ['lab_test', 'inventory_item', 'quantity_consumed_per_test']
    list_filter = ['lab_test']


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['date', 'notes']


@admin.register(DailyLogEntry)
class DailyLogEntryAdmin(admin.ModelAdmin):
    list_display = ['daily_log', 'lab_test', 'quantity_performed']
    list_filter = ['lab_test']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'movement_type', 'quantity', 'reason', 'timestamp']
    list_filter = ['movement_type', 'inventory_item']
    readonly_fields = ['timestamp']
