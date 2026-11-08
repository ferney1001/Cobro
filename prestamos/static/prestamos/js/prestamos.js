
/*
    =========================================
    BUSCADOR DE CLIENTES
    =========================================
*/

const buscador = document.getElementById('buscar-cliente');
const resultados = document.getElementById('resultados-clientes');
const clienteSeleccionado = document.getElementById('id_cliente');

if (buscador && resultados && clienteSeleccionado) {

    buscador.addEventListener('input', function () {

        const texto = buscador.value.trim();

        resultados.innerHTML = '';
        clienteSeleccionado.value = '';

        if (texto.length === 0) {
            return;
        }

        fetch(`/prestamos/buscar-clientes/?q=${encodeURIComponent(texto)}`)
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
    ELEMENTOS DEL FORMULARIO
    =========================================
*/

const montoInput = document.getElementById('id_monto');

const interesInput = document.getElementById(
    'id_porcentaje_interes'
);

const cuotasInput = document.getElementById(
    'id_numero_cuotas'
);

const plazoMesesInput = document.getElementById(
    'id_plazo_meses'
);

const plazoDiasInput = document.getElementById(
    'id_plazo_dias'
);

const frecuenciaInput = document.getElementById(
    'id_frecuencia'
);

const tipoPrestamoInput = document.getElementById(
    'id_tipo_prestamo'
);


/*
    =========================================
    CONTENEDORES DE LOS CAMPOS
    =========================================
*/

const campoPlazoMeses = document.getElementById(
    'campo-plazo-meses'
);

const campoPlazoDias = document.getElementById(
    'campo-plazo-dias'
);

const campoFrecuencia = document.getElementById(
    'campo-frecuencia'
);

const campoNumeroCuotas = document.getElementById(
    'campo-numero-cuotas'
);


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

const formularioPrestamo = montoInput
    ? montoInput.closest('form')
    : null;


/*
    =========================================
    FORMATO DE PESOS
    =========================================
*/

function formatoPesos(valor) {

    return valor.toLocaleString('es-CO', {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0
    });

}


/*
    =========================================
    REDONDEAR AL MÚLTIPLO DE $50
    =========================================
*/

function redondearA50(valor) {

    return Math.round(valor / 50) * 50;

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
    CAMBIAR CAMPOS SEGÚN EL TIPO
    =========================================
*/

function actualizarCampos() {

    if (!tipoPrestamoInput) {
        return;
    }

    const tipo = tipoPrestamoInput.value;

    // Capital + intereses
    if (tipo === 'cuotas') {

        campoPlazoMeses.style.display = '';
        campoPlazoDias.style.display = 'none';
        campoFrecuencia.style.display = '';
        campoNumeroCuotas.style.display = '';

        frecuenciaInput.disabled = false;

        plazoDiasInput.value = '';

    }

    // Solo intereses
    else if (tipo === 'solo_intereses') {

        campoPlazoMeses.style.display = '';
        campoPlazoDias.style.display = 'none';
        campoFrecuencia.style.display = 'none';
        campoNumeroCuotas.style.display = '';

        // Los préstamos de solo intereses son mensuales.
        frecuenciaInput.value = 'mensual';
        frecuenciaInput.disabled = false;

        plazoDiasInput.value = '';

    }

    // Factura
    else if (tipo === 'factura') {

        campoPlazoMeses.style.display = 'none';
        campoPlazoDias.style.display = '';
        campoFrecuencia.style.display = '';
        campoNumeroCuotas.style.display = '';

        frecuenciaInput.disabled = false;

        // Factura no utiliza plazo en meses.
        plazoMesesInput.value = '1';

    }

    actualizarResumen();

}


/*
    =========================================
    CALCULAR Y MOSTRAR EL RESUMEN
    =========================================
*/

function actualizarResumen() {

    if (
        !montoInput ||
        !interesInput ||
        !cuotasInput ||
        !resumen
    ) {
        return;
    }

    const tipo = tipoPrestamoInput
        ? tipoPrestamoInput.value
        : 'cuotas';

    const monto = obtenerMontoNumerico();

    const porcentaje = parseFloat(interesInput.value);

    const cuotas = parseInt(cuotasInput.value, 10);

    let interesTotal = 0;

    /*
        Validaciones generales
    */

    if (
        !Number.isFinite(monto) ||
        monto <= 0 ||
        !Number.isFinite(porcentaje) ||
        porcentaje < 0 ||
        !Number.isFinite(cuotas) ||
        cuotas <= 0
    ) {

        resumen.style.display = 'none';
        return;

    }


    /*
        =========================================
        FACTURA
        =========================================

        Interés = capital × porcentaje / 100 / 30 × días
    */

    if (tipo === 'factura') {

        const dias = parseInt(plazoDiasInput.value, 10);

        if (
            !Number.isFinite(dias) ||
            dias <= 0
        ) {

            resumen.style.display = 'none';
            return;

        }

        interesTotal = (
            monto *
            (porcentaje / 100) /
            30 *
            dias
        );

    }


    /*
        =========================================
        CAPITAL + INTERESES
        Y SOLO INTERESES
        =========================================
    */

    else {

        const plazoMeses = parseInt(
            plazoMesesInput.value,
            10
        );

        if (
            !Number.isFinite(plazoMeses) ||
            plazoMeses <= 0
        ) {

            resumen.style.display = 'none';
            return;

        }

        const interesMensual = monto * porcentaje / 100;

        interesTotal = interesMensual * plazoMeses;

    }


    /*
        =========================================
        CALCULAR TOTAL
        =========================================
    */

    let total = 0;

    if (tipo === 'solo_intereses') {

        total = interesTotal;

    } else {

        total = monto + interesTotal;

    }


    /*
        =========================================
        CALCULAR VALOR APROXIMADO POR CUOTA
        =========================================
    */

    const totalPesos = Math.round(total);

    const valorCuota = totalPesos / cuotas;

    const cuotaRedondeada = redondearA50(valorCuota);


    /*
        =========================================
        MOSTRAR RESULTADOS
        =========================================
    */

    resumenInteres.textContent = formatoPesos(
        Math.round(interesTotal)
    );

    resumenTotal.textContent = formatoPesos(
        totalPesos
    );

    resumenCuota.textContent = formatoPesos(
        cuotaRedondeada
    );

    resumen.style.display = 'block';

}


/*
    =========================================
    EVENTOS DE LOS CAMPOS
    =========================================
*/

if (montoInput) {

    montoInput.addEventListener('input', function () {

        formatearMonto();
        actualizarResumen();

    });

}

if (interesInput) {

    interesInput.addEventListener(
        'input',
        actualizarResumen
    );

}

if (cuotasInput) {

    cuotasInput.addEventListener(
        'input',
        actualizarResumen
    );

}

if (plazoMesesInput) {

    plazoMesesInput.addEventListener(
        'input',
        actualizarResumen
    );

}

if (plazoDiasInput) {

    plazoDiasInput.addEventListener(
        'input',
        actualizarResumen
    );

}

if (frecuenciaInput) {

    frecuenciaInput.addEventListener(
        'change',
        actualizarResumen
    );

}

if (tipoPrestamoInput) {

    tipoPrestamoInput.addEventListener(
        'change',
        actualizarCampos
    );

}


/*
    =========================================
    ANTES DE GUARDAR
    =========================================
*/

if (formularioPrestamo && montoInput) {

    formularioPrestamo.addEventListener('submit', function () {

        // Enviar el monto sin separadores.
        montoInput.value = montoInput.value.replace(/\D/g, '');

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
    INICIAR FORMULARIO
    =========================================
*/

actualizarCampos();
