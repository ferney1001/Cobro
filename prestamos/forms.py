from decimal import Decimal

from django import forms
from django.utils import timezone

from .models import Prestamo, Pago


class PrestamoForm(forms.ModelForm):

    class Meta:

        model = Prestamo

        fields = [
            'cliente',
            'tipo_prestamo',
            'monto',
            'porcentaje_interes',
            'frecuencia',
            'numero_cuotas',
            'fecha_prestamo',
            'fecha_primer_cobro',
        ]

        widgets = {
            'cliente': forms.HiddenInput(),
            'tipo_prestamo': forms.Select(),
            'monto': forms.TextInput(
                attrs={
                    'inputmode': 'numeric',
                    'autocomplete': 'off'
                }
            ),
            'porcentaje_interes': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'numero_cuotas': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '1',
                    'min': '1',
                    'inputmode': 'numeric',
                }
            ),
            'fecha_prestamo': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'fecha_primer_cobro': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo_prestamo'].choices = [
            ('', 'Seleccione el tipo de préstamo'),
            ('cuotas', 'Capital + intereses en cuotas'),
            ('solo_intereses', 'Solo intereses'),
        ]

        self.fields['frecuencia'].choices = [
            ('', 'Seleccione la frecuencia de cobro'),
            ('diaria', 'Diaria'),
            ('semanal', 'Semanal'),
            ('quincenal', 'Cada 15 días'),
            ('mensual', 'Mensual'),
        ]

        if not self.instance.pk:
            self.initial['fecha_prestamo'] = timezone.localdate()


class PrestamoEditarForm(forms.ModelForm):

    class Meta:

        model = Prestamo

        fields = [
            'tipo_prestamo',
            'monto',
            'porcentaje_interes',
            'frecuencia',
            'numero_cuotas',
            'fecha_prestamo',
            'fecha_primer_cobro',
        ]

        widgets = {
            'tipo_prestamo': forms.Select(),
            'monto': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '1',
                    'min': '1',
                    'inputmode': 'numeric',
                }
            ),
            'porcentaje_interes': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '0.01',
                    'min': '0',
                }
            ),
            'numero_cuotas': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '1',
                    'min': '1',
                    'inputmode': 'numeric',
                }
            ),
            'fecha_prestamo': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'fecha_primer_cobro': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipo_prestamo'].choices = [
            ('', 'Seleccione el tipo de préstamo'),
            ('cuotas', 'Capital + intereses en cuotas'),
            ('solo_intereses', 'Solo intereses'),
        ]

        self.fields['frecuencia'].choices = [
            ('', 'Seleccione la frecuencia de cobro'),
            ('diaria', 'Diaria'),
            ('semanal', 'Semanal'),
            ('quincenal', 'Cada 15 días'),
            ('mensual', 'Mensual'),
        ]


class PagoForm(forms.ModelForm):

    class Meta:

        model = Pago

        fields = [
            'monto',
            'fecha_hora'
        ]

        widgets = {
            'monto': forms.TextInput(
                attrs={
                    'inputmode': 'numeric',
                    'autocomplete': 'off'
                }
            ),
            'fecha_hora': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.initial['fecha_hora'] = timezone.localtime().strftime(
                '%Y-%m-%dT%H:%M'
            )

    def clean_monto(self):

        valor = self.cleaned_data['monto']

        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '').strip()

            if valor == '':
                raise forms.ValidationError(
                    'Ingresa un monto.'
                )

            try:
                monto = Decimal(valor)
            except Exception:
                raise forms.ValidationError(
                    'Ingresa un monto válido.'
                )
        else:
            monto = valor

        if monto <= 0:
            raise forms.ValidationError(
                'El monto debe ser mayor que cero.'
            )

        if monto != monto.quantize(Decimal('1')):
            raise forms.ValidationError(
                'El pago debe registrarse en pesos enteros, sin centavos.'
            )

        return monto