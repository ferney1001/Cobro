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

### 💵 Gestión de préstamos

* Registro de préstamos asociados a un cliente.
* Número de préstamo independiente para cada cliente.
* Monto prestado.
* Porcentaje de interés configurable.
* Frecuencia de cobro:

  * Diaria
  * Semanal
  * Mensual
* Número de cuotas configurable.
* Selección independiente de la fecha del préstamo y del primer cobro.
* Cálculo automático de intereses y total a pagar.
* Generación automática de las cuotas y sus fechas de cobro.

### 📅 Control de cuotas

* Seguimiento individual de cada cuota.
* Identificación de cuotas pendientes, abonadas y pagadas.
* Cálculo automático del saldo pendiente.
* Manejo de fechas de cobro vencidas.
* Tratamiento especial para cobros mensuales en meses con diferente cantidad de días.

### 💳 Registro de pagos

* Registro de pagos asociados a una cuota específica.
* Registro de fecha y hora exacta del pago.
* Permite realizar pagos parciales.
* Permite múltiples pagos sobre una misma cuota.
* Conservación permanente del historial de movimientos.
* Una cuota permanece pendiente hasta completar su valor total.

### 📊 Dashboard

El panel principal permite visualizar rápidamente:

* Cobros programados para el día actual.
* Cuotas atrasadas.
* Cuotas con abonos.
* Cuotas pagadas.
* Saldo pendiente.
* Acceso directo al registro de pagos.

### 📚 Historial de préstamos

Los préstamos completamente pagados dejan de aparecer entre los préstamos pendientes, pero permanecen almacenados para conservar el historial y permitir futuras consultas contables.

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
* Gestión de préstamos.
* Generación automática de cuotas.
* Cálculo de intereses.
* Registro de pagos.
* Pagos parciales.
* Historial de pagos.
* Dashboard de cobros.
* Control de cuotas atrasadas.
* Control de préstamos pagados.

### Próximas funcionalidades

* Módulo de contabilidad.
* Historial general de movimientos.
* Consulta de préstamos pagados.
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

https://github.com/ferney1001

```

### Para tu hoja de vida

Este proyecto te puede servir bastante como **proyecto de portafolio**, especialmente porque no es solamente "hice una página en Django". Tiene cosas interesantes para un perfil junior:

**Python + Django + ORM + SQLite + autenticación + relaciones entre modelos + lógica de negocio + fechas + pagos parciales + Git.**

Y cuando terminemos **Contabilidad**, podemos mejorar todavía más el README para mostrar consultas, reportes y manejo de información financiera.

Solo una cosa importante antes de subir este README: **no pongas contraseñas, claves API, `SECRET_KEY` ni archivos `.env` en GitHub**. Tu repositorio es público.
```
