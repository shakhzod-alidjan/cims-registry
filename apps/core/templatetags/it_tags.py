from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def split(value, sep=','):
    """{{ "a,b,c"|split:"," }} → ['a','b','c']"""
    return value.split(sep)


@register.simple_tag
def days_left(date):
    """Return days left until date, or None."""
    if not date:
        return None
    return (date - timezone.now().date()).days


@register.filter
def status_color(status):
    return {
        'expired':      'var(--red)',
        'expiring_soon':'var(--amber)',
        'expiring':     'var(--amber)',
        'active':       'var(--green)',
    }.get(status, 'var(--muted)')


@register.filter
def uzs_millions(value):
    """Format UZS as millions: 3 900 000 → 3.9 млн"""
    try:
        v = float(value)
        if v >= 1_000_000:
            return f'{v/1_000_000:.1f} млн'
        return f'{v:,.0f}'
    except (TypeError, ValueError):
        return '—'


@register.filter
def expiry_class(days):
    """Return CSS class based on days_until_expiry value."""
    if days is None:
        return ''
    if days <= 0:
        return 'td-exp'
    if days <= 30:
        return 'td-exp'
    if days <= 90:
        return 'td-warn'
    return ''


@register.filter
def expiry_label(days):
    """Return human-readable expiry label."""
    if days is None:
        return '—'
    if days <= 0:
        return 'Истёк'
    return f'{days} дн.'


@register.filter
def expiry_pill_class(days):
    """Return pill CSS class based on days."""
    if days is None:
        return 'p-green'
    if days <= 0:
        return 'p-red'
    if days <= 90:
        return 'p-amber'
    return 'p-green'


@register.filter
def can_edit(user):
    return getattr(user, 'is_editor', False) or getattr(user, 'is_superuser', False)


@register.filter
def can_admin(user):
    return getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False)


@register.filter
def currency(value, prefix='$'):
    """Format number as currency: 42000 → $42,000"""
    try:
        return f'{prefix}{float(value):,.0f}'
    except (TypeError, ValueError):
        return '—'


@register.filter
def mul(value, arg):
    """Multiply: {{ value|mul:12 }}"""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0
