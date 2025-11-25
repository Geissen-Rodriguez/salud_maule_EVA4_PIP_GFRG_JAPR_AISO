from django.db import models
from principal.models import PersonalSalud
from django.core.exceptions import ValidationError

# Estados clínicos del paciente
ESTADOS_PACIENTE = [
    ('alta', 'En alta'),
    ('tratamiento', 'En tratamiento'),
    ('preop', 'Pre Operatorio'),
]

# Tipos de centro de salud
TIPO_CENTRO = [
    ('hospital', 'Hospital'),
    ('cesfam', 'CESFAM'),
]

class CentroSalud(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CENTRO)
    ciudad = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class Area(models.Model):
    centro = models.ForeignKey(CentroSalud, on_delete=models.CASCADE, related_name='areas')
    nombre = models.CharField(max_length=80)

    class Meta:
        unique_together = ('centro', 'nombre')

    def __str__(self):
        return f"{self.nombre} - {self.centro.nombre}"

class Paciente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"

class IngresoPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='ingresos')
    centro = models.ForeignKey(CentroSalud, on_delete=models.PROTECT)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS_PACIENTE, default='tratamiento')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    detalles_alta = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def clean(self):
        if self.area and self.area.centro_id != self.centro_id:
            raise ValidationError('El área seleccionada no pertenece al centro elegido.')

    def marcar_alta(self, detalle: str):
        self.estado = 'alta'
        self.detalles_alta = detalle
        self.activo = False

    def __str__(self):
        return f"Ingreso #{self.id} - {self.paciente} - {self.centro}"

class FichaClinica(models.Model):
    ingreso = models.ForeignKey(IngresoPaciente, on_delete=models.CASCADE, related_name='fichas')
    estado_actual = models.CharField(max_length=20, choices=ESTADOS_PACIENTE, default='tratamiento')
    sector = models.CharField(max_length=80, blank=True)
    resumen_tratamiento = models.TextField(blank=True)
    medico_responsable = models.ForeignKey('principal.PersonalSalud', on_delete=models.PROTECT, related_name='fichas_responsables')

    def clean(self):
        if self.medico_responsable and self.medico_responsable.cargo != 'medico':
            raise ValidationError('El responsable debe tener cargo Médico.')


class NotaMedica(models.Model):
    ficha = models.ForeignKey(FichaClinica, on_delete=models.CASCADE, related_name='notas')
    medico = models.ForeignKey('principal.PersonalSalud', on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField()


class AsignacionClinica(models.Model):
    personal = models.ForeignKey('principal.PersonalSalud', on_delete=models.CASCADE, related_name='asignaciones')
    centro = models.ForeignKey(CentroSalud, on_delete=models.CASCADE, related_name='asignaciones')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='asignaciones')
    activo = models.BooleanField(default=True)


