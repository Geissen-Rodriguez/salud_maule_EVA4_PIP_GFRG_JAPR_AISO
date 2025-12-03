# clinica/forms.py
from django import forms
from decimal import Decimal
from .models import Paciente, IngresoPaciente, FichaClinica, NotaMedica

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombres', 'apellidos', 'correo', 'telefono', 'sexo']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solo números.")
            if len(telefono) != 9:
                raise forms.ValidationError("El teléfono debe tener 9 dígitos.")
            if not telefono.startswith('9'):
                raise forms.ValidationError("El teléfono debe comenzar con 9.")
        return telefono

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if nombres and not all(x.isalpha() or x.isspace() for x in nombres):
            raise forms.ValidationError("El nombre solo debe contener letras.")
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if apellidos and not all(x.isalpha() or x.isspace() for x in apellidos):
            raise forms.ValidationError("El apellido solo debe contener letras.")
        return apellidos


class IngresoForm(forms.ModelForm):
    class Meta:
        model = IngresoPaciente
        fields = ['paciente', 'centro', 'area']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'centro': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')

        if paciente:
            existe_activo = IngresoPaciente.objects.filter(
                paciente=paciente,
                activo=True
            ).exclude(pk=self.instance.pk).exists()

            if existe_activo:
                raise forms.ValidationError(
                    'El paciente ya tiene un ingreso activo. Debe dar de alta el anterior.'
                )

        return cleaned_data


class FichaForm(forms.ModelForm):
    class Meta:
        model = FichaClinica
        fields = ['estado_actual', 'sector', 'subsector', 'resumen_tratamiento']
        widgets = {
            'estado_actual': forms.Select(attrs={'class': 'form-select'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'subsector': forms.Select(attrs={'class': 'form-select'}),
            'resumen_tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class NotaForm(forms.ModelForm):
    class Meta:
        model = NotaMedica
        fields = ['detalle']
        widgets = {
            'detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ------------------------------------------------------
#   FORMULARIO CLÍNICO: PESO Y ESTATURA CON COMA
# ------------------------------------------------------

class PacienteClinicalForm(forms.ModelForm):

    # Convertimos los DecimalField originales a CharField
    peso = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 64,4'}),
        required=False
    )
    estatura = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1,75'}),
        required=False
    )

    class Meta:
        model = Paciente
        fields = [
            'peso', 'estatura', 'grupo_sanguineo', 'fecha_nacimiento',
            'fecha_ingreso', 'detalles_alta', 'alergias_libre'
        ]
        widgets = {
            'grupo_sanguineo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_nacimiento': forms.SelectDateWidget(
                years=range(1920, 2026),
                attrs={'class': 'form-select',
                       'style': 'width: auto; display: inline-block; margin-right: 5px;'}
            ),
            'fecha_ingreso': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'detalles_alta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alergias_libre': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    # -------------------------
    #  VALIDACIONES PERSONALIZADAS
    # -------------------------

    def clean_peso(self):
        data = self.cleaned_data.get('peso')
        if not data:
            return None

        data = data.replace(',', '.')
        try:
            val = Decimal(data)
        except:
            raise forms.ValidationError("Peso inválido.")

        if val < 1 or val > 1000:
            raise forms.ValidationError("El peso debe estar entre 1 y 1000 kg.")

        return val

    def clean_estatura(self):
        data = self.cleaned_data.get('estatura')
        if not data:
            return None

        data = data.replace(',', '.')
        try:
            val = Decimal(data)
        except:
            raise forms.ValidationError("Estatura inválida.")

        if val < Decimal('0.50') or val > Decimal('3.00'):
            raise forms.ValidationError("La estatura debe estar entre 0.50 y 3.00 metros.")

        return val
