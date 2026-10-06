from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from prestamos.models import Cuota


@login_required
def dashboard(request):

    hoy = timezone.localdate()

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

        # Determinar el estado de la cuota
        if pendiente <= Decimal('0.00'):
            estado = 'pagado'

        elif abonado > Decimal('0.00'):
            estado = 'abono'

        else:
            estado = 'pendiente'

        datos = {
            'cuota': cuota,
            'abonado': abonado,
            'pendiente': max(pendiente, Decimal('0.00')),
            'estado': estado,
        }

        # COBROS DE HOY
        if cuota.fecha_cobro == hoy:
            cobros_hoy.append(datos)

        # ATRASADOS
        elif cuota.fecha_cobro < hoy:

            # Solo mostramos cuotas que todavía tienen
            # dinero pendiente.
            if pendiente > Decimal('0.00'):
                atrasados.append(datos)

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'cobros_hoy': cobros_hoy,
            'atrasados': atrasados,
        }
    )