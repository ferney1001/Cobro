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
* Una cuota cambia a pagada cuando sus pagos completan el valor total de la cuota.
* Los pagos pueden registrarse posteriormente con su fecha y hora correspondiente.

### 📊 Dashboard

El panel principal permite visualizar rápidamente:

* Cobros programados para el día actual.
* Cuotas atrasadas.
* Cuotas con abonos.
* Cuotas pagadas.
* Saldo pendiente.
* Acceso directo al registro de pagos.

El dashboard diferencia los cobros del día actual de las cuotas que ya se encuentran atrasadas.

### 📚 Historial de préstamos

Los préstamos completamente pagados permanecen almacenados para conservar el historial financiero.

El sistema permite consultar los préstamos mediante dos secciones:

* **Préstamos por pagar.**
* **Préstamos pagados.**

La búsqueda de préstamos puede realizarse por nombre o apellido del cliente.

Los préstamos completamente pagados pueden eliminarse manualmente mediante una confirmación previa. Al eliminarlos, también se eliminan sus cuotas y registros de pago asociados.

Los préstamos que todavía tienen saldo pendiente no pueden eliminarse.

---

## 🛠️ Tecnologías utilizadas

* **Python 3.13**
* **Django 6**
* **SQLite**
* **HTML5**
* **CSS3**
* **JavaScript**
* **Git**
* **GitHub**

## 🧠 Conceptos aplicados

Durante el desarrollo se han aplicado conceptos de:

* Programación orientada a objetos.
* Modelado de datos.
* Relaciones entre modelos.
* ORM de Django.
* CRUD.
* Autenticación y autorización.
* Formularios de Django.
* Validación de datos.
* Consultas con Django ORM.
* Manejo de fechas.
* Cálculos financieros con `Decimal`.
* Separación entre lógica de negocio y presentación.
* Diseño responsive.
* Control de versiones con Git.

## 🗂️ Estructura del proyecto

```text
Cobro/
│
├── clientes/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── templatetags/
│
├── prestamos/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── static/
│
├── manage.py
├── requirements.txt
└── README.md
```

## 📌 Estado actual

El proyecto se encuentra en desarrollo.

Actualmente cuenta con:

* Autenticación.
* Gestión de clientes.
* Activación y desactivación de clientes.
* Gestión de préstamos.
* Tipos de préstamo: capital + intereses y solo intereses.
* Frecuencias de cobro diaria, semanal, quincenal y mensual.
* Generación automática de cuotas.
* Cálculo de intereses.
* Registro de pagos.
* Pagos parciales.
* Múltiples pagos por cuota.
* Historial de pagos.
* Dashboard de cobros.
* Control de cuotas atrasadas.
* Control de préstamos por pagar.
* Historial de préstamos pagados.
* Eliminación de préstamos completamente pagados.
* Diseño responsive para dispositivos móviles.

### Próximas funcionalidades

* Módulo de contabilidad.
* Resumen general de dinero prestado y cobrado.
* Contabilidad por cliente.
* Separación entre capital recuperado e intereses recibidos.
* Cálculo de capital pendiente.
* Historial general de movimientos.
* Filtros por fechas.
* Reportes financieros.
* Exportación a Excel.
* Generación de PDF.
* Mejoras de seguridad para despliegue.
* Publicación de la aplicación en un servidor.

## 💻 Instalación local

Clonar el repositorio:

```bash
git clone https://github.com/ferney1001/Cobro.git
cd Cobro
```

Crear y activar el entorno virtual:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

Aplicar las migraciones:

```powershell
python manage.py migrate
```

Crear un usuario administrador:

```powershell
python manage.py createsuperuser
```

Ejecutar el servidor:

```powershell
python manage.py runserver
```

La aplicación estará disponible localmente en:

```text
http://127.0.0.1:8000/
```

## 👨‍💻 Autor

**Ferney Stiven Rueda Gonzalez**

Ingeniero de Sistemas | Desarrollador Junior

Interesado principalmente en desarrollo con **Python, Java y bases de datos**.

GitHub:

```text
https://github.com/ferney1001
```
