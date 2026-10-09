from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from .forms import PrestamoForm, PrestamoEditarForm, PagoForm
from .models import Prestamo, Cuota, Pago


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

    texto = request.GET.get(
        'q',
        ''
    ).strip()

    estado = request.GET.get(
        'estado',
        'por_pagar'
    )

    if estado not in ['por_pagar', 'pagados']:
        estado = 'por_pagar'

    prestamos = (
        Prestamo.objects
        .select_related('cliente')
        .prefetch_related('cuotas__pagos')
    )

    # Buscar cliente dentro de la sección seleccionada
    if texto:
        palabras = texto.split()
        consulta = Q()

        for palabra in palabras:
            consulta &= (
                Q(cliente__nombre__icontains=palabra)
                |
                Q(cliente__apellido__icontains=palabra)
            )

        prestamos = prestamos.filter(consulta)

    prestamos_resultado = []

    for prestamo in prestamos:

        total_prestamo = 0
        total_pagado = 0

        for cuota in prestamo.cuotas.all():

            total_prestamo += cuota.valor

            for pago in cuota.pagos.all():
                total_pagado += pago.monto

        pendiente = total_prestamo - total_pagado

        if pendiente <= 0:
            estado_calculado = 'pagado'

        elif total_pagado > 0:
            estado_calculado = 'abono'

        else:
            estado_calculado = 'pendiente'

        # PRÉSTAMOS PAGADOS
        if estado == 'pagados':

            if estado_calculado != 'pagado':
                continue

        # PRÉSTAMOS POR PAGAR
        else:

            if estado_calculado == 'pagado':
                continue

        prestamo.total_prestamo = total_prestamo
        prestamo.total_pagado = total_pagado
        prestamo.pendiente = max(
            pendiente,
            0
        )
        prestamo.estado_calculado = estado_calculado

        prestamos_resultado.append(
            prestamo
        )

    # Sin búsqueda: máximo 10
    if not texto:
        prestamos_resultado = prestamos_resultado[:10]

    return render(
        request,
        'prestamos/lista_prestamos.html',
        {
            'prestamos': prestamos_resultado,
            'busqueda': texto,
            'estado': estado,
        }
    )


@login_required
def eliminar_prestamo(request, prestamo_id):

    prestamo = get_object_or_404(
        Prestamo.objects.select_related('cliente'),
        id=prestamo_id
    )

    # Recordar desde dónde se inició la eliminación.
    origen = request.GET.get(
        'origen',
        request.POST.get('origen', '')
    )

    cliente_id = prestamo.cliente_id

    # Calcular el saldo real del préstamo.
    cuotas = (
        Cuota.objects
        .filter(prestamo=prestamo)
        .prefetch_related('pagos')
    )

    total_cuotas = 0
    total_pagado = 0

    for cuota in cuotas:
        total_cuotas += cuota.valor

        for pago in cuota.pagos.all():
            total_pagado += pago.monto

    pendiente = total_cuotas - total_pagado

    # Solo se eliminan préstamos completamente pagados.
    if pendiente > 0:
        if origen == 'contabilidad_cliente':
            return redirect(
                f"{reverse('contabilidad_cliente')}?cliente={cliente_id}"
            )

        return redirect('lista_prestamos')

    # Mostrar la confirmación.
    if request.method == 'GET':
        return render(
            request,
            'prestamos/eliminar_prestamo.html',
            {
                'prestamo': prestamo,
                'origen': origen,
            }
        )

    # Eliminar únicamente mediante POST.
    if request.method == 'POST':
        prestamo.delete()

        if origen == 'contabilidad_cliente':
            return redirect(
                f"{reverse('contabilidad_cliente')}?cliente={cliente_id}"
            )

        return redirect(
            f"{reverse('lista_prestamos')}?estado=pagados"
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
            )
            |
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

    if pendiente <= 0:
        cuota.estado = 'pagada'
        cuota.save()

        return render(
            request,
            'prestamos/pago_bloqueado.html',
            {'cuota': cuota}
        )

    # Cargar las cuotas futuras del mismo préstamo.
    cuotas_siguientes = (
        Cuota.objects
        .filter(
            prestamo=cuota.prestamo,
            numero__gt=cuota.numero
        )
        .prefetch_related('pagos')
        .order_by('numero')
    )

    cuotas_disponibles = []

    for cuota_futura in cuotas_siguientes:
        abonado_futuro = sum(
            pago.monto
            for pago in cuota_futura.pagos.all()
        )

        pendiente_futuro = (
            cuota_futura.valor - abonado_futuro
        )

        if pendiente_futuro > 0:
            cuota_futura.abonado_calculado = abonado_futuro
            cuota_futura.pendiente_calculado = pendiente_futuro
            cuotas_disponibles.append(cuota_futura)

    if request.method == 'POST':

        formulario = PagoForm(request.POST)

        if formulario.is_valid():

            monto_recibido = formulario.cleaned_data['monto']

            incluir_siguientes = (
                request.POST.get('incluir_siguientes') == 'on'
            )

            ids_seleccionados = request.POST.getlist(
                'cuotas_siguientes'
            )

            # Sin adelantos, se conserva la validación habitual.
            if not incluir_siguientes and monto_recibido > pendiente:
                formulario.add_error(
                    'monto',
                    (
                        'El pago no puede superar el pendiente '
                        f'de ${pendiente:.0f}.'
                    )
                )

            else:

                cuotas_destino = [cuota]

                if incluir_siguientes and ids_seleccionados:

                    cuotas_validas = list(
                        Cuota.objects
                        .filter(
                            prestamo=cuota.prestamo,
                            numero__gt=cuota.numero,
                            id__in=ids_seleccionados
                        )
                        .prefetch_related('pagos')
                        .order_by('numero')
                    )

                    # Rechazar identificadores que no sean
                    # cuotas futuras de este préstamo.
                    ids_validos = {
                        str(c.id) for c in cuotas_validas
                    }

                    if (
                        len(ids_validos) != len(set(ids_seleccionados))
                    ):
                        formulario.add_error(
                            None,
                            'Hay cuotas seleccionadas que no son válidas.'
                        )

                    else:
                        cuotas_destino.extend(cuotas_validas)

                # Si el dinero supera la cuota actual,
                # debe existir al menos una cuota futura seleccionada.
                if (
                    incluir_siguientes
                    and monto_recibido > pendiente
                    and not ids_seleccionados
                ):
                    formulario.add_error(
                        None,
                        'Selecciona al menos una cuota futura para adelantar.'
                    )

                if not formulario.errors:

                    fecha_hora = formulario.cleaned_data['fecha_hora']
                    medio_pago = formulario.cleaned_data['medio_pago']

                    monto_restante = monto_recibido
                    total_aplicado = 0
                    cambio = 0
                    detalles_pagos = []

                    with transaction.atomic():

                        for cuota_destino in cuotas_destino:

                            if monto_restante <= 0:
                                break

                            abonado_destino = sum(
                                pago.monto
                                for pago in cuota_destino.pagos.all()
                            )

                            pendiente_destino = (
                                cuota_destino.valor - abonado_destino
                            )

                            if pendiente_destino <= 0:
                                cuota_destino.estado = 'pagada'
                                cuota_destino.save()
                                continue

                            monto_aplicado = min(
                                monto_restante,
                                pendiente_destino
                            )

                            if monto_aplicado <= 0:
                                continue

                            Pago.objects.create(
                                cuota=cuota_destino,
                                monto=monto_aplicado,
                                fecha_hora=fecha_hora,
                                medio_pago=medio_pago
                            )

                            monto_restante -= monto_aplicado
                            total_aplicado += monto_aplicado

                            detalles_pagos.append({
                                'cuota': cuota_destino,
                                'monto': monto_aplicado,
                            })

                            nuevo_abonado = (
                                abonado_destino + monto_aplicado
                            )

                            if nuevo_abonado >= cuota_destino.valor:
                                cuota_destino.estado = 'pagada'
                                cuota_destino.save()

                        # El sobrante es cambio, no un pago.
                        cambio = max(monto_restante, 0)

                        prestamo = cuota.prestamo

                        todas_pagadas = not prestamo.cuotas.filter(
                            estado='pendiente'
                        ).exists()

                        if todas_pagadas:
                            prestamo.activo = False
                            prestamo.save()

                    return render(
                        request,
                        'prestamos/resultado_pago.html',
                        {
                            'cuota': cuota,
                            'prestamo': cuota.prestamo,
                            'monto_recibido': monto_recibido,
                            'total_aplicado': total_aplicado,
                            'cambio': cambio,
                            'detalles_pagos': detalles_pagos,
                        }
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
            'cuotas_siguientes': cuotas_disponibles,
        }
    )

# ============================================================
# CONTABILIDAD DIARIA
# ============================================================

@login_required
def contabilidad(request):

    fecha = request.GET.get('fecha')

    if fecha:

        try:

            fecha_consulta = datetime.strptime(
                fecha,
                '%Y-%m-%d'
            ).date()

        except ValueError:

            fecha_consulta = timezone.localdate()

    else:

        fecha_consulta = timezone.localdate()

    pagos = (
        Pago.objects
        .filter(
            fecha_hora__date=fecha_consulta
        )
        .select_related(
            'cuota',
            'cuota__prestamo',
            'cuota__prestamo__cliente'
        )
        .order_by(
            'fecha_hora',
            'id'
        )
    )

    # ========================================================
    # Para saber si cada movimiento fue ABONO o PAGO COMPLETO
    # revisamos los pagos históricos de cada cuota.
    # ========================================================

    cuotas_ids = pagos.values_list(
        'cuota_id',
        flat=True
    )

    pagos_historicos = (
        Pago.objects
        .filter(
            cuota_id__in=cuotas_ids
        )
        .select_related(
            'cuota'
        )
        .order_by(
            'cuota_id',
            'fecha_hora',
            'id'
        )
    )

    acumulados = {}

    tipo_por_pago = {}

    for pago_historico in pagos_historicos:

        cuota_id = pago_historico.cuota_id

        if cuota_id not in acumulados:
            acumulados[cuota_id] = 0

        acumulados[cuota_id] += pago_historico.monto

        if acumulados[cuota_id] >= pago_historico.cuota.valor:

            tipo_por_pago[pago_historico.id] = 'completo'

        else:

            tipo_por_pago[pago_historico.id] = 'abono'

    # ========================================================
    # TOTALES DEL DÍA
    # ========================================================

    total_efectivo = 0
    total_nequi = 0

    pagos_resultado = []

    for pago in pagos:

        pago.tipo_pago = tipo_por_pago.get(
            pago.id,
            'abono'
        )

        if pago.medio_pago == 'efectivo':

            total_efectivo += pago.monto

        elif pago.medio_pago == 'nequi':

            total_nequi += pago.monto

        pagos_resultado.append(
            pago
        )

    total_recibido = (
        total_efectivo +
        total_nequi
    )

    return render(
        request,
        'prestamos/contabilidad.html',
        {
            'fecha_consulta': fecha_consulta,
            'pagos': pagos_resultado,
            'total_efectivo': total_efectivo,
            'total_nequi': total_nequi,
            'total_recibido': total_recibido,
        }
    )

# ============================================================
# CONTABILIDAD POR CLIENTE
# ============================================================

@login_required
def contabilidad_cliente(request):

    texto = request.GET.get(
        'q',
        ''
    ).strip()

    cliente_id = request.GET.get(
        'cliente'
    )

    prestamo_id = request.GET.get(
        'prestamo'
    )

    fecha_desde = request.GET.get(
        'desde'
    )

    fecha_hasta = request.GET.get(
        'hasta'
    )

    cliente_seleccionado = None
    prestamo_seleccionado = None

    prestamos_cliente = []

    clientes = Cliente.objects.none()

    # ========================================================
    # BUSCAR CLIENTES
    # ========================================================

    if texto:

        palabras = texto.split()

        consulta = Q()

        for palabra in palabras:

            consulta &= (
                Q(
                    nombre__icontains=palabra
                )
                |
                Q(
                    apellido__icontains=palabra
                )
            )

        clientes = (
            Cliente.objects
            .filter(consulta)
            .order_by(
                'nombre',
                'apellido'
            )
        )

    # ========================================================
    # SELECCIONAR CLIENTE
    # ========================================================

    if cliente_id:

        cliente_seleccionado = get_object_or_404(
            Cliente,
            id=cliente_id
        )

        prestamos_cliente = (
            Prestamo.objects
            .filter(
                cliente=cliente_seleccionado
            )
            .prefetch_related(
                'cuotas__pagos'
            )
            .order_by(
                '-fecha_prestamo',
                '-numero_prestamo'
            )
        )

    # ========================================================
    # SELECCIONAR PRÉSTAMO
    # ========================================================

    if prestamo_id:

        prestamo_seleccionado = get_object_or_404(
            Prestamo.objects
            .select_related('cliente')
            .prefetch_related(
                'cuotas__pagos'
            ),
            id=prestamo_id
        )

        cliente_seleccionado = (
            prestamo_seleccionado.cliente
        )

        prestamos_cliente = (
            Prestamo.objects
            .filter(
                cliente=cliente_seleccionado
            )
            .prefetch_related(
                'cuotas__pagos'
            )
            .order_by(
                '-fecha_prestamo',
                '-numero_prestamo'
            )
        )

        # ====================================================
        # RESUMEN COMPLETO DEL PRÉSTAMO
        # ====================================================

        total_planeado = 0
        total_recuperado = 0

        cuotas_pagadas = 0
        cuotas_abono = 0
        cuotas_pendientes = 0

        cuotas = prestamo_seleccionado.cuotas.all()

        for cuota in cuotas:

            total_planeado += cuota.valor

            abonado = sum(
                pago.monto
                for pago in cuota.pagos.all()
            )

            total_recuperado += abonado

            pendiente = cuota.valor - abonado

            if pendiente <= 0:

                cuotas_pagadas += 1

            elif abonado > 0:

                cuotas_abono += 1

            else:

                cuotas_pendientes += 1

        if prestamo_seleccionado.tipo_prestamo == 'solo_intereses':

            interes = total_planeado

        else:

            interes = (
                total_planeado -
                prestamo_seleccionado.monto
            )

        pendiente_total = (
            total_planeado -
            total_recuperado
        )

        if pendiente_total <= 0:

            estado_prestamo = 'pagado'

        elif total_recuperado > 0:

            estado_prestamo = 'abono'

        else:

            estado_prestamo = 'pendiente'

        prestamo_seleccionado.total_planeado = (
            total_planeado
        )

        prestamo_seleccionado.interes_calculado = (
            interes
        )

        prestamo_seleccionado.total_recuperado = (
            total_recuperado
        )

        prestamo_seleccionado.pendiente_calculado = max(
            pendiente_total,
            0
        )

        prestamo_seleccionado.cuotas_pagadas = (
            cuotas_pagadas
        )

        prestamo_seleccionado.cuotas_abono = (
            cuotas_abono
        )

        prestamo_seleccionado.cuotas_pendientes = (
            cuotas_pendientes
        )

        prestamo_seleccionado.estado_calculado = (
            estado_prestamo
        )

        # ====================================================
        # FECHA DESDE
        # Siempre es la fecha del préstamo.
        # ====================================================

        fecha_desde_obj = (
            prestamo_seleccionado.fecha_prestamo
        )

        # ====================================================
        # FECHA HASTA
        # Por defecto es hoy.
        # ====================================================

        fecha_hasta_obj = timezone.localdate()

        if fecha_hasta:

            try:

                fecha_hasta_obj = datetime.strptime(
                    fecha_hasta,
                    '%Y-%m-%d'
                ).date()

            except ValueError:

                fecha_hasta_obj = timezone.localdate()

        # ====================================================
        # Nunca permitimos que DESDE sea modificable.
        # Siempre usamos fecha del préstamo.
        # ====================================================

        if fecha_hasta_obj < fecha_desde_obj:

            fecha_hasta_obj = fecha_desde_obj

        # ====================================================
        # MOVIMIENTOS DEL PERÍODO
        # ====================================================

        pagos_todos = (
            Pago.objects
            .filter(
                cuota__prestamo=prestamo_seleccionado
            )
            .select_related(
                'cuota'
            )
            .order_by(
                'fecha_hora',
                'id'
            )
        )

        acumulados = {}

        tipo_por_pago = {}

        for pago_historico in pagos_todos:

            cuota_id = pago_historico.cuota_id

            if cuota_id not in acumulados:

                acumulados[cuota_id] = 0

            acumulados[cuota_id] += (
                pago_historico.monto
            )

            if (
                acumulados[cuota_id]
                >= pago_historico.cuota.valor
            ):

                tipo_por_pago[
                    pago_historico.id
                ] = 'completo'

            else:

                tipo_por_pago[
                    pago_historico.id
                ] = 'abono'

        # ====================================================
        # Ahora sí filtramos los movimientos por el período.
        # ====================================================

        pagos_periodo = (
            pagos_todos
            .filter(
                fecha_hora__date__gte=fecha_desde_obj,
                fecha_hora__date__lte=fecha_hasta_obj
            )
        )

        total_efectivo_periodo = 0
        total_nequi_periodo = 0

        pagos_resultado = []

        for pago in pagos_periodo:

            pago.tipo_pago_calculado = (
                tipo_por_pago.get(
                    pago.id,
                    'abono'
                )
            )

            if pago.medio_pago == 'efectivo':

                total_efectivo_periodo += (
                    pago.monto
                )

            elif pago.medio_pago == 'nequi':

                total_nequi_periodo += (
                    pago.monto
                )

            pagos_resultado.append(
                pago
            )

        total_recogido_periodo = (
            total_efectivo_periodo +
            total_nequi_periodo
        )

    else:

        fecha_desde_obj = None
        fecha_hasta_obj = None

        pagos_resultado = []

        total_efectivo_periodo = 0
        total_nequi_periodo = 0
        total_recogido_periodo = 0

    return render(
        request,
        'prestamos/contabilidad_cliente.html',
        {
            'busqueda': texto,
            'clientes': clientes,

            'cliente_seleccionado':
                cliente_seleccionado,

            'prestamos_cliente':
                prestamos_cliente,

            'prestamo_seleccionado':
                prestamo_seleccionado,

            'fecha_desde':
                fecha_desde_obj,

            'fecha_hasta':
                fecha_hasta_obj,

            'pagos':
                pagos_resultado,

            'total_efectivo_periodo':
                total_efectivo_periodo,

            'total_nequi_periodo':
                total_nequi_periodo,

            'total_recogido_periodo':
                total_recogido_periodo,
        }
    )