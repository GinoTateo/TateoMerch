from django import template

register = template.Library()


@register.filter(name='to_int')
def to_int(value):
    """Converts a float value to int if it's a whole number."""
    try:
        return int(value) if value == int(value) else value
    except (ValueError, TypeError):
        return value
