const buscador = document.getElementById('buscar-cliente');

const resultados = document.getElementById('resultados-clientes');

const clienteSeleccionado = document.getElementById('id_cliente');


/*
    =========================================
    BUSCADOR DE CLIENTES
    =========================================
*/

if (buscador && resultados && clienteSeleccionado) {

    buscador.addEventListener('input', function () {

        const texto = buscador.value.trim();

        resultados.innerHTML = '';

        clienteSeleccionado.value = '';


        if (texto.length === 0) {
            return;
        }


        fetch(
            `/prestamos/buscar-clientes/?q=${encodeURIComponent(texto)}`
        )
            .then(response => response.json())

            .then(clientes => {

                if (clientes.length === 0) {

                    resultados.innerHTML =
                        '<div class="sin-resultados">' +
                        'No se encontraron clientes' +
                        '</div>';

                    return;
                }


                clientes.forEach(cliente => {

                    const elemento =
                        document.createElement('button');

                    elemento.type = 'button';

                    elemento.className =
                        'resultado-cliente';

                    elemento.textContent =
                        cliente.nombre;


                    elemento.addEventListener(
                        'click',
                        function () {

                            buscador.value =
                                cliente.nombre;

                            clienteSeleccionado.value =
                                cliente.id;

                            resultados.innerHTML = '';

                        }
                    );


                    resultados.appendChild(elemento);

                });

            });

    });

}


/*
    =========================================
    CAMPOS DEL PRÉSTAMO
    =========================================
*/

const montoInput =
    document.getElementById('id_monto');

const interesInput =
    document.getElementById(
        'id_porcentaje_interes'
    );

const cuotasInput =
    document.getElementById(
        'id_numero_cuotas'
    );

const tipoPrestamoInput =
    document.getElementById(
        'id_tipo_prestamo'
    );


/*
    =========================================
    FORMULARIO
    =========================================
*/

const formularioPrestamo =
    montoInput
        ? montoInput.closest('form')
        : null;


/*
    =========================================
    RESUMEN
    =========================================
*/

const resumen =
    document.getElementById(
        'resumen-prestamo'
    );

const resumenInteres =
    document.getElementById(
        'resumen-interes'
    );

const resumenTotal =
    document.getElementById(
        'resumen-total'
    );

const resumenCuota =
    document.getElementById(
        'resumen-cuota'
    );


/*
    =========================================
    REDONDEAR AL MÚLTIPLO DE $50 MÁS CERCANO
    =========================================
*/

function redondearA50(valor) {

    return Math.round(valor / 50) * 50;

}


/*
    =========================================
    FORMATO DE PESOS
    =========================================
*/

function formatoPesos(valor) {

    return valor.toLocaleString(
        'es-CO',
        {
            style: 'currency',
            currency: 'COP',
            maximumFractionDigits: 0
        }
    );

}


/*
    =========================================
    OBTENER MONTO NUMÉRICO
    =========================================

    Convierte:

    10.000.000

    en:

    10000000
*/

function obtenerMontoNumerico() {

    if (!montoInput) {
        return NaN;
    }

    const valorLimpio =
        montoInput.value.replace(/\D/g, '');

    if (valorLimpio === '') {
        return NaN;
    }

    return parseInt(
        valorLimpio,
        10
    );

}


/*
    =========================================
    FORMATEAR MONTO VISUALMENTE
    =========================================

    Ejemplo:

    10000000
          ↓
    10.000.000

    Esto es solamente visual.
*/

function formatearMonto() {

    if (!montoInput) {
        return;
    }


    const valorLimpio =
        montoInput.value.replace(/\D/g, '');


    if (valorLimpio === '') {

        montoInput.value = '';

        return;
    }


    const valor =
        parseInt(
            valorLimpio,
            10
        );


    montoInput.value =
        valor.toLocaleString('es-CO');

}


/*
    =========================================
    ACTUALIZAR RESUMEN
    =========================================
*/

function actualizarResumen() {

    if (
        !montoInput ||
        !interesInput ||
        !cuotasInput ||
        !resumen ||
        !resumenInteres ||
        !resumenTotal ||
        !resumenCuota
    ) {
        return;
    }


    const monto =
        obtenerMontoNumerico();

    const porcentaje =
        parseFloat(interesInput.value);

    const cuotas =
        parseInt(cuotasInput.value);


    /*
        Si los datos todavía no están completos,
        ocultamos el resumen.
    */

    if (
        isNaN(monto) ||
        monto <= 0 ||
        isNaN(porcentaje) ||
        porcentaje < 0
    ) {

        resumen.style.display = 'none';

        return;
    }


    /*
        INTERÉS DE UN PERÍODO

        Ejemplo:

        $10.000.000
        1.5%

        = $150.000
    */

    const interesPeriodo =
        monto * porcentaje / 100;


    let interesTotal = 0;

    let total = 0;

    let valorCuota = 0;


    /*
        =========================================
        CAPITAL + INTERESES EN CUOTAS
        =========================================

        Ejemplo:

        $10.000.000
        1.5%
        12 cuotas

        Interés por período:
        $150.000

        Interés total:
        $1.800.000

        Total:
        $11.800.000
    */

    if (
        !tipoPrestamoInput ||
        tipoPrestamoInput.value === 'cuotas'
    ) {

        if (
            !cuotas ||
            cuotas <= 0
        ) {

            resumen.style.display = 'none';

            return;
        }


        interesTotal =
            interesPeriodo * cuotas;


        total =
            monto + interesTotal;


        valorCuota =
            total / cuotas;

    }


    /*
        =========================================
        SOLO INTERESES
        =========================================

        Ejemplo:

        $10.000.000
        1.5%
        12 cuotas

        Cada cuota:
        $150.000

        Interés total:
        $1.800.000

        El capital NO se suma al total
        de estas cuotas.
    */

    else if (
        tipoPrestamoInput.value === 'solo_intereses'
    ) {

        if (
            !cuotas ||
            cuotas <= 0
        ) {

            resumen.style.display = 'none';

            return;
        }


        interesTotal =
            interesPeriodo * cuotas;


        total =
            interesTotal;


        valorCuota =
            interesPeriodo;

    }


    /*
        Redondeamos la cuota mostrada
        al múltiplo de $50 más cercano.
    */

    const cuotaRedondeada =
        redondearA50(valorCuota);


    resumenInteres.textContent =
        formatoPesos(interesTotal);


    resumenTotal.textContent =
        formatoPesos(total);


    resumenCuota.textContent =
        formatoPesos(cuotaRedondeada);


    resumen.style.display =
        'block';

}


/*
    =========================================
    EVENTO DEL MONTO
    =========================================
*/

if (montoInput) {

    montoInput.addEventListener(
        'input',
        function () {

            formatearMonto();

            actualizarResumen();

        }
    );

}


/*
    =========================================
    EVENTO DEL PORCENTAJE
    =========================================

    IMPORTANTE:

    El porcentaje NO se modifica.

    Puede seguir siendo:

    1.5
    2
    2.25
*/

if (interesInput) {

    interesInput.addEventListener(
        'input',
        actualizarResumen
    );

}


/*
    =========================================
    EVENTO DEL NÚMERO DE CUOTAS
    =========================================
*/

if (cuotasInput) {

    cuotasInput.addEventListener(
        'input',
        actualizarResumen
    );

}


/*
    =========================================
    EVENTO DEL TIPO DE PRÉSTAMO
    =========================================
*/

if (tipoPrestamoInput) {

    tipoPrestamoInput.addEventListener(
        'change',
        actualizarResumen
    );

}


/*
    =========================================
    ANTES DE GUARDAR
    =========================================

    El usuario puede ver:

    10.000.000

    pero Django recibe:

    10000000
*/

if (formularioPrestamo && montoInput) {

    formularioPrestamo.addEventListener(
        'submit',
        function () {

            montoInput.value =
                montoInput.value.replace(/\D/g, '');

        }
    );

}


/*
    =========================================
    EJECUTAR AL CARGAR
    =========================================
*/

actualizarResumen();