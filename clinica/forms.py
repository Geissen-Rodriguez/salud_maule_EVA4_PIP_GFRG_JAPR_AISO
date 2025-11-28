# clinica/forms.py
from django import forms
from .models import Paciente, IngresoPaciente, FichaClinica, NotaMedica

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombres', 'apellidos', 'correo']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

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
        
        # Validacion Verificar si el paciente ya tiene un ingreso activo
        if paciente:
            existe_activo = IngresoPaciente.objects.filter(
                paciente=paciente, 
                activo=True
            ).exclude(pk=self.instance.pk).exists() # Excluirse a si mismo para actualizaciones
            
            if existe_activo:
                raise forms.ValidationError('El paciente ya tiene un ingreso activo. Debe dar de alta el ingreso anterior antes de crear uno nuevo.')
        
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
