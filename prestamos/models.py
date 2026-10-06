from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import calendar

from django.db import models
from django.db.models import Max
from django.core.exceptions import ValidationError

from clientes.models import Cliente


class Prestamo(models.Model):

    FRECUENCIA_CHOICES = [
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Cada 15 días'),
        ('mensual', 'Mensual'),
    ]

    TIPO_PRESTAMO_CHOICES = [
        ('cuotas', 'Capital + intereses en cuotas'),
        ('solo_intereses', 'Solo intereses'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='prestamos'
    )

    numero_prestamo = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    porcentaje_interes = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    frecuencia = models.CharField(
        max_length=10,
        choices=FRECUENCIA_CHOICES
    )

    tipo_prestamo = models.CharField(
        max_length=20,
        choices=TIPO_PRESTAMO_CHOICES,
        default='cuotas'
    )

    numero_cuotas = models.PositiveIntegerField()

    fecha_prestamo = models.DateField()

    fecha_primer_cobro = models.DateField()

    activo = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"Préstamo de {self.cliente} - ${self.monto}"


    def clean(self):

        if self.fecha_primer_cobro < self.fecha_prestamo:

            raise ValidationError(
                'La fecha del primer cobro no puede ser anterior '
                'a la fecha del préstamo.'
            )

        if self.monto <= 0:

            raise ValidationError(
                'El monto del préstamo debe ser mayor que cero.'
            )

        if self.numero_cuotas <= 0:

            raise ValidationError(
                'El número de cuotas debe ser mayor que cero.'
            )

        if self.porcentaje_interes < 0:

            raise ValidationError(
                'El porcentaje de interés no puede ser negativo.'
            )


    def save(self, *args, **kwargs):

        self.full_clean()

        es_nuevo = self.pk is None

        if es_nuevo and self.numero_prestamo is None:

            ultimo_numero = self.cliente.prestamos.aggregate(
                max_numero=Max('numero_prestamo')
            )['max_numero']

            if ultimo_numero is None:

                self.numero_prestamo = 1

            else:

                self.numero_prestamo = (
                    ultimo_numero + 1
                )

        super().save(*args, **kwargs)

        if es_nuevo:

            self.crear_cuotas()


    def crear_cuotas(self):

        # =========================================
        # SOLO INTERESES
        # =========================================

        if self.tipo_prestamo == 'solo_intereses':

            interes_periodo = (
                self.monto *
                self.porcentaje_interes /
                Decimal('100')
            )

            interes_periodo = interes_periodo.quantize(
                Decimal('1'),
                rounding=ROUND_HALF_UP
            )

            # Redondear el interés de cada período
            # al múltiplo de $50 más cercano.
            interes_redondeado = (
                (interes_periodo / Decimal('50'))
                .quantize(
                    Decimal('1'),
                    rounding=ROUND_HALF_UP
                )
                * Decimal('50')
            )

            for numero in range(
                1,
                self.numero_cuotas + 1
            ):

                fecha_cobro = self.calcular_fecha_cobro(
                    numero
                )

                Cuota.objects.create(
                    prestamo=self,
                    numero=numero,
                    fecha_cobro=fecha_cobro,
                    valor=interes_redondeado
                )

            return


        # =========================================
        # CAPITAL + INTERESES EN CUOTAS
        # =========================================

        interes_periodo = (
            self.monto *
            self.porcentaje_interes /
            Decimal('100')
        )

        interes_total = (
            interes_periodo *
            self.numero_cuotas
        )

        total = (
            self.monto +
            interes_total
        )

        total = total.quantize(
            Decimal('1'),
            rounding=ROUND_HALF_UP
        )


        # Valor aproximado de cada cuota.
        valor_base = (
            total /
            self.numero_cuotas
        )


        # Redondear la cuota al múltiplo
        # de $50 más cercano.
        valor_redondeado = (
            (valor_base / Decimal('50'))
            .quantize(
                Decimal('1'),
                rounding=ROUND_HALF_UP
            )
            * Decimal('50')
        )


        # =========================================
        # AJUSTE PARA CONSERVAR EL TOTAL EXACTO
        # =========================================

        total_redondeado = (
            valor_redondeado *
            self.numero_cuotas
        )

        diferencia = (
            total -
            total_redondeado
        )


        # Cantidad de bloques de $50
        # que debemos corregir.
        bloques = int(
            abs(diferencia) / Decimal('50')
        )


        # =========================================
        # CUOTAS POR ENCIMA DEL TOTAL
        # =========================================

        if diferencia < 0:

            for numero in range(
                1,
                self.numero_cuotas + 1
            ):

                valor = valor_redondeado

                if numero <= bloques:

                    valor -= Decimal('50')

                fecha_cobro = self.calcular_fecha_cobro(
                    numero
                )

                Cuota.objects.create(
                    prestamo=self,
                    numero=numero,
                    fecha_cobro=fecha_cobro,
                    valor=valor
                )


        # =========================================
        # CUOTAS POR DEBAJO DEL TOTAL
        # =========================================

        else:

            for numero in range(
                1,
                self.numero_cuotas + 1
            ):

                valor = valor_redondeado

                if numero <= bloques:

                    valor += Decimal('50')

                fecha_cobro = self.calcular_fecha_cobro(
                    numero
                )

                Cuota.objects.create(
                    prestamo=self,
                    numero=numero,
                    fecha_cobro=fecha_cobro,
                    valor=valor
                )


    def calcular_fecha_cobro(self, numero):

        # =========================================
        # DIARIA
        # =========================================

        if self.frecuencia == 'diaria':

            return (
                self.fecha_primer_cobro +
                timedelta(days=numero - 1)
            )


        # =========================================
        # SEMANAL
        # =========================================

        if self.frecuencia == 'semanal':

            return (
                self.fecha_primer_cobro +
                timedelta(weeks=numero - 1)
            )


        # =========================================
        # QUINCENAL
        # =========================================

        if self.frecuencia == 'quincenal':

            return (
                self.fecha_primer_cobro +
                timedelta(
                    days=15 * (numero - 1)
                )
            )


        # =========================================
        # MENSUAL
        # =========================================

        if self.frecuencia == 'mensual':

            return sumar_meses(
                self.fecha_primer_cobro,
                numero - 1
            )


        return self.fecha_primer_cobro


def sumar_meses(fecha, meses):

    mes_total = (
        fecha.month -
        1 +
        meses
    )

    año = (
        fecha.year +
        mes_total // 12
    )

    mes = (
        mes_total % 12 +
        1
    )

    ultimo_dia = calendar.monthrange(
        año,
        mes
    )[1]

    dia = min(
        fecha.day,
        ultimo_dia
    )

    return date(
        año,
        mes,
        dia
    )


class Cuota(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
    ]

    prestamo = models.ForeignKey(
        Prestamo,
        on_delete=models.CASCADE,
        related_name='cuotas'
    )

    numero = models.PositiveIntegerField()

    fecha_cobro = models.DateField()

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )


    def __str__(self):

        return (
            f"Cuota {self.numero} - "
            f"{self.prestamo.cliente}"
        )


class Pago(models.Model):

    cuota = models.ForeignKey(
        Cuota,
        on_delete=models.CASCADE,
        related_name='pagos'
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha_hora = models.DateTimeField()


    def __str__(self):

        return (
            f"Pago de ${self.monto} - "
            f"{self.cuota}"
        )