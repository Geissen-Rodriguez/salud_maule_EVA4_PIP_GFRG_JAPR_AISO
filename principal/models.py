from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from django.contrib.auth.models import User


# Validador para RUT
rut_validator = RegexValidator(
    r'^[0-9Kk\-]+$',
    'El RUT solo puede contener números, guion y K.'
)


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
    cargo = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.cargo})"

    def get_absolute_url(self):
        return reverse('perfil_editar', kwargs={'pk': self.pk})


class TokenRecuperacionCuenta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.token} - {'Activo' if self.activo else 'Inactivo'}"
