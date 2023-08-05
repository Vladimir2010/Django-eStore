from django import template
from cart.utils import get_or_set_order_session

register = template.Library()


@register.filter
def cart_item_count(request):
    order = get_or_set_order_session(request)
    count = order.items.count()
    return count


@register.filter
def increment(value):
    return value + 1

@register.filter
def dds(value):
    value = int(value)
    value_with_dds = value * 1,2
    dds = value_with_dds - value
    return str(dds)

@register.filter
def total_price_withot_dds(value):
    value = int(value)
    value_without_dds = value / 1,2
    return str(value_without_dds)