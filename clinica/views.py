# clinica/views.py

from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery

from .models import Paciente, IngresoPaciente, FichaClinica, NotaMedica, ESTADOS_PACIENTE
from .forms import PacienteForm, IngresoForm, FichaForm, NotaForm


# --- Mixins de control por cargo ---

class SoloAdminIngresoMixin:
    def dispatch(self, request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil_salud', None)
        if not perfil or perfil.cargo != 'administrativo_ingreso':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

#  NUEVO MIXIN: Permite acceso a Médicos y Administrativos (para ver datos)
class SoloMedicoOAdminMixin:
    def dispatch(self, request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil_salud', None)
        # Permite si el cargo es 'administrativo_ingreso' O 'medico'
        if not perfil or perfil.cargo not in ['administrativo_ingreso', 'medico']:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SoloMedicoMixin:
    def dispatch(self, request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil_salud', None)
        if not perfil or perfil.cargo != 'medico':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SoloDirectorMixin:
    def dispatch(self, request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil_salud', None)
        if not perfil or perfil.cargo != 'director':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# --- Administrativo ingreso (Paciente y Ingreso) ---

# --- PACIENTE ---

class PacienteCreateView(LoginRequiredMixin, SoloAdminIngresoMixin, CreateView):
    # Solo Administrativo puede crear
    model = Paciente
    form_class = PacienteForm
    template_name = 'clinica/pacientes/paciente_form.html' 
    success_url = '/pacientes/' 

class PacienteListView(LoginRequiredMixin, SoloMedicoOAdminMixin, ListView): #  CAMBIO DE PERMISO
    # Listar permitido a Admin y Médico
    model = Paciente
    template_name = 'clinica/pacientes/paciente_list.html'
    context_object_name = 'pacientes'

    def get_queryset(self):
        # Optimización para mostrar el último estado de ingreso en la lista (Mantenida)
        ultimo_ingreso = IngresoPaciente.objects.filter(
            paciente=OuterRef('pk')
        ).order_by('-fecha_ingreso')

        estado_subquery = ultimo_ingreso.values('estado')[:1]
        fecha_subquery = ultimo_ingreso.values('fecha_ingreso')[:1]
        centro_subquery = ultimo_ingreso.values('centro__nombre')[:1]
        
        queryset = Paciente.objects.annotate(
            ultimo_estado=Subquery(estado_subquery),
            fecha_ultimo_ingreso=Subquery(fecha_subquery),
            centro_actual=Subquery(centro_subquery)
        ).order_by('apellidos')

        Paciente.get_ultimo_estado_display = lambda self: dict(ESTADOS_PACIENTE).get(self.ultimo_estado, self.ultimo_estado)

        return queryset

class PacienteDetailView(LoginRequiredMixin, SoloMedicoOAdminMixin, DetailView): #  CAMBIO DE PERMISO
    # Detalle permitido a Admin y Médico
    model = Paciente
    template_name = 'clinica/pacientes/paciente_detail.html' 
    context_object_name = 'paciente'

class PacienteUpdateView(LoginRequiredMixin, SoloAdminIngresoMixin, UpdateView):
    # Actualizar solo para Admin
    model = Paciente
    form_class = PacienteForm
    template_name = 'clinica/pacientes/paciente_form.html' 
    success_url = '/pacientes/'


# --- INGRESO ---

class IngresoCreateView(LoginRequiredMixin, SoloAdminIngresoMixin, CreateView):
    # Crear solo para Admin
    model = IngresoPaciente
    form_class = IngresoForm
    template_name = 'clinica/ingresos/ingreso_form.html'
    success_url = '/ingresos/'

class IngresoListView(LoginRequiredMixin, SoloMedicoOAdminMixin, ListView): #  CAMBIO DE PERMISO
    # Listar permitido a Admin y Médico
    model = IngresoPaciente
    template_name = 'clinica/ingresos/ingreso_list.html' 
    context_object_name = 'ingresos'
    
    def get_queryset(self):
        # Consulta optimizada para la lista de ingresos (Mantenida)
        return IngresoPaciente.objects.select_related('paciente', 'centro', 'area').order_by('-fecha_ingreso')

class IngresoDetailView(LoginRequiredMixin, SoloMedicoOAdminMixin, DetailView): #  CAMBIO DE PERMISO
    # Detalle permitido a Admin y Médico
    model = IngresoPaciente
    template_name = 'clinica/ingresos/ingreso_detail.html' 
    context_object_name = 'ingreso'

class IngresoUpdateView(LoginRequiredMixin, SoloAdminIngresoMixin, UpdateView):
    # Actualizar solo para Admin
    model = IngresoPaciente
    form_class = IngresoForm
    template_name = 'clinica/ingresos/ingreso_form.html'
    success_url = '/ingresos/'


# --- Médico (Ficha y Nota) ---
# Estas vistas SÍ deben restringirse solo a Médico (SoloMedicoMixin)

class FichaUpdateView(LoginRequiredMixin, SoloMedicoMixin, UpdateView):
    model = FichaClinica
    form_class = FichaForm
    template_name = 'clinica/fichas/ficha_form.html'
    success_url = '/fichas/'


class FichaListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = FichaClinica
    template_name = 'clinica/fichas/ficha_list.html' 
    context_object_name = 'fichas'

    def get_queryset(self):
        perfil = getattr(self.request.user, 'perfil_salud', None)
        if perfil and perfil.cargo == 'medico':
            return FichaClinica.objects.filter(
                medico_responsable=perfil
            ).select_related('ingreso__paciente', 'ingreso__centro', 'ingreso__area')
        return FichaClinica.objects.none()


class NotaCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
    model = NotaMedica
    form_class = NotaForm
    template_name = 'clinica/notas/nota_form.html' 
    success_url = '/fichas/'

    def form_valid(self, form):
        perfil = getattr(self.request.user, 'perfil_salud', None)
        if not perfil or perfil.cargo != 'medico':
            raise PermissionDenied
        form.instance.medico = perfil
        form.instance.ficha = get_object_or_404(FichaClinica, pk=self.kwargs['ficha_id'])
        return super().form_valid(form)

# --- Director ---

class ReporteMedicosView(LoginRequiredMixin, SoloDirectorMixin, ListView):
    model = FichaClinica
    template_name = 'clinica/reportes/medicos.html' 
    context_object_name = 'fichas'

    def get_queryset(self):
        return FichaClinica.objects.select_related(
            'medico_responsable',
            'ingreso__paciente',
            'ingreso__centro',
            'ingreso__area'
        ).order_by('ingreso__centro__nombre', 'medico_responsable__apellidos')