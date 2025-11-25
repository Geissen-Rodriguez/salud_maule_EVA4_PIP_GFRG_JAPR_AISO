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

class FichaForm(forms.ModelForm):
    class Meta:
        model = FichaClinica
        fields = ['estado_actual', 'sector', 'resumen_tratamiento']
        widgets = {
            'estado_actual': forms.Select(attrs={'class': 'form-select'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen_tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = NotaMedica
        fields = ['detalle']
        widgets = {
            'detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
