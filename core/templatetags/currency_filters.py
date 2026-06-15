from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='inr')
def inr_format(value):
    if value is None:
        return '₹0.00'
    try:
        val = Decimal(str(value))
        s = f"{val:.2f}"
        parts = s.split('.')
        int_part = parts[0]
        dec_part = parts[1]
        
        is_negative = False
        if int_part.startswith('-'):
            is_negative = True
            int_part = int_part[1:]

        if len(int_part) <= 3:
            res = int_part
        else:
            last_three = int_part[-3:]
            remaining = int_part[:-3]
            groups = []
            while len(remaining) > 0:
                groups.append(remaining[-2:])
                remaining = remaining[:-2]
            groups.reverse()
            res = ",".join(groups) + "," + last_three

        prefix = "-" if is_negative else ""
        return f"{prefix}₹{res}.{dec_part}"
    except Exception:
        return f"₹{value}"

@register.filter(name='mul')
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
