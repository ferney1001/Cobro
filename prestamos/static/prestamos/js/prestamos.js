
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

                    const elemento = document.createElement('button');

                    elemento.type = 'button';
                    elemento.className = 'resultado-cliente';
                    elemento.textContent = cliente.nombre;

                    elemento.addEventListener('click', function () {

                        buscador.value = cliente.nombre;
                        clienteSeleccionado.value = cliente.id;
                        resultados.innerHTML = '';

                    });

                    resultados.appendChild(elemento);

                });

            })
            .catch(error => {
                console.error('Error al buscar clientes:', error);
            });

    });

}


/*
    =========================================
    CAMPOS DEL PRÉSTAMO
    =========================================
*/

const montoInput = document.getElementById('id_monto');

const interesInput = document.getElementById(
    'id_porcentaje_interes'
);

const cuotasInput = document.getElementById(
    'id_numero_cuotas'
);

const plazoInput = document.getElementById(
    'id_plazo_meses'
);

const tipoPrestamoInput = document.getElementById(
    'id_tipo_prestamo'
);


/*
    =========================================
    FORMULARIO
    =========================================
*/

const formularioPrestamo = montoInput
    ? montoInput.closest('form')
    : null;


/*
    =========================================
    RESUMEN
    =========================================
*/

const resumen = document.getElementById('resumen-prestamo');

const resumenInteres = document.getElementById(
    'resumen-interes'
);

const resumenTotal = document.getElementById(
    'resumen-total'
);

const resumenCuota = document.getElementById(
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
*/

function obtenerMontoNumerico() {

    if (!montoInput) {
        return NaN;
    }

    const valorLimpio = montoInput.value.replace(/\D/g, '');

    if (valorLimpio === '') {
        return NaN;
    }

    return parseInt(valorLimpio, 10);

}


/*
    =========================================
    FORMATEAR MONTO VISUALMENTE
    =========================================
*/

function formatearMonto() {

    if (!montoInput) {
        return;
    }

    const valorLimpio = montoInput.value.replace(/\D/g, '');

    if (valorLimpio === '') {
        montoInput.value = '';
        return;
    }

    const valor = parseInt(valorLimpio, 10);

    montoInput.value = valor.toLocaleString('es-CO');

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
        !plazoInput ||
        !resumen ||
        !resumenInteres ||
        !resumenTotal ||
        !resumenCuota
    ) {
        return;
    }

    const monto = obtenerMontoNumerico();

    const porcentaje = parseFloat(interesInput.value);

    const cuotas = parseInt(cuotasInput.value, 10);

    const plazoMeses = parseInt(plazoInput.value, 10);


    /*
        Validar que los datos estén completos.
    */

    if (
        !Number.isFinite(monto) ||
        monto <= 0 ||
        !Number.isFinite(porcentaje) ||
        porcentaje < 0 ||
        !Number.isFinite(cuotas) ||
        cuotas <= 0 ||
        !Number.isFinite(plazoMeses) ||
        plazoMeses <= 0
    ) {

        resumen.style.display = 'none';
        return;

    }


    /*
        =========================================
        CÁLCULO DEL INTERÉS
        =========================================

        Interés mensual =
        monto × porcentaje / 100

        Interés total =
        interés mensual × plazo en meses

        El número de cuotas NO determina
        cuánto interés se genera.
    */

    const interesMensual = monto * porcentaje / 100;

    const interesTotal = interesMensual * plazoMeses;

    let total = 0;


    /*
        =========================================
        CAPITAL + INTERESES
        =========================================
    */

    if (
        !tipoPrestamoInput ||
        tipoPrestamoInput.value === 'cuotas'
    ) {

        total = monto + interesTotal;

    }


    /*
        =========================================
        SOLO INTERESES
        =========================================

        El capital no se incluye en las cuotas.
        Solamente se distribuyen los intereses.
    */

    else if (tipoPrestamoInput.value === 'solo_intereses') {

        total = interesTotal;

    }


    /*
        =========================================
        VALOR POR CUOTA
        =========================================
    */

    const valorCuota = total / cuotas;

    const cuotaRedondeada = redondearA50(valorCuota);


    /*
        =========================================
        MOSTRAR RESULTADOS
        =========================================
    */

    resumenInteres.textContent = formatoPesos(interesTotal);

    resumenTotal.textContent = formatoPesos(total);

    resumenCuota.textContent = formatoPesos(cuotaRedondeada);

    resumen.style.display = 'block';

}


/*
    =========================================
    EVENTO DEL MONTO
    =========================================
*/

if (montoInput) {

    montoInput.addEventListener('input', function () {

        formatearMonto();

        actualizarResumen();

    });

}


/*
    =========================================
    EVENTO DEL PORCENTAJE
    =========================================
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
    EVENTO DEL PLAZO EN MESES
    =========================================
*/

if (plazoInput) {

    plazoInput.addEventListener(
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
*/

if (formularioPrestamo && montoInput) {

    formularioPrestamo.addEventListener('submit', function () {

        // Quitar separadores del monto antes de enviarlo.
        montoInput.value = montoInput.value.replace(/\D/g, '');

        // Evitar envíos duplicados.
        const botonCrear = document.getElementById('boton-crear');

        if (botonCrear) {
            botonCrear.disabled = true;
            botonCrear.textContent = 'Creando préstamo...';
        }

    });

}
/*
    =========================================
    NOTIFICACIONES TEMPORALES
    =========================================
*/

document.addEventListener('DOMContentLoaded', function () {

    const mensajes = document.querySelectorAll('.mensaje-exito');

    mensajes.forEach(function (mensaje) {

        setTimeout(function () {

            mensaje.classList.add('ocultando');

            setTimeout(function () {
                mensaje.remove();
            }, 500);

        }, 4000);

    });

});

/*
    =========================================
    EJECUTAR AL CARGAR
    =========================================
*/

actualizarResumen();
