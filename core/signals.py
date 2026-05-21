from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import StockMovement, InventoryItem, LabTest


def _bust():
    cache.delete('activity_feed')


@receiver(post_save, sender=StockMovement)
@receiver(post_delete, sender=StockMovement)
def bust_on_stock(sender, **kwargs):
    _bust()


@receiver(post_save, sender=InventoryItem)
@receiver(post_delete, sender=InventoryItem)
def bust_on_item(sender, **kwargs):
    _bust()


@receiver(post_save, sender=LabTest)
@receiver(post_delete, sender=LabTest)
def bust_on_test(sender, **kwargs):
    _bust()
