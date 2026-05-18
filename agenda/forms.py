from datetime import date

from django import forms
from django.utils import timezone

from .models import EntradaAgenda


class EntradaAgendaForm(forms.ModelForm):
    dia = forms.TypedChoiceField(
        label='Dia',
        required=False,
        coerce=lambda value: int(value) if value else None,
        choices=[('', '---------')] + [(day, day) for day in range(1, 32)],
    )

    class Meta:
        model = EntradaAgenda
        fields = [
            'mes',
            'dia',
            'horario_inicio',
            'horario_fin',
            'nombre_actividad',
            'direccion_coordinacion',
            'localidad',
            'lugar_actividad',
            'poblacion_destinataria',
            'objetivo',
            'prioridad_actividad',
            'requerimientos_comunicacion',
            'informacion_brindada',
        ]
        widgets = {
            'horario_inicio': forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M',
            ),
            'horario_fin': forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M',
            ),
            'nombre_actividad': forms.Textarea(attrs={'rows': 3}),
            'objetivo': forms.Textarea(attrs={'rows': 4}),
            'requerimientos_comunicacion': forms.Textarea(attrs={'rows': 4}),
            'informacion_brindada': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # Extract is_editor from kwargs before calling super()
        self.is_editor_user = kwargs.pop('is_editor', False)
        super().__init__(*args, **kwargs)
        
        # Add 'realizada' field only for editors and only for existing instances
        if self.is_editor_user and self.instance.pk:
            self.fields['realizada'] = forms.BooleanField(
                required=False,
                label='Marcar como realizada',
                initial=self.instance.realizada,
                help_text='Las actividades realizadas tendrán menor prioridad en la visualización.',
            )
            self.fields['realizada'].widget.attrs['class'] = 'form-check-input'
        
        if not self.is_bound and not self.instance.pk:
            self.fields['mes'].initial = timezone.localdate().month
        elif not self.is_bound and self.instance.pk and self.instance.fecha:
            self.fields['dia'].initial = self.instance.fecha.day

        for name, field in self.fields.items():
            field.required = name == 'nombre_actividad'

        self.fields['horario_inicio'].input_formats = ['%H:%M']
        self.fields['horario_fin'].input_formats = ['%H:%M']
        self.fields['dia'].help_text = 'Opcional si la fecha todavia esta a definir.'
        self.fields['horario_inicio'].help_text = 'Opcional si el horario todavia esta a definir.'
        self.fields['horario_fin'].help_text = 'Opcional si la actividad no tiene horario de finalizacion.'

        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            if field.widget.__class__.__name__ == 'CheckboxInput':
                css_class = 'form-check-input'
            field.widget.attrs.setdefault('class', css_class)

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get('dia')
        mes = cleaned_data.get('mes')

        if dia and not mes:
            self.add_error('mes', 'Selecciona un mes para poder guardar el dia.')
            return cleaned_data

        if dia and mes:
            try:
                cleaned_data['fecha'] = date(timezone.localdate().year, mes, dia)
            except ValueError:
                self.add_error('dia', 'El dia no es valido para el mes seleccionado.')
        else:
            cleaned_data['fecha'] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fecha = self.cleaned_data.get('fecha')

        if commit:
            instance.save()
            self.save_m2m()

        return instance