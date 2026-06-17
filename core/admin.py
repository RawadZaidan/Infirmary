from django.contrib import admin
from django.utils.html import format_html
from .models import DailyLog, DailyLogEntry, InventoryItem, LabTest, PurchaseOrder, StockMovement, TestConsumption


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'quantity_in_stock', 'reorder_threshold', 'unit_cost', 'stock_value_display', 'status']
    list_filter = ['category']
    search_fields = ['name']
    list_editable = ['unit_cost']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Item Details', {'fields': ['name', 'category', 'unit']}),
        ('Stock Levels', {'fields': ['quantity_in_stock', 'reorder_threshold']}),
        ('Financials', {'fields': ['unit_cost']}),
        ('Timestamps', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]

    @admin.display(description='Stock Value')
    def stock_value_display(self, obj):
        if obj.unit_cost and obj.quantity_in_stock > 0:
            val = obj.unit_cost * obj.quantity_in_stock
            return format_html('<span style="color:#58a6ff;">${}</span>', f'{val:.2f}')
        return '—'


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'selling_price', 'consumption_count', 'created_at']
    search_fields = ['name']
    list_editable = ['selling_price']
    readonly_fields = ['created_at']

    @admin.display(description='# Items')
    def consumption_count(self, obj):
        return obj.consumptions.count()


@admin.register(TestConsumption)
class TestConsumptionAdmin(admin.ModelAdmin):
    list_display = ['lab_test', 'inventory_item', 'quantity_consumed_per_test', 'line_cost']
    list_filter = ['lab_test']
    search_fields = ['lab_test__name', 'inventory_item__name']

    @admin.display(description='Cost / Run')
    def line_cost(self, obj):
        if obj.inventory_item.unit_cost:
            cost = obj.inventory_item.unit_cost * obj.quantity_consumed_per_test
            return format_html('${}', f'{cost:.4f}')
        return '—'


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['date', 'entry_count', 'notes']

    @admin.display(description='Entries')
    def entry_count(self, obj):
        return obj.entries.count()


@admin.register(DailyLogEntry)
class DailyLogEntryAdmin(admin.ModelAdmin):
    list_display = ['daily_log', 'lab_test', 'quantity_performed']
    list_filter = ['lab_test', 'daily_log__date']
    date_hierarchy = 'daily_log__date'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'movement_type', 'quantity', 'reason', 'timestamp']
    list_filter = ['movement_type', 'inventory_item']
    search_fields = ['inventory_item__name', 'reason']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['date', 'inventory_item', 'quantity', 'unit_cost', 'total_cost_display', 'supplier']
    list_filter = ['date', 'inventory_item']
    search_fields = ['inventory_item__name', 'supplier']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    fieldsets = [
        ('Order Details', {'fields': ['inventory_item', 'quantity', 'unit_cost', 'supplier', 'date']}),
        ('Notes', {'fields': ['notes']}),
        ('Meta', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]

    @admin.display(description='Total Cost')
    def total_cost_display(self, obj):
        return format_html('<strong>${}</strong>', f'{obj.total_cost:.2f}')
