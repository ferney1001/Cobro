from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.lista_prestamos,
        name='lista_prestamos'
    ),

    path(
        'nuevo/',
        views.crear_prestamo,
        name='crear_prestamo'
    ),

    path(
        'editar/<int:prestamo_id>/',
        views.editar_prestamo,
        name='editar_prestamo'
    ),

    path(
        'buscar-clientes/',
        views.buscar_clientes,
        name='buscar_clientes'
    ),

    path(
        'eliminar/<int:prestamo_id>/',
        views.eliminar_prestamo,
        name='eliminar_prestamo'
    ),

    path(
        '<int:prestamo_id>/',
        views.detalle_prestamo,
        name='detalle_prestamo'
    ),

    path(
        'pago/<int:cuota_id>/',
        views.registrar_pago,
        name='registrar_pago'
    ),

    path(
        'contabilidad/',
        views.contabilidad,
        name='contabilidad'
    ),

    path(
        'contabilidad/cliente/',
        views.contabilidad_cliente,
        name='contabilidad_cliente'
    ),

]