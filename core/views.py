import csv
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    DateRangeForm,
    DailyLogEntryForm,
    InventoryItemForm,
    LabTestForm,
    RestockForm,
    TestConsumptionForm,
)
from .models import (
    DailyLog,
    DailyLogEntry,
    InventoryItem,
    LabTest,
    StockMovement,
    TestConsumption,
)


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@login_required
def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory/list.html', {'items': items})


@login_required
def inventory_bulk_receive(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_id')
        quantities = request.POST.getlist('quantity')
        reasons = request.POST.getlist('reason')

        received = 0
        errors = []
        for i, item_id in enumerate(item_ids):
            if not item_id:
                continue
            qty_str = quantities[i].strip() if i < len(quantities) else ''
            if not qty_str:
                continue
            try:
                qty = Decimal(qty_str)
                if qty <= 0:
                    raise ValueError
            except Exception:
                errors.append(f'Row {i+1}: invalid quantity.')
                continue
            try:
                item = InventoryItem.objects.get(pk=item_id)
            except InventoryItem.DoesNotExist:
                errors.append(f'Row {i+1}: item not found.')
                continue
            reason = (reasons[i] if i < len(reasons) else '').strip() or 'Bulk receipt'
            item.quantity_in_stock += qty
            item.save(update_fields=['quantity_in_stock', 'updated_at'])
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='ADD',
                quantity=qty,
                reason=reason,
            )
            received += 1

        for e in errors:
            messages.warning(request, e)
        if received:
            messages.success(request, f'{received} item{"s" if received != 1 else ""} restocked.')
        elif not errors:
            messages.info(request, 'No items received — all rows were blank.')
    return redirect('inventory_list')


@login_required
def inventory_edit(request, item_id):
    item = get_object_or_404(InventoryItem, pk=item_id)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated.')
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/edit.html', {'form': form, 'item': item})


@login_required
def inventory_restock(request, item_id):
    item = get_object_or_404(InventoryItem, pk=item_id)
    if request.method == 'POST':
        form = RestockForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            reason = form.cleaned_data['reason'] or 'Manual restock'
            item.quantity_in_stock += qty
            item.save(update_fields=['quantity_in_stock', 'updated_at'])
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='ADD',
                quantity=qty,
                reason=reason,
            )
            messages.success(request, f'Added {qty} {item.unit} to {item.name}.')
        else:
            messages.error(request, 'Invalid restock amount.')
    return redirect('inventory_list')


# ---------------------------------------------------------------------------
# Lab Tests
# ---------------------------------------------------------------------------

@login_required
def test_list(request):
    tests = LabTest.objects.prefetch_related('consumptions').all()
    return render(request, 'tests/list.html', {'tests': tests})


@login_required
def test_bulk_log(request):
    if request.method == 'POST':
        test_ids = request.POST.getlist('test_id')
        quantities = request.POST.getlist('quantity_performed')

        log, _ = DailyLog.objects.get_or_create(date=date.today())
        logged = 0
        errors = []
        for i, test_id in enumerate(test_ids):
            if not test_id:
                continue
            qty_str = quantities[i].strip() if i < len(quantities) else ''
            if not qty_str:
                continue
            try:
                qty = int(qty_str)
                if qty < 1:
                    raise ValueError
            except Exception:
                errors.append(f'Row {i+1}: quantity must be a positive integer.')
                continue
            try:
                test = LabTest.objects.get(pk=test_id)
            except LabTest.DoesNotExist:
                errors.append(f'Row {i+1}: test not found.')
                continue
            DailyLogEntry.objects.create(daily_log=log, lab_test=test, quantity_performed=qty)
            logged += 1

        for e in errors:
            messages.warning(request, e)
        if logged:
            messages.success(request, f'{logged} test entr{"ies" if logged != 1 else "y"} logged for today.')
        elif not errors:
            messages.info(request, 'No entries logged — all rows were blank.')
    return redirect('test_list')


@login_required
def test_add(request):
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            test = form.save()
            messages.success(request, 'Lab test created.')
            return redirect('test_edit', test_id=test.pk)
    else:
        form = LabTestForm()
    return render(request, 'tests/add.html', {'form': form})


@login_required
def test_edit(request, test_id):
    test = get_object_or_404(LabTest, pk=test_id)
    consumptions = test.consumptions.select_related('inventory_item').all()
    form = LabTestForm(instance=test)
    consumption_form = TestConsumptionForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_test':
            form = LabTestForm(request.POST, instance=test)
            if form.is_valid():
                form.save()
                messages.success(request, 'Test updated.')
                return redirect('test_edit', test_id=test.pk)

        elif action == 'add_consumption':
            consumption_form = TestConsumptionForm(request.POST)
            if consumption_form.is_valid():
                c = consumption_form.save(commit=False)
                c.lab_test = test
                try:
                    c.save()
                    messages.success(request, 'Consumption entry added.')
                    return redirect('test_edit', test_id=test.pk)
                except Exception:
                    messages.error(request, 'That item is already mapped to this test.')

        elif action == 'delete_consumption':
            c_id = request.POST.get('consumption_id')
            TestConsumption.objects.filter(pk=c_id, lab_test=test).delete()
            messages.success(request, 'Entry removed.')
            return redirect('test_edit', test_id=test.pk)

    return render(request, 'tests/edit.html', {
        'test': test,
        'form': form,
        'consumption_form': consumption_form,
        'consumptions': consumptions,
    })


# ---------------------------------------------------------------------------
# Daily Log
# ---------------------------------------------------------------------------

@login_required
def daily_log_today(request):
    return redirect('daily_log', date_str=date.today().isoformat())


@login_required
def daily_log(request, date_str):
    try:
        log_date = date.fromisoformat(date_str)
    except ValueError:
        return redirect('daily_log_today')

    log, _ = DailyLog.objects.get_or_create(date=log_date)

    if request.method == 'POST':
        form = DailyLogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.daily_log = log
            entry.save()
            messages.success(request, 'Entry added and inventory updated.')
            return redirect('daily_log', date_str=date_str)
    else:
        form = DailyLogEntryForm()

    entries = log.entries.select_related('lab_test').all()

    consumed = {}
    for entry in entries:
        for c in entry.lab_test.consumptions.select_related('inventory_item').all():
            key = c.inventory_item_id
            if key not in consumed:
                consumed[key] = {'item': c.inventory_item, 'total': Decimal('0')}
            consumed[key]['total'] += c.quantity_consumed_per_test * entry.quantity_performed

    today = date.today()
    prev_date = (log_date - timedelta(days=1)).isoformat()
    next_date = (log_date + timedelta(days=1)).isoformat() if log_date < today else None

    return render(request, 'daily_log/log.html', {
        'log': log,
        'log_date': log_date,
        'form': form,
        'entries': entries,
        'consumed': consumed.values(),
        'is_today': log_date == today,
        'prev_date': prev_date,
        'next_date': next_date,
    })


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@login_required
def reports(request):
    today = date.today()
    default_start = today.replace(day=1)

    form = DateRangeForm(request.GET or None)
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = default_start
        end_date = today

    entries_qs = DailyLogEntry.objects.filter(
        daily_log__date__gte=start_date,
        daily_log__date__lte=end_date,
    )

    total_performed = entries_qs.aggregate(total=Sum('quantity_performed'))['total'] or 0
    unique_test_types = entries_qs.values('lab_test').distinct().count()

    tests_summary = (
        entries_qs
        .values('lab_test__name')
        .annotate(total=Sum('quantity_performed'))
        .order_by('-total')
    )

    movements_qs = StockMovement.objects.filter(
        movement_type='DEDUCT',
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date,
    ).select_related('inventory_item')

    item_consumption = {}
    for m in movements_qs:
        key = m.inventory_item_id
        if key not in item_consumption:
            item_consumption[key] = {'item': m.inventory_item, 'total_consumed': Decimal('0')}
        item_consumption[key]['total_consumed'] += m.quantity
    consumption_summary = sorted(item_consumption.values(), key=lambda x: x['total_consumed'], reverse=True)

    low_stock_items = InventoryItem.objects.filter(
        quantity_in_stock__lte=F('reorder_threshold')
    ).order_by('name')

    return render(request, 'reports/reports.html', {
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'total_performed': total_performed,
        'unique_test_types': unique_test_types,
        'tests_summary': tests_summary,
        'consumption_summary': consumption_summary,
        'low_stock_items': low_stock_items,
        'items_below_threshold': low_stock_items.count(),
    })


@login_required
def reports_export_pdf(request):
    today = date.today()
    try:
        start_date = date.fromisoformat(request.GET.get('start_date', today.replace(day=1).isoformat()))
        end_date = date.fromisoformat(request.GET.get('end_date', today.isoformat()))
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    entries_qs = DailyLogEntry.objects.filter(
        daily_log__date__gte=start_date,
        daily_log__date__lte=end_date,
    )

    total_performed = entries_qs.aggregate(total=Sum('quantity_performed'))['total'] or 0
    unique_test_types = entries_qs.values('lab_test').distinct().count()

    tests_summary = list(
        entries_qs
        .values('lab_test__name')
        .annotate(total=Sum('quantity_performed'))
        .order_by('-total')
    )

    movements_qs = StockMovement.objects.filter(
        movement_type='DEDUCT',
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date,
    ).select_related('inventory_item')

    item_consumption = {}
    for m in movements_qs:
        key = m.inventory_item_id
        if key not in item_consumption:
            item_consumption[key] = {'item': m.inventory_item, 'total_consumed': Decimal('0')}
        item_consumption[key]['total_consumed'] += m.quantity
    consumption_summary = sorted(item_consumption.values(), key=lambda x: x['total_consumed'], reverse=True)

    low_stock_items = InventoryItem.objects.filter(
        quantity_in_stock__lte=F('reorder_threshold')
    ).order_by('name')

    return render(request, 'reports/pdf_report.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_performed': total_performed,
        'unique_test_types': unique_test_types,
        'tests_summary': tests_summary,
        'consumption_summary': consumption_summary,
        'low_stock_items': low_stock_items,
        'items_below_threshold': low_stock_items.count(),
        'generated_on': today,
    })


@login_required
def reports_export(request):
    today = date.today()
    try:
        start_date = date.fromisoformat(request.GET.get('start_date', today.replace(day=1).isoformat()))
        end_date = date.fromisoformat(request.GET.get('end_date', today.isoformat()))
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="biolab_report_{start_date}_{end_date}.csv"'
    writer = csv.writer(response)

    writer.writerow(['BioLab Inventory Report'])
    writer.writerow(['Period', f'{start_date} to {end_date}'])
    writer.writerow([])

    writer.writerow(['TESTS PERFORMED'])
    writer.writerow(['Test Name', 'Total Count'])
    entries = (
        DailyLogEntry.objects
        .filter(daily_log__date__gte=start_date, daily_log__date__lte=end_date)
        .values('lab_test__name')
        .annotate(total=Sum('quantity_performed'))
        .order_by('-total')
    )
    for e in entries:
        writer.writerow([e['lab_test__name'], e['total']])

    writer.writerow([])
    writer.writerow(['INVENTORY CONSUMPTION'])
    writer.writerow(['Item', 'Unit', 'Total Consumed', 'Current Stock', 'Threshold', 'Status'])
    movements = (
        StockMovement.objects
        .filter(movement_type='DEDUCT', timestamp__date__gte=start_date, timestamp__date__lte=end_date)
        .values('inventory_item')
        .annotate(total_consumed=Sum('quantity'))
        .order_by('-total_consumed')
    )
    item_ids = [m['inventory_item'] for m in movements]
    items_map = {i.pk: i for i in InventoryItem.objects.filter(pk__in=item_ids)}
    for m in movements:
        item = items_map.get(m['inventory_item'])
        if item:
            writer.writerow([item.name, item.unit, m['total_consumed'],
                             item.quantity_in_stock, item.reorder_threshold, item.status])

    writer.writerow([])
    writer.writerow(['LOW STOCK ITEMS'])
    writer.writerow(['Item', 'Category', 'Unit', 'Current Stock', 'Threshold', 'Status'])
    for item in InventoryItem.objects.filter(quantity_in_stock__lte=F('reorder_threshold')).order_by('name'):
        writer.writerow([item.name, item.get_category_display(), item.unit,
                         item.quantity_in_stock, item.reorder_threshold, item.status])

    return response
