from decimal import Decimal, ROUND_HALF_UP
from itertools import islice
from django.core.cache import cache
from .models import InventoryItem, LabTest, StockMovement

ACTIVITY_FEED_TTL = 60


def _fmt(value):
    try:
        rounded = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return format(rounded.normalize(), 'f')
    except Exception:
        return value


def _build_activity_feed():
    events = []

    for m in StockMovement.objects.select_related('inventory_item').order_by('-timestamp')[:20]:
        if m.movement_type == 'ADD':
            label = f"Restocked {_fmt(m.quantity)} {m.inventory_item.unit} of {m.inventory_item.name}"
            kind = 'add'
        else:
            label = f"Used {_fmt(m.quantity)} {m.inventory_item.unit} of {m.inventory_item.name}"
            kind = 'deduct'
        events.append({'ts': m.timestamp, 'label': label, 'kind': kind})

    for item in InventoryItem.objects.order_by('-created_at')[:10]:
        events.append({'ts': item.created_at, 'label': f"New item added: {item.name}", 'kind': 'new_item'})

    for test in LabTest.objects.order_by('-created_at')[:10]:
        events.append({'ts': test.created_at, 'label': f"New test added: {test.name}", 'kind': 'new_test'})

    events.sort(key=lambda e: e['ts'], reverse=True)
    return list(islice(events, 5))


def activity_feed(request):
    if not request.user.is_authenticated:
        return {}

    cache_key = 'activity_feed'
    feed = cache.get(cache_key)
    if feed is None:
        feed = _build_activity_feed()
        cache.set(cache_key, feed, ACTIVITY_FEED_TTL)

    return {'activity_feed': feed}
