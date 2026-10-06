from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.lista_clientes,
        name='lista_clientes'
    ),

    path(
        'nuevo/',
        views.crear_cliente,
        name='crear_cliente'
    ),

    path(
        'editar/<int:cliente_id>/',
        views.editar_cliente,
        name='editar_cliente'
    ),

    path(
        'desactivar/<int:cliente_id>/',
        views.desactivar_cliente,
        name='desactivar_cliente'
    ),
    path(
        'inactivos/',
        views.lista_clientes_inactivos,
        name='lista_clientes_inactivos'
    ),
    path(
        'reactivar/<int:cliente_id>/',
        views.reactivar_cliente,
        name='reactivar_cliente'
    ),

]