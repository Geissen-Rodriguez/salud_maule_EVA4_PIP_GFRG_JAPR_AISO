from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Paciente, IngresoPaciente, FichaClinica, NotaMedica
from .forms import PacienteForm, IngresoForm, FichaForm, NotaForm

# --- Mixins de Permisos ---

class SoloDirectorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'director'

class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'medico'

class SoloAdministrativoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'administrativo_ingreso'

# --- Vistas de Paciente ---

class PacienteListView(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = 'clinica/pacientes/paciente_list.html'
    context_object_name = 'pacientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(rut__icontains=q) | 
                Q(nombres__icontains=q) | 
                Q(apellidos__icontains=q)
            )
        return queryset

class PacienteCreateView(LoginRequiredMixin, SoloAdministrativoMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'clinica/pacientes/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'clinica/pacientes/paciente_detail.html'
    context_object_name = 'paciente'

class PacienteUpdateView(LoginRequiredMixin, SoloAdministrativoMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'clinica/pacientes/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

# --- Vistas de Ingreso ---

class IngresoListView(LoginRequiredMixin, ListView):
    model = IngresoPaciente
    template_name = 'clinica/ingresos/ingreso_list.html'
    context_object_name = 'ingresos'
    paginate_by = 10

    def get_queryset(self):
        return IngresoPaciente.objects.select_related('paciente', 'centro', 'area').order_by('-fecha_ingreso')

class IngresoCreateView(LoginRequiredMixin, SoloAdministrativoMixin, CreateView):
    model = IngresoPaciente
    form_class = IngresoForm
    template_name = 'clinica/ingresos/ingreso_form.html'
    success_url = reverse_lazy('ingreso_list')

class IngresoDetailView(LoginRequiredMixin, DetailView):
    model = IngresoPaciente
    template_name = 'clinica/ingresos/ingreso_detail.html'
    context_object_name = 'ingreso'

class IngresoUpdateView(LoginRequiredMixin, SoloAdministrativoMixin, UpdateView):
    model = IngresoPaciente
    form_class = IngresoForm
    template_name = 'clinica/ingresos/ingreso_form.html'
    success_url = reverse_lazy('ingreso_list')

class IngresoDeleteView(LoginRequiredMixin, SoloAdministrativoMixin, DeleteView):
    model = IngresoPaciente
    template_name = 'clinica/ingresos/ingreso_confirm_delete.html'
    success_url = reverse_lazy('ingreso_list')

# --- Vistas de Ficha y Nota (Médico) ---

class MedicoIngresoListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = IngresoPaciente
    template_name = 'clinica/medico/ingreso_list_medico.html'
    context_object_name = 'ingresos'

    def get_queryset(self):
        # Mostrar todos los ingresos activos
        return IngresoPaciente.objects.filter(activo=True).select_related('paciente', 'centro', 'area').order_by('-fecha_ingreso')

class FichaListView(LoginRequiredMixin, SoloMedicoMixin, ListView):
    model = FichaClinica
    template_name = 'clinica/fichas/ficha_list.html'
    context_object_name = 'fichas'

    def get_queryset(self):
        # Filtrar fichas asignadas al medico o de su área (si aplica)
        # Por ahora mostramos todas las fichas donde el medico es responsable
        perfil = self.request.user.perfil_salud
        return FichaClinica.objects.filter(medico_responsable=perfil).select_related('ingreso__paciente')

class FichaCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
    model = FichaClinica
    form_class = FichaForm
    template_name = 'clinica/fichas/ficha_form.html'
    success_url = reverse_lazy('ficha_list')

    def form_valid(self, form):
        ingreso = get_object_or_404(IngresoPaciente, pk=self.kwargs['ingreso_id'])
        form.instance.ingreso = ingreso
        form.instance.medico_responsable = self.request.user.perfil_salud
        return super().form_valid(form)

class FichaUpdateView(LoginRequiredMixin, SoloMedicoMixin, UpdateView):
    model = FichaClinica
    form_class = FichaForm
    template_name = 'clinica/fichas/ficha_form.html'
    success_url = reverse_lazy('ficha_list')

class NotaCreateView(LoginRequiredMixin, SoloMedicoMixin, CreateView):
    model = NotaMedica
    form_class = NotaForm
    template_name = 'clinica/fichas/nota_form.html'
    
    def get_success_url(self):
        return reverse_lazy('ingreso_detail', kwargs={'pk': self.object.ficha.ingreso.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ficha'] = get_object_or_404(FichaClinica, pk=self.kwargs['ficha_id'])
        return context

    def form_valid(self, form):
        perfil = getattr(self.request.user, 'perfil_salud', None)
        if not perfil or perfil.cargo != 'medico':
            raise PermissionDenied
        form.instance.medico = perfil
        form.instance.ficha = get_object_or_404(FichaClinica, pk=self.kwargs['ficha_id'])
        return super().form_valid(form)

# --- Vistas de Reporte (Director) ---

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