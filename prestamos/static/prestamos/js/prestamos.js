const buscador = document.getElementById('buscar-cliente');

const resultados = document.getElementById('resultados-clientes');

const clienteSeleccionado = document.getElementById('id_cliente');


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

        });

});


const montoInput = document.getElementById('id_monto');

const interesInput = document.getElementById(
    'id_porcentaje_interes'
);

const cuotasInput = document.getElementById(
    'id_numero_cuotas'
);


const resumen = document.getElementById(
    'resumen-prestamo'
);

const resumenInteres = document.getElementById(
    'resumen-interes'
);

const resumenTotal = document.getElementById(
    'resumen-total'
);

const resumenCuota = document.getElementById(
    'resumen-cuota'
);


function actualizarResumen() {

    const monto = parseFloat(montoInput.value);

    const porcentaje = parseFloat(interesInput.value);

    const cuotas = parseInt(cuotasInput.value);


    if (
        !monto ||
        monto <= 0 ||
        porcentaje < 0
    ) {

        resumen.style.display = 'none';

        return;
    }


    const interes = monto * porcentaje / 100;

    const total = monto + interes;


    resumenInteres.textContent = interes.toLocaleString(
        'es-CO',
        {
            style: 'currency',
            currency: 'COP'
        }
    );


    resumenTotal.textContent = total.toLocaleString(
        'es-CO',
        {
            style: 'currency',
            currency: 'COP'
        }
    );


    if (cuotas && cuotas > 0) {

        const valorCuota = total / cuotas;

        resumenCuota.textContent = valorCuota.toLocaleString(
            'es-CO',
            {
                style: 'currency',
                currency: 'COP'
            }
        );

    } else {

        resumenCuota.textContent = '$0,00';

    }


    resumen.style.display = 'block';
}


montoInput.addEventListener(
    'input',
    actualizarResumen
);


interesInput.addEventListener(
    'input',
    actualizarResumen
);


cuotasInput.addEventListener(
    'input',
    actualizarResumen
);


actualizarResumen();