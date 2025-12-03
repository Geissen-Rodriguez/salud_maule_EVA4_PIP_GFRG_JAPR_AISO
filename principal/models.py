from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.urls import reverse
from django.contrib.auth.models import User

rut_validator = RegexValidator(
    r'^[0-9Kk\-]+$',
    'El RUT solo puede contener números, guion y K.'
)

SECTORES = [
    ('verde', 'Verde'),
    ('amarillo', 'Amarillo'),
    ('rojo', 'Rojo'),
]

SUBSECTORES = [
    ('A', 'Sector A'),
    ('B', 'Sector B'),
    ('C', 'Sector C'),
]

CARGOS = [
    ('medico', 'Médico'),
    ('administrativo_ingreso', 'Administrativo ingreso'),
    ('director', 'Director'),
]

class PersonalSalud(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_salud'
    )
    rut = models.CharField(max_length=12, unique=True, validators=[rut_validator])
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    correo_institucional = models.EmailField(unique=True)
    cargo = models.CharField(max_length=30, choices=CARGOS)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.get_cargo_display()})"

    def get_absolute_url(self):
        return reverse('perfil_editar', kwargs={'pk': self.pk})

    def get_area_actual(self):
        # Retorna el nombre del área de la asignación activa, si existe.
        asignacion = self.asignaciones.filter(activo=True).first()
        if asignacion and asignacion.area:
            return asignacion.area.nombre
        return None

    def get_centro_actual(self):
        # Retorna el nombre del centro de la asignación activa, si existe.
        asignacion = self.asignaciones.filter(activo=True).first()
        if asignacion and asignacion.centro:
            return asignacion.centro.nombre
        return None
