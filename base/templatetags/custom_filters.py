from django import template

register = template.Library()


@register.filter
def currency(price):
    return f"Price: ${price}"


@register.filter
def discount(price, percentage):
    return (
        f"With discount: {float(price) - (float(price) * float(percentage / 100)):.2f}"
    )
