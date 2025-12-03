# clinica/urls.py
from django.urls import path
from .views import (
    # Vistas de Paciente
    PacienteCreateView, PacienteListView, PacienteDetailView, PacienteUpdateView, 
    
    # Vistas de Ingreso
    IngresoCreateView, IngresoListView, IngresoDetailView, IngresoUpdateView, IngresoDeleteView,
    
    # Vistas de Ficha y Nota
    FichaListView, FichaUpdateView, NotaCreateView, FichaCreateView, MedicoIngresoListView,
    
    # Vistas de Reporte
    ReporteMedicosView,

    # API Views
    get_alergias_by_categoria, agregar_alergia_paciente, eliminar_alergia_paciente
)

urlpatterns = [
    
  
    # RECURSO: PACIENTES (/pacientes/)
    # (Mapeado a Admin. Ingreso)

    
    # GET: Listar todos (Index/List)
    path('pacientes/', PacienteListView.as_view(), name='paciente_list'),
    
    # POST: Crear nuevo recurso (Create)
    path('pacientes/nuevo/', PacienteCreateView.as_view(), name='paciente_create'),
    
    # GET: Obtener detalle del recurso (Detail)
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name='paciente_detail'),
    
    # PUT/POST: Actualizar recurso (Edit)
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name='paciente_edit'),


 
    # RECURSO: INGRESOS (/ingresos/)
    # (Mapeado a Admin. Ingreso)
  
    
    # GET: Listar todos (Index/List)
    path('ingresos/', IngresoListView.as_view(), name='ingreso_list'), 
    
    # POST: Crear nuevo recurso (Create)
    path('ingresos/nuevo/', IngresoCreateView.as_view(), name='ingreso_create'),
    
    # GET: Obtener detalle del recurso (Detail)
    path('ingresos/<int:pk>/', IngresoDetailView.as_view(), name='ingreso_detail'),
    
    # PUT/POST: Actualizar recurso (Edit)
    path('ingresos/<int:pk>/editar/', IngresoUpdateView.as_view(), name='ingreso_edit'),
    
    # DELETE: Eliminar recurso (Delete)
    path('ingresos/<int:pk>/eliminar/', IngresoDeleteView.as_view(), name='ingreso_delete'),


 
    #  RECURSO: FICHAS Y NOTAS (Médico)

    
    # GET: Listar todos los ingresos activos (Para Médico)
    path('medico/pacientes/', MedicoIngresoListView.as_view(), name='medico_ingreso_list'),

    # GET: Listar Fichas (Index para Médico Responsable)
    path('fichas/', FichaListView.as_view(), name='ficha_list'), 
    
    # PUT/POST: Actualizar Ficha (Edit)
    path('fichas/<int:pk>/editar/', FichaUpdateView.as_view(), name='ficha_edit'),
    
    # POST: Crear Nota (Recurso anidado en la Ficha)
    path('fichas/<int:ficha_id>/nota/', NotaCreateView.as_view(), name='nota_create'),

    # POST: Crear Ficha (Desde Ingreso)
    path('ingresos/<int:ingreso_id>/ficha/nueva/', FichaCreateView.as_view(), name='ficha_create'),


    #  RECURSO: REPORTES (Director)

    
    # GET: Obtener reporte
    path('reportes/medicos/', ReporteMedicosView.as_view(), name='reporte_medicos'),

    # API ALERGIAS
    path('api/alergias/categoria/<int:categoria_id>/', get_alergias_by_categoria, name='api_alergias_categoria'),
    path('api/alergias/agregar/', agregar_alergia_paciente, name='api_alergias_agregar'),
    path('api/alergias/eliminar/', eliminar_alergia_paciente, name='api_alergias_eliminar'),
]