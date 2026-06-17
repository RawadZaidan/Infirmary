from django import template

register = template.Library()


@register.filter
def status_class(status):
    return {'OK': 'ok', 'LOW': 'low', 'DEFICIT': 'deficit'}.get(status, 'ok')


@register.filter
def abs_val(value):
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value


@register.filter
def mul(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0


@register.filter
def qty(value):
    """Round to 2 decimal places, strip trailing zeros."""
    try:
        from decimal import Decimal, ROUND_HALF_UP
        rounded = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        normalized = rounded.normalize()
        # Never show scientific notation for small numbers
        return format(normalized, 'f')
    except Exception:
        return value


@register.filter
def currency(value):
    """Format as currency with 2 decimal places, e.g. $1,234.56"""
    try:
        from decimal import Decimal
        d = Decimal(str(value))
        return '${:,.2f}'.format(d)
    except Exception:
        return value


@register.filter
def pct(value):
    """Format as percentage with 1 decimal place."""
    try:
        from decimal import Decimal
        return '{:.1f}%'.format(Decimal(str(value)))
    except Exception:
        return value
