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
    if value == 1 or value == "1":
        return value
    else:
        return value + 1

@register.filter
def dds(value):
    value = float(value)
    value_without_dds = value /  1.2
    dds = value - value_without_dds
    return f"{dds:.2f}"

@register.filter
def total_price_withot_dds(value):
    value = float(value)
    value_without_dds = value / 1,2
    return str(value_without_dds)
