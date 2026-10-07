# 💰 Cobro — Sistema de gestión de préstamos y cobros

Sistema web desarrollado con **Python y Django** para gestionar clientes, préstamos, cuotas y pagos de una persona dedicada al préstamo de dinero.

El proyecto fue desarrollado como una aplicación práctica para solucionar necesidades reales de administración y seguimiento de préstamos, teniendo en cuenta el control de pagos parciales, cuotas vencidas y conservación del historial financiero.

## 🚀 Funcionalidades

### 🔐 Autenticación y seguridad

* Inicio de sesión mediante el sistema de autenticación de Django.
* Protección de las páginas mediante usuarios autenticados.
* Redirección automática de usuarios no autenticados al inicio de sesión.

### 👥 Gestión de clientes

* Registro de clientes.
* Edición de información.
* Búsqueda por nombre y apellido.
* Activación y desactivación de clientes.
* Conservación del historial de clientes inactivos.
* Reactivación de clientes previamente desactivados.
* Los clientes no se eliminan físicamente para conservar su información histórica.

### 💵 Gestión de préstamos

* Registro de préstamos asociados a un cliente.
* Número de préstamo independiente para cada cliente.
* Monto prestado.
* Porcentaje de interés configurable para cada préstamo.
* Selección del tipo de préstamo:

  * Capital + intereses en cuotas.
  * Solo intereses.
* Frecuencia de cobro configurable:

  * Diaria.
  * Semanal.
  * Cada 15 días.
  * Mensual.
* Número de cuotas configurable.
* Selección independiente de la fecha del préstamo y del primer cobro.
* Cálculo automático de intereses y total a pagar.
* Generación automática de las cuotas y sus fechas de cobro.
* Cálculo de fechas mensuales considerando meses con diferente cantidad de días.
* Edición de préstamos mientras no existan pagos registrados.

### 📅 Control de cuotas

* Seguimiento individual de cada cuota.
* Identificación de cuotas pendientes, abonadas y pagadas.
* Cálculo automático del saldo pendiente.
* Manejo de cuotas vencidas.
* Una cuota permanece pendiente hasta completar su valor total.
* Una cuota puede recibir múltiples pagos.
* La fecha programada de cobro permanece independiente de la fecha real en que se realiza el pago.

### 💳 Registro de pagos

* Registro de pagos asociados a una cuota específica.
* Registro de fecha y hora exacta del pago.
* Permite realizar pagos parciales.
* Permite múltiples pagos sobre una misma cuota.
* Conservación permanente del historial de movimientos.
* Cálculo automático del valor abonado y saldo pendiente.
* Una cuota cambia a pagada cuando sus pagos completa
