from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()


@register.filter
def dinero(valor):

    if valor is None:
        return "0"

    valor = Decimal(str(valor))

    valor = valor.quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    numero = f"{int(valor):,}"

    return numero.replace(",", ".")