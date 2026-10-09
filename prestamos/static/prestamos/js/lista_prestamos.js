const buscador = document.getElementById(
    'buscador-prestamos'
);


const filtros = document.querySelectorAll(
    '.filtro-prestamo'
);


filtros.forEach(function(filtro) {

    filtro.addEventListener(
        'click',
        function(event) {

            event.preventDefault();


            const texto = buscador.value.trim();

            const estado = filtro.dataset.estado;


            let url = '?estado=' + estado;


            /*
             * Si el buscador tiene texto,
             * lo conservamos al cambiar de filtro.
             *
             * Si está vacío, no agregamos q.
             * Así se muestran todos los préstamos.
             */

            if (texto !== '') {

                url += '&q=' + encodeURIComponent(
                    texto
                );

            }


            window.location.href = url;

        }
    );

});