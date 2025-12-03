from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

from .models import (
    Paciente, IngresoPaciente, FichaClinica, NotaMedica,
    CategoriaAlergia, Alergia, PacienteAlergia, Area
)
from .forms import PacienteForm, IngresoForm, FichaForm, NotaForm, PacienteClinicalForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

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
        queryset = IngresoPaciente.objects.select_related('paciente', 'centro', 'area').order_by('-fecha_ingreso')
        area_id = self.request.GET.get('area')
        if area_id:
            queryset = queryset.filter(area__id=area_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.all()
        area_id = self.request.GET.get('area')
        if area_id:
            try:
                context['selected_area_id'] = int(area_id)
            except ValueError:
                pass
        return context

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

    def get_success_url(self):
        return reverse_lazy('ingreso_detail', kwargs={'pk': self.kwargs['ingreso_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingreso = get_object_or_404(IngresoPaciente, pk=self.kwargs['ingreso_id'])
        if self.request.POST:
            context['clinical_form'] = PacienteClinicalForm(self.request.POST, instance=ingreso.paciente)
        else:
            context['clinical_form'] = PacienteClinicalForm(instance=ingreso.paciente)
        
        context['categorias_alergia'] = CategoriaAlergia.objects.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        clinical_form = context['clinical_form']
        ingreso = get_object_or_404(IngresoPaciente, pk=self.kwargs['ingreso_id'])
        
        if clinical_form.is_valid():
            clinical_form.save()
            
        form.instance.ingreso = ingreso
        form.instance.medico_responsable = self.request.user.perfil_salud
        return super().form_valid(form)

class FichaUpdateView(LoginRequiredMixin, SoloMedicoMixin, UpdateView):
    model = FichaClinica
    form_class = FichaForm
    template_name = 'clinica/fichas/ficha_form.html'
    success_url = reverse_lazy('ficha_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ficha = self.object
        
        if 'clinical_form' not in context:
            if self.request.POST:
                context['clinical_form'] = PacienteClinicalForm(self.request.POST, instance=ficha.ingreso.paciente)
            else:
                context['clinical_form'] = PacienteClinicalForm(instance=ficha.ingreso.paciente)
        
        context['categorias_alergia'] = CategoriaAlergia.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        clinical_form = PacienteClinicalForm(request.POST, instance=self.object.ingreso.paciente)
        
        if form.is_valid() and clinical_form.is_valid():
            clinical_form.save()
            return self.form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form, clinical_form=clinical_form))

    def form_valid(self, form):
        # clinical_form is already saved in post
        return super().form_valid(form)

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

# --- API Views para Alergias ---

@login_required
def get_alergias_by_categoria(request, categoria_id):
    alergias = Alergia.objects.filter(categoria_id=categoria_id).values('id', 'ale_nombre')
    return JsonResponse(list(alergias), safe=False)

@require_POST
@login_required
def agregar_alergia_paciente(request):
    try:
        data = json.loads(request.body)
        paciente_id = data.get('paciente_id')
        alergia_id = data.get('alergia_id')
        
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        alergia = get_object_or_404(Alergia, pk=alergia_id)
        
        PacienteAlergia.objects.create(paciente=paciente, alergia=alergia)
        
        return JsonResponse({'status': 'success', 'message': 'Alergia agregada correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@login_required
def eliminar_alergia_paciente(request):
    try:
        data = json.loads(request.body)
        paciente_id = data.get('paciente_id')
        alergia_id = data.get('alergia_id')
        
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        alergia = get_object_or_404(Alergia, pk=alergia_id)
        
        PacienteAlergia.objects.filter(paciente=paciente, alergia=alergia).delete()
        
        return JsonResponse({'status': 'success', 'message': 'Alergia eliminada correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

import logging
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Importa tu modelo y Mixins personalizados
from .models import FichaClinica
# Asume que SoloMedicoMixin y LoginRequiredMixin están definidos o importados
# Si no existen, necesitarás definirlos o eliminarlos y usar solo LoginRequiredMixin.
# from tu_app.mixins import SoloMedicoMixin  # Descomenta si usas un archivo mixins.py

# Se importa xhtml2pdf solo dentro de la función para manejo de errores
# from xhtml2pdf import pisa  # No es necesario aquí si lo importas dentro de render_to_pdf

logger = logging.getLogger(__name__)

# NOTA: Reemplaza 'SoloMedicoMixin' con la importación real o quítalo
# si no está definido en tu proyecto. Para este ejemplo, asumiremos que existe.

# ... [Tus importaciones previas] ...
from .models import (
    Paciente, IngresoPaciente, FichaClinica, NotaMedica,
    CategoriaAlergia, Alergia, PacienteAlergia # Asegúrate de importar PacienteAlergia
)
# ... [Tus Mixins y otras Vistas] ...

import logging
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from django.db.models import Q

# Importa tus modelos necesarios
from .models import (
    Paciente, IngresoPaciente, FichaClinica, NotaMedica,
    CategoriaAlergia, Alergia, PacienteAlergia
)

# Importa xhtml2pdf (necesaria para render_to_pdf)
from xhtml2pdf import pisa 

# Importa tus Mixins de Permisos (asumiendo que están en este archivo)
from django.contrib.auth.mixins import UserPassesTestMixin
class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'medico'
# Fin de Mixins de Permisos

logger = logging.getLogger(__name__)
import logging
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import get_object_or_404
# from django.db.models import Q # No es necesario para esta vista

# Importa tus modelos necesarios
from .models import (
    FichaClinica, NotaMedica, PacienteAlergia
)

# Importa xhtml2pdf (asumiendo que está disponible)
from xhtml2pdf import pisa 

logger = logging.getLogger(__name__)

# --- Mixin de Permisos (Incluido aquí para que sea 'copiar y pegar') ---
class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'medico'

import logging
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import get_object_or_404
# from django.db.models import Q # No es necesario para esta vista

# Importa tus modelos necesarios
from .models import (
    FichaClinica, NotaMedica, PacienteAlergia,
    Paciente, IngresoPaciente, CategoriaAlergia, Alergia # Incluimos todos los modelos referenciados
)

# Importa xhtml2pdf 
from xhtml2pdf import pisa 

logger = logging.getLogger(__name__)

# --- Mixin de Permisos (Requerido para que la vista funcione) ---
class SoloMedicoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               hasattr(self.request.user, 'perfil_salud') and \
               self.request.user.perfil_salud.cargo == 'medico'

# --- VISTA PARA GENERAR EL PDF ---
# ... (otras importaciones) ...
from django.utils import timezone
# --- VISTA PARA GENERAR EL PDF ---
class FichaPDFView(LoginRequiredMixin, SoloMedicoMixin, DetailView):
    """
    Vista que genera un PDF de una Ficha Clínica específica, incluyendo
    todos los datos del paciente, alergias y notas médicas.
    """
    model = FichaClinica
    template_name = 'clinica/fichas/ficha_pdf.html' 
    context_object_name = 'ficha'

    # 1. OPTIMIZACIÓN: Precarga las relaciones clave (ingreso, paciente, médico responsable)
    def get_queryset(self):
        """
        Precarga las relaciones ForeignKey para el objeto principal.
        """
        # Con esto, 'self.object' ya tiene 'ingreso' y 'medico_responsable' cargados.
        return FichaClinica.objects.select_related(
            'ingreso', 
            'ingreso__paciente',
            'medico_responsable'
        )

    def get_context_data(self, **kwargs):
        """
        Añade el objeto Paciente, Alergias, Notas Médicas, y el Perfil del Médico Logueado al contexto.
        """
        # 1. Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        
        ficha = self.object 
        
        # 2. Obtener el objeto Paciente asociado (ya precargado gracias a get_queryset)
        paciente = ficha.ingreso.paciente # Acceso sin consulta adicional
        
        # 3. Obtener las Alergias del Paciente (relación ManyToMany through)
        # Se sigue usando select_related para optimizar la carga de las relaciones de Alergia
        alergias_paciente = PacienteAlergia.objects.filter(paciente=paciente).select_related('alergia', 'alergia__categoria')
        
        # 4. Obtener las Notas Médicas 
        notas_medicas = NotaMedica.objects.filter(ficha=ficha).order_by('fecha_hora')

        # 5. Añadir los datos del paciente y clínicos al contexto
        context['paciente'] = paciente
        context['alergias_paciente'] = alergias_paciente
        context['notas_medicas'] = notas_medicas 
        
        # 6. INYECCIONES CLAVE PARA EL PDF
        context['perfil'] = self.request.user.perfil_salud
        context['now'] = timezone.now()
        
        return context

    def render_to_pdf(self, template_src, context_dict=None):
        """
        Renderiza la plantilla a bytes PDF y devuelve los bytes o None si hay error.
        """
        context_dict = context_dict or {}
        try:
            template = get_template(template_src)
            html = template.render(context_dict)
        except Exception as e:
            logger.exception("Error al renderizar plantilla %s: %s", template_src, e)
            return None

        result = BytesIO()
        # UTF-8 es clave para acentos
        pisa_status = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        
        if pisa_status.err:
            logger.error("Error de xhtml2pdf pisa: %s", pisa_status.err)
            return None
        
        return result.getvalue()

    def get(self, request, *args, **kwargs):
        """
        Sobrescribe el método GET para generar y servir el PDF.
        """
        # Llama a get_queryset y get_object
        self.object = self.get_object() 
        
        context = self.get_context_data(object=self.object) 
        pdf_bytes = self.render_to_pdf(self.template_name, context)
        
        if not pdf_bytes:
            return HttpResponse(
                "Error al generar el PDF. Revisa los logs del servidor para más detalles.",
                status=400
            )

        try:
            # Crea un nombre de archivo basado en el RUT del paciente
            filename = f"Ficha_{self.object.ingreso.paciente.rut}.pdf"
        except AttributeError:
            logger.warning("No se pudo obtener el RUT del paciente. Usando nombre genérico.")
            filename = f"Ficha_{self.object.pk}.pdf"
            
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
