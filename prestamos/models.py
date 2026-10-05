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
        ('mensual', 'Mensual'),
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

    numero_cuotas = models.PositiveIntegerField()

    fecha_prestamo = models.DateField()

    fecha_primer_cobro = models.DateField()

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Préstamo de {self.cliente} - ${self.monto}"

    def clean(self):

        if self.fecha_primer_cobro < self.fecha_prestamo:
            raise ValidationError(
                'La fecha del primer cobro no puede ser anterior a la fecha del préstamo.'
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
                self.numero_prestamo = ultimo_numero + 1

        super().save(*args, **kwargs)

        if es_nuevo:
            self.crear_cuotas()

    def crear_cuotas(self):

        interes = (
            self.monto * self.porcentaje_interes / Decimal('100')
        )

        total = self.monto + interes

        total = total.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

        valor_base = (
            total / self.numero_cuotas
        ).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

        total_acumulado = Decimal('0.00')

        for numero in range(1, self.numero_cuotas + 1):

            if numero == self.numero_cuotas:
                valor = total - total_acumulado
            else:
                valor = valor_base

            total_acumulado += valor

            fecha_cobro = self.calcular_fecha_cobro(numero)

            Cuota.objects.create(
                prestamo=self,
                numero=numero,
                fecha_cobro=fecha_cobro,
                valor=valor
            )

    def calcular_fecha_cobro(self, numero):

        if self.frecuencia == 'diaria':

            return self.fecha_primer_cobro + timedelta(
                days=numero - 1
            )

        if self.frecuencia == 'semanal':

            return self.fecha_primer_cobro + timedelta(
                weeks=numero - 1
            )

        if self.frecuencia == 'mensual':

            return sumar_meses(
                self.fecha_primer_cobro,
                numero - 1
            )

        return self.fecha_primer_cobro


def sumar_meses(fecha, meses):

    mes_total = fecha.month - 1 + meses

    año = fecha.year + mes_total // 12

    mes = mes_total % 12 + 1

    ultimo_dia = calendar.monthrange(año, mes)[1]

    dia = min(fecha.day, ultimo_dia)

    return date(año, mes, dia)


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
        return f"Cuota {self.numero} - {self.prestamo.cliente}"


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
        return f"Pago de ${self.monto} - {self.cuota}"