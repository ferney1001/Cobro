from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from clientes.models import Cliente
from .forms import PrestamoForm, PrestamoEditarForm, PagoForm
from .models import Prestamo, Cuota


@login_required
def crear_prestamo(request):

    if request.method == 'POST':

        formulario = PrestamoForm(request.POST)

        if formulario.is_valid():

            formulario.save()

            return redirect('crear_prestamo')

    else:

        formulario = PrestamoForm()

    return render(
        request,
        'prestamos/crear_prestamo.html',
        {
            'formulario': formulario
        }
    )


@login_required
def lista_prestamos(request):

    texto = request.GET.get('q', '').strip()

    prestamos = Prestamo.objects.select_related(
        'cliente'
    ).prefetch_related(
        'cuotas__pagos'
    )

    if texto:

        palabras = texto.split()

        consulta = Q()

        for palabra in palabras:

            consulta &= (
                Q(
                    cliente__nombre__icontains=palabra
                ) |
                Q(
                    cliente__apellido__icontains=palabra
                )
            )

        prestamos = prestamos.filter(consulta)


    prestamos_activos = []


    for prestamo in prestamos:

        total_prestamo = 0
        total_pagado = 0

        for cuota in prestamo.cuotas.all():

            total_prestamo += cuota.valor

            for pago in cuota.pagos.all():

                total_pagado += pago.monto


        pendiente = total_prestamo - total_pagado


        if pendiente > 0:

            if total_pagado > 0:

                estado = 'abono'

            else:

                estado = 'pendiente'


            prestamo.total_prestamo = total_prestamo
            prestamo.total_pagado = total_pagado
            prestamo.pendiente = pendiente
            prestamo.estado_calculado = estado

            prestamos_activos.append(prestamo)


    if not texto:

        prestamos_activos = prestamos_activos[:10]


    return render(
        request,
        'prestamos/lista_prestamos.html',
        {
            'prestamos': prestamos_activos,
            'busqueda': texto
        }
    )


@login_required
def detalle_prestamo(request, prestamo_id):

    prestamo = get_object_or_404(
        Prestamo.objects.select_related('cliente'),
        id=prestamo_id
    )

    cuotas = (
        Cuota.objects
        .filter(prestamo=prestamo)
        .prefetch_related('pagos')
        .order_by('numero')
    )

    tiene_pagos = False

    total_cuotas = 0
    total_pagado = 0

    for cuota in cuotas:

        abonado = sum(
            pago.monto
            for pago in cuota.pagos.all()
        )

        if abonado > 0:
            tiene_pagos = True

        pendiente = cuota.valor - abonado

        if abonado <= 0:

            estado = 'pendiente'

        elif pendiente > 0:

            estado = 'abono'

        else:

            estado = 'pagada'

        cuota.abonado = abonado

        cuota.pendiente = max(
            pendiente,
            0
        )

        cuota.estado_calculado = estado

        total_cuotas += cuota.valor

        total_pagado += abonado


    # =========================================
    # RESUMEN DEL PRÉSTAMO
    # =========================================

    if prestamo.tipo_prestamo == 'solo_intereses':

        interes = total_cuotas

        total = total_cuotas

    else:

        total = total_cuotas

        interes = (
            total_cuotas -
            prestamo.monto
        )


    pendiente_total = (
        total -
        total_pagado
    )


    return render(
        request,
        'prestamos/detalle_prestamo.html',
        {
            'prestamo': prestamo,
            'cuotas': cuotas,
            'interes': interes,
            'total': total,
            'total_pagado': total_pagado,
            'pendiente_total': max(
                pendiente_total,
                0
            ),
            'tiene_pagos': tiene_pagos,
        }
    )

@login_required
def editar_prestamo(request, prestamo_id):

    prestamo = get_object_or_404(
        Prestamo.objects.select_related('cliente'),
        id=prestamo_id
    )


    # =========================================
    # COMPROBAR SI EXISTEN PAGOS
    # =========================================

    tiene_pagos = Cuota.objects.filter(
        prestamo=prestamo,
        pagos__isnull=False
    ).exists()


    if tiene_pagos or not prestamo.activo:

        return render(
            request,
            'prestamos/editar_prestamo_bloqueado.html',
            {
                'prestamo': prestamo,
                'tiene_pagos': tiene_pagos,
            }
        )


    # =========================================
    # EDITAR
    # =========================================

    if request.method == 'POST':

        formulario = PrestamoEditarForm(
            request.POST,
            instance=prestamo
        )


        if formulario.is_valid():

            with transaction.atomic():

                prestamo = formulario.save(
                    commit=False
                )

                prestamo.save()


                # =================================
                # COMO NO HAY PAGOS,
                # PODEMOS REGENERAR LAS CUOTAS
                # =================================

                prestamo.cuotas.all().delete()

                prestamo.crear_cuotas()


            return redirect(
                'detalle_prestamo',
                prestamo_id=prestamo.id
            )


    else:

        formulario = PrestamoEditarForm(
            instance=prestamo
        )


    return render(
        request,
        'prestamos/editar_prestamo.html',
        {
            'prestamo': prestamo,
            'formulario': formulario,
        }
    )


@login_required
def buscar_clientes(request):

    texto = request.GET.get(
        'q',
        ''
    ).strip()


    if not texto:

        return JsonResponse(
            [],
            safe=False
        )


    palabras = texto.split()

    consulta = Q()


    for palabra in palabras:

        consulta &= (
            Q(
                nombre__icontains=palabra
            ) |
            Q(
                apellido__icontains=palabra
            )
        )


    clientes = Cliente.objects.filter(
        consulta
    ).order_by(
        'nombre',
        'apellido'
    )


    resultados = [
        {
            'id': cliente.id,
            'nombre': (
                f'{cliente.nombre} '
                f'{cliente.apellido}'
            )
        }

        for cliente in clientes
    ]


    return JsonResponse(
        resultados,
        safe=False
    )


@login_required
def registrar_pago(request, cuota_id):

    cuota = get_object_or_404(
        Cuota.objects.select_related(
            'prestamo',
            'prestamo__cliente'
        ),
        id=cuota_id
    )


    abonado = cuota.pagos.aggregate(
        total=Sum('monto')
    )['total'] or 0


    pendiente = cuota.valor - abonado


    # =========================================
    # COMPROBAR SI LA CUOTA YA ESTÁ PAGADA
    # =========================================

    if pendiente <= 0:

        cuota.estado = 'pagada'
        cuota.save()

        return render(
            request,
            'prestamos/pago_bloqueado.html',
            {
                'cuota': cuota,
            }
        )


    # =========================================
    # REGISTRAR PAGO
    # =========================================

    if request.method == 'POST':

        formulario = PagoForm(
            request.POST
        )


        if formulario.is_valid():

            monto = formulario.cleaned_data[
                'monto'
            ]


            if monto > pendiente:

                formulario.add_error(
                    'monto',
                    (
                        'El pago no puede ser mayor '
                        f'al pendiente de ${pendiente:.0f}.'
                    )
                )


            else:

                pago = formulario.save(
                    commit=False
                )

                pago.cuota = cuota

                pago.save()


                nuevo_abonado = (
                    abonado + monto
                )


                if nuevo_abonado >= cuota.valor:

                    cuota.estado = 'pagada'

                    cuota.save()


                prestamo = cuota.prestamo


                todas_pagadas = not prestamo.cuotas.filter(
                    estado='pendiente'
                ).exists()


                if todas_pagadas:

                    prestamo.activo = False

                    prestamo.save()


                return redirect(
                    'dashboard'
                )


    else:

        formulario = PagoForm()


    return render(
        request,
        'prestamos/registrar_pago.html',
        {
            'cuota': cuota,
            'formulario': formulario,
            'abonado': abonado,
            'pendiente': pendiente,
        }
    )