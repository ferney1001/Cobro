from django.shortcuts import get_object_or_404, render, redirect
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.decorators import login_required


@login_required
def lista_clientes(request):
    clientes = Cliente.objects.filter(
        activo=True
    )

    return render(
        request,
        'clientes/lista_clientes.html',
        {
            'clientes': clientes
        }
    )

@login_required
def crear_cliente(request):

    if request.method == 'POST':

        formulario = ClienteForm(request.POST)

        if formulario.is_valid():

            formulario.save()

            return redirect('lista_clientes')

    else:

        formulario = ClienteForm()

    return render(
        request,
        'clientes/crear_cliente.html',
        {
            'formulario': formulario
        }
    )


@login_required
def editar_cliente(request, cliente_id):

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id
    )

    if request.method == 'POST':

        formulario = ClienteForm(
            request.POST,
            instance=cliente
        )

        if formulario.is_valid():

            formulario.save()

            return redirect('lista_clientes')

    else:

        formulario = ClienteForm(
            instance=cliente
        )

    return render(
        request,
        'clientes/editar_cliente.html',
        {
            'formulario': formulario,
            'cliente': cliente
        }
    )

@login_required
def desactivar_cliente(request, cliente_id):

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        activo=True
    )

    if request.method == 'POST':

        cliente.activo = False
        cliente.save()

        return redirect('lista_clientes')

    return render(
        request,
        'clientes/desactivar_cliente.html',
        {
            'cliente': cliente
        }
    )
@login_required
def lista_clientes_inactivos(request):

    clientes = Cliente.objects.filter(
        activo=False
    )

    return render(
        request,
        'clientes/lista_clientes_inactivos.html',
        {
            'clientes': clientes
        }
    )

@login_required
def reactivar_cliente(request, cliente_id):

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        activo=False
    )

    if request.method == 'POST':

        cliente.activo = True
        cliente.save()

        return redirect('lista_clientes_inactivos')

    return redirect('lista_clientes_inactivos')