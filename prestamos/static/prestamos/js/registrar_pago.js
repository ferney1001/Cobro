
document.addEventListener('DOMContentLoaded', function () {

    const formulario = document.getElementById('formulario-pago');

    const botonPagoCompleto =
        document.getElementById('boton-pago-completo');

    const botonHoy =
        document.getElementById('boton-hoy');

    const campoMonto =
        document.querySelector('input[name="monto"]');

    const campoFechaHora =
        document.querySelector('input[name="fecha_hora"]');

    const checkboxIncluir =
        document.getElementById('incluir-siguientes');

    const contenedorCuotas =
        document.getElementById('contenedor-cuotas-siguientes');

    const casillasCuotas = document.querySelectorAll(
        '.checkbox-cuota-siguiente'
    );


    /*
    =========================================
    MOSTRAR U OCULTAR CUOTAS FUTURAS
    =========================================
    */

    console.log('JavaScript de registrar pago cargado.');

    console.log('Casilla de cuotas:', checkboxIncluir);
    console.log('Contenedor de cuotas:', contenedorCuotas);
    console.log('Cantidad de cuotas:', casillasCuotas.length);

    if (checkboxIncluir && contenedorCuotas) {

        function actualizarCuotas() {

            const activado = checkboxIncluir.checked;

            contenedorCuotas.hidden = !activado;

            checkboxIncluir.setAttribute(
                'aria-expanded',
                String(activado)
            );

            casillasCuotas.forEach(function (casilla) {

                casilla.disabled = !activado;

                if (!activado) {
                    casilla.checked = false;
                }

            });

            console.log(
                'Cuotas futuras visibles:',
                activado
            );

        }

        checkboxIncluir.addEventListener(
            'change',
            actualizarCuotas
        );

        actualizarCuotas();

    } else {

        console.error(
            'No se encontró la casilla o el contenedor de cuotas futuras.'
        );

    }


    /*
    =========================================
    FORMATO DEL MONTO
    =========================================
    */

    function obtenerNumero(valor) {

        return valor.replace(/\D/g, '');

    }


    function formatearMonto(valor) {

        const numero = obtenerNumero(valor);

        if (numero === '') {
            return '';
        }

        return parseInt(numero, 10).toLocaleString('es-CO');

    }


    if (campoMonto) {

        campoMonto.addEventListener('input', function () {

            campoMonto.value = formatearMonto(campoMonto.value);

        });

    }


    /*
    =========================================
    PAGAR CUOTA COMPLETA
    =========================================
    */

    if (botonPagoCompleto && campoMonto) {

        botonPagoCompleto.addEventListener('click', function () {

            const pendiente = botonPagoCompleto.dataset.pendiente;

            if (pendiente) {
                campoMonto.value = formatearMonto(pendiente);
            }

        });

    }


    /*
    =========================================
    FECHA Y HORA ACTUAL
    =========================================
    */

    if (botonHoy && campoFechaHora) {

        botonHoy.addEventListener('click', function () {

            const ahora = new Date();

            const año = ahora.getFullYear();

            const mes = String(
                ahora.getMonth() + 1
            ).padStart(2, '0');

            const dia = String(
                ahora.getDate()
            ).padStart(2, '0');

            const hora = String(
                ahora.getHours()
            ).padStart(2, '0');

            const minutos = String(
                ahora.getMinutes()
            ).padStart(2, '0');

            campoFechaHora.value =
                `${año}-${mes}-${dia}T${hora}:${minutos}`;

        });

    }


    /*
    =========================================
    FECHA VACÍA AL ENTRAR
    =========================================
    */

    if (formulario && campoFechaHora) {

        const tieneErrores =
            formulario.dataset.tieneErrores === 'true';

        if (!tieneErrores) {
            campoFechaHora.value = '';
        }

    }


    /*
    =========================================
    LIMPIAR MONTO ANTES DE ENVIAR
    =========================================
    */

    if (formulario && campoMonto) {

        formulario.addEventListener('submit', function () {

            campoMonto.value = obtenerNumero(campoMonto.value);

        });

    }

});