from django.contrib.auth.decorators import login_required
from django.db.models import Q ,Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from clientes.models import Cliente
from .forms import PrestamoForm, PagoForm
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
        {'formulario': formulario}
    )

@login_required
def lista_prestamos(request):

    texto = request.GET.get('q', '').strip()

    if texto:

        palabras = texto.split()

        consulta = Q()

        for palabra in palabras:
            consulta &= (
                Q(cliente__nombre__icontains=palabra) |
                Q(cliente__apellido__icontains=palabra)
            )

        prestamos = Prestamo.objects.select_related(
            'cliente'
        ).filter(
            consulta
        ).order_by(
            '-fecha_prestamo'
        )

    else:

        prestamos = Prestamo.objects.select_related(
            'cliente'
        ).order_by(
            '-fecha_prestamo'
        )[:10]

    return render(
        request,
        'prestamos/lista_prestamos.html',
        {
            'prestamos': prestamos,
            'busqueda': texto
        }
    )

@login_required
def detalle_prestamo(request, prestamo_id):

    prestamo = get_object_or_404(
        Prestamo.objects.select_related('cliente'),
        id=prestamo_id
    )

    cuotas = Cuota.objects.filter(
        prestamo=prestamo
    ).order_by(
        'numero'
    )

    interes = (
        prestamo.monto *
        prestamo.porcentaje_interes /
        100
    )

    total = prestamo.monto + interes

    return render(
        request,
        'prestamos/detalle_prestamo.html',
        {
            'prestamo': prestamo,
            'cuotas': cuotas,
            'interes': interes,
            'total': total
        }
    )
    
@login_required
def buscar_clientes(request):

    texto = request.GET.get('q', '').strip()

    if not texto:
        return JsonResponse([], safe=False)

    palabras = texto.split()

    consulta = Q()

    for palabra in palabras:
        consulta &= (
            Q(nombre__icontains=palabra) |
            Q(apellido__icontains=palabra)
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
            'nombre': f'{cliente.nombre} {cliente.apellido}'
        }
        for cliente in clientes
    ]

    return JsonResponse(resultados, safe=False)

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

    if request.method == 'POST':

        formulario = PagoForm(request.POST)

        if formulario.is_valid():

            monto = formulario.cleaned_data['monto']

            if monto <= 0:

                formulario.add_error(
                    'monto',
                    'El monto debe ser mayor que cero.'
                )

            elif monto > pendiente:

                formulario.add_error(
                    'monto',
                    f'El pago no puede ser mayor al pendiente de ${pendiente:.2f}.'
                )

            else:

                pago = formulario.save(commit=False)

                pago.cuota = cuota

                pago.save()

                nuevo_abonado = abonado + monto

                if nuevo_abonado >= cuota.valor:
                    cuota.estado = 'pagada'
                    cuota.save()

                return redirect('inicio')

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