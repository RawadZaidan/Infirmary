from decimal import Decimal
from django import forms
from .models import InventoryItem, LabTest, TestConsumption, DailyLogEntry


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'category', 'unit', 'quantity_in_stock', 'reorder_threshold']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. mL, pieces, boxes'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0'}),
            'reorder_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0'}),
        }


class RestockForm(forms.Form):
    quantity = forms.DecimalField(
        max_digits=12, decimal_places=4, min_value=Decimal('0.0001'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'placeholder': 'Qty to add'}),
    )
    reason = forms.CharField(
        max_length=500, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason (optional)'}),
    )


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Test name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class TestConsumptionForm(forms.ModelForm):
    class Meta:
        model = TestConsumption
        fields = ['inventory_item', 'quantity_consumed_per_test']
        widgets = {
            'inventory_item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_consumed_per_test': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0.0001', 'placeholder': 'Qty per test'}),
        }


class DailyLogEntryForm(forms.ModelForm):
    class Meta:
        model = DailyLogEntry
        fields = ['lab_test', 'quantity_performed']
        widgets = {
            'lab_test': forms.Select(attrs={'class': 'form-control'}),
            'quantity_performed': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Times performed'}),
        }


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
