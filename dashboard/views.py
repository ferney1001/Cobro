from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from prestamos.models import Cuota


@login_required
def inicio(request):

    hoy = __import__('django.utils.timezone').utils.timezone.localdate()

    cuotas = Cuota.objects.select_related(
        'prestamo',
        'prestamo__cliente'
    ).prefetch_related(
        'pagos'
    ).order_by(
        'fecha_cobro',
        'prestamo__cliente__nombre',
        'prestamo__cliente__apellido',
        'numero'
    )

    cobros_hoy = []
    atrasados = []

    for cuota in cuotas:

        abonado = cuota.pagos.aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')

        pendiente = cuota.valor - abonado

        if pendiente <= Decimal('0.00'):
            continue

        datos = {
            'cuota': cuota,
            'abonado': abonado,
            'pendiente': pendiente,
        }

        if cuota.fecha_cobro == hoy:
            cobros_hoy.append(datos)

        elif cuota.fecha_cobro < hoy:
            atrasados.append(datos)

    return render(
        request,
        'dashboard/inicio.html',
        {
            'cobros_hoy': cobros_hoy,
            'atrasados': atrasados,
        }
    )