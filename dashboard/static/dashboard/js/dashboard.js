const secciones = document.querySelectorAll('.seccion');


secciones.forEach(function(seccion) {

    const botonesFiltro =
        seccion.querySelectorAll('.filtro');

    const buscador =
        seccion.querySelector('.buscador');

    const tarjetas =
        seccion.querySelectorAll('.tarjeta-cobro');


    let filtroActual = 'todos';


    function aplicarFiltros() {

        const texto =
            buscador.value
                .trim()
                .toLowerCase();


        tarjetas.forEach(function(tarjeta) {

            const estado =
                tarjeta.dataset.estado;

            const cliente =
                tarjeta.dataset.cliente
                    .toLowerCase();


            const coincideEstado =
                filtroActual === 'todos' ||
                estado === filtroActual;


            const coincideBusqueda =
                texto === '' ||
                cliente.includes(texto);


            if (
                coincideEstado &&
                coincideBusqueda
            ) {

                tarjeta.style.display = '';

            } else {

                tarjeta.style.display = 'none';

            }

        });

    }


    botonesFiltro.forEach(function(boton) {

        boton.addEventListener(
            'click',
            function() {

                filtroActual =
                    boton.dataset.filtro;


                botonesFiltro.forEach(
                    function(otroBoton) {

                        otroBoton.classList.remove(
                            'activo'
                        );

                    }
                );


                boton.classList.add(
                    'activo'
                );


                aplicarFiltros();

            }
        );

    });


    buscador.addEventListener(
        'input',
        function() {

            aplicarFiltros();

        }
    );


});