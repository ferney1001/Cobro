
document.addEventListener("DOMContentLoaded", () => {

    const buscador = document.getElementById("buscar-cliente");
    const resultados = document.getElementById("resultados-clientes");

    // Formato de dinero colombiano
    function dinero(valor) {
        return new Intl.NumberFormat("es-CO", {
            style: "currency",
            currency: "COP",
            maximumFractionDigits: 0
        }).format(Number(valor) || 0);
    }

    // Crear elementos HTML de forma segura
    function crearElemento(etiqueta, clase, texto = "") {
        const elemento = document.createElement(etiqueta);

        if (clase) {
            elemento.className = clase;
        }

        elemento.textContent = texto;

        return elemento;
    }

    function mostrarMensaje(texto) {
        resultados.replaceChildren(
            crearElemento("p", "mensaje", texto)
        );
    }

    // =========================================
    // BUSCAR CLIENTES
    // =========================================

    let temporizadorBusqueda;

    buscador.addEventListener("input", () => {

        clearTimeout(temporizadorBusqueda);

        const texto = buscador.value.trim();

        if (texto.length < 2) {
            resultados.replaceChildren();
            return;
        }

        temporizadorBusqueda = setTimeout(() => {
            buscarClientes(texto);
        }, 300);

    });

    async function buscarClientes(texto) {

        mostrarMensaje("Buscando clientes...");

        try {

            const respuesta = await fetch(
                `/prestamos/buscar-clientes/?q=${encodeURIComponent(texto)}`
            );

            if (!respuesta.ok) {
                throw new Error("No se pudieron buscar los clientes.");
            }

            const datos = await respuesta.json();

            const clientes = Array.isArray(datos)
                ? datos
                : datos.clientes || [];

            resultados.replaceChildren();

            if (clientes.length === 0) {
                mostrarMensaje("No se encontraron clientes.");
                return;
            }

            clientes.forEach(cliente => {

                const tarjeta = crearElemento("div", "tarjeta");

                const informacion = crearElemento("div", "tarjeta-info");

                informacion.appendChild(
                    crearElemento("h3", "", cliente.nombre)
                );

                const boton = crearElemento(
                    "button",
                    "boton-seleccionar",
                    "Seleccionar"
                );

                boton.type = "button";

                boton.addEventListener("click", () => {
                    buscarPrestamos(cliente);
                });

                tarjeta.append(informacion, boton);

                resultados.appendChild(tarjeta);

            });

        } catch (error) {

            mostrarMensaje(error.message);

        }

    }

    // =========================================
    // BUSCAR PRÉSTAMOS DEL CLIENTE
    // =========================================

    async function buscarPrestamos(cliente) {

        mostrarMensaje("Cargando préstamos del cliente...");

        try {

            const respuesta = await fetch(
                `/prestamos/buscar-prestamos-cliente/?cliente_id=${encodeURIComponent(cliente.id)}`
            );

            if (!respuesta.ok) {
                throw new Error("No se pudieron cargar los préstamos.");
            }

            const prestamos = await respuesta.json();

            resultados.replaceChildren();

            // Botón para regresar a los resultados de clientes
            const botonRegresar = crearElemento(
                "button",
                "boton-volver",
                "← Volver a clientes"
            );

            botonRegresar.type = "button";

            botonRegresar.addEventListener("click", () => {
                buscarClientes(buscador.value.trim());
            });

            resultados.appendChild(botonRegresar);

            resultados.appendChild(
                crearElemento(
                    "h2",
                    "",
                    `Préstamos de ${cliente.nombre}`
                )
            );

            if (prestamos.length === 0) {

                resultados.appendChild(
                    crearElemento(
                        "p",
                        "mensaje",
                        "Este cliente no tiene préstamos pendientes."
                    )
                );

                return;
            }

            prestamos.forEach(prestamo => {

                const tarjeta = crearElemento("div", "tarjeta");

                const informacion = crearElemento(
                    "div",
                    "tarjeta-info"
                );

                informacion.appendChild(
                    crearElemento(
                        "h3",
                        "",
                        `Préstamo #${prestamo.numero}`
                    )
                );

                informacion.appendChild(
                    crearElemento(
                        "p",
                        "",
                        `Monto: ${dinero(prestamo.monto)}`
                    )
                );

                informacion.appendChild(
                    crearElemento(
                        "p",
                        "",
                        `Saldo pendiente: ${dinero(prestamo.saldo_pendiente)}`
                    )
                );

                const boton = crearElemento(
                    "button",
                    "boton-seleccionar",
                    "Seleccionar préstamo"
                );

                boton.type = "button";

                boton.addEventListener("click", () => {
                    buscarCuota(prestamo, cliente);
                });

                tarjeta.append(informacion, boton);

                resultados.appendChild(tarjeta);

            });

        } catch (error) {

            mostrarMensaje(error.message);

        }

    }

    // =========================================
    // BUSCAR PRIMERA CUOTA PENDIENTE
    // =========================================

    async function buscarCuota(prestamo, cliente) {

        mostrarMensaje("Buscando primera cuota pendiente...");

        try {

            const respuesta = await fetch(
                `/prestamos/buscar-cuotas-prestamo/?prestamo_id=${encodeURIComponent(prestamo.id)}`
            );

            if (!respuesta.ok) {
                throw new Error("No se pudo consultar la cuota.");
            }

            const cuotas = await respuesta.json();

            resultados.replaceChildren();

            const botonRegresar = crearElemento(
                "button",
                "boton-volver",
                "← Volver a préstamos"
            );

            botonRegresar.type = "button";

            botonRegresar.addEventListener("click", () => {
                buscarPrestamos(cliente);
            });

            resultados.appendChild(botonRegresar);

            resultados.appendChild(
                crearElemento(
                    "h2",
                    "",
                    `Préstamo #${prestamo.numero}`
                )
            );

            if (cuotas.length === 0) {

                resultados.appendChild(
                    crearElemento(
                        "p",
                        "mensaje",
                        "Este préstamo no tiene cuotas pendientes."
                    )
                );

                return;
            }

            // El endpoint devuelve la primera cuota pendiente.
            const cuota = cuotas[0];

            const tarjeta = crearElemento(
                "div",
                "seccion"
            );

            tarjeta.appendChild(
                crearElemento(
                    "h2",
                    "",
                    `Próxima cuota pendiente: #${cuota.numero}`
                )
            );

            tarjeta.appendChild(
                crearElemento(
                    "p",
                    "",
                    `Cliente: ${cliente.nombre}`
                )
            );

            tarjeta.appendChild(
                crearElemento(
                    "p",
                    "",
                    `Fecha de cobro: ${cuota.fecha_cobro}`
                )
            );

            const resumen = crearElemento(
                "div",
                "cuota-resumen"
            );

            const valor = crearElemento(
                "div",
                "dato-cuota"
            );

            valor.appendChild(
                crearElemento("span", "", "Valor de la cuota")
            );

            valor.appendChild(
                crearElemento("strong", "", dinero(cuota.valor))
            );

            const abonado = crearElemento(
                "div",
                "dato-cuota"
            );

            abonado.appendChild(
                crearElemento("span", "", "Abonado")
            );

            abonado.appendChild(
                crearElemento("strong", "", dinero(cuota.abonado))
            );

            const pendiente = crearElemento(
                "div",
                "dato-cuota dato-pendiente"
            );

            pendiente.appendChild(
                crearElemento("span", "", "Saldo pendiente")
            );

            pendiente.appendChild(
                crearElemento("strong", "", dinero(cuota.pendiente))
            );

            resumen.append(valor, abonado, pendiente);

            tarjeta.appendChild(resumen);

            // Ir al formulario original de registrar pago
            const botonPagar = crearElemento(
                "a",
                "boton-registrar",
                "Registrar pago"
            );

            botonPagar.href = `/prestamos/pago/${cuota.id}/`;

            tarjeta.appendChild(botonPagar);

            resultados.appendChild(tarjeta);

        } catch (error) {

            mostrarMensaje(error.message);

        }

    }

});
