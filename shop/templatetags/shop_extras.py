from django import template


register = template.Library()


@register.filter
def vnd(value):
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        number = 0
    return f"{number:,}".replace(",", ".") + " đ"
