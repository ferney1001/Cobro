from django import forms
from django.utils import timezone

from .models import Prestamo, Pago


class PrestamoForm(forms.ModelForm):

    class Meta:
        model = Prestamo

        fields = [
            'cliente',
            'monto',
            'porcentaje_interes',
            'frecuencia',
            'numero_cuotas',
            'fecha_prestamo',
            'fecha_primer_cobro',
        ]

        widgets = {
            'cliente': forms.HiddenInput(),

            'fecha_prestamo': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            ),

            'fecha_primer_cobro': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['frecuencia'].choices = [
            ('', 'Seleccione la frecuencia de cobro'),
            ('diaria', 'Diaria'),
            ('semanal', 'Semanal'),
            ('mensual', 'Mensual'),
        ]

        if not self.instance.pk:
            self.initial['fecha_prestamo'] = timezone.localdate()


class PagoForm(forms.ModelForm):

    class Meta:
        model = Pago

        fields = [
            'monto',
            'fecha_hora',
        ]

        widgets = {
            'fecha_hora': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local'
                }
            ),
        }