
import os

content = """{% extends 'layout/base.html' %}
{% block title %}Ficha Clínica{% endblock %}

{% block content %}
<div class="container-fluid">
  <div class="row">
    <!-- Columna Izquierda: Datos Clínicos del Paciente -->
    <div class="col-md-6">
      <div class="card shadow mb-4">
        <div class="card-header py-3 bg-info text-white">
          <h6 class="m-0 font-weight-bold">Datos Clínicos del Paciente: {{ clinical_form.instance.nombres }} {{ clinical_form.instance.apellidos }}</h6>
        </div>
        <div class="card-body">
          <form method="post" id="clinicalForm">
            {% csrf_token %}
            <!-- Renderizamos los campos del formulario clínico manualmente para mejor control -->
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="{{ clinical_form.peso.id_for_label }}">Peso (kg)</label>
                {{ clinical_form.peso }}
              </div>
              <div class="col-md-6 mb-3">
                <label for="{{ clinical_form.estatura.id_for_label }}">Estatura (m)</label>
                {{ clinical_form.estatura }}
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="{{ clinical_form.grupo_sanguineo.id_for_label }}">Grupo Sanguíneo</label>
                {{ clinical_form.grupo_sanguineo }}
              </div>
              <div class="col-md-6 mb-3">
                <label for="{{ clinical_form.fecha_nacimiento.id_for_label }}">Fecha Nacimiento</label>
                {{ clinical_form.fecha_nacimiento }}
              </div>
            </div>

            <hr>
            <h6 class="font-weight-bold text-primary">Gestión de Alergias</h6>

            <!-- Selección de Alergias -->
            <div class="row mb-3">
              <div class="col-md-5">
                <label>Categoría</label>
                <select id="categoriaSelect" class="form-control">
                  <option value="">Seleccione Categoría...</option>
                  {% for cat in categorias_alergia %}
                  <option value="{{ cat.id }}">{{ cat.nombre_categoria }}</option>
                  {% endfor %}
                </select>
              </div>
              <div class="col-md-5">
                <label>Alergia</label>
                <select id="alergiaSelect" class="form-control" disabled>
                  <option value="">Seleccione Alergia...</option>
                </select>
              </div>
              <div class="col-md-2 d-flex align-items-end">
                <button type="button" id="btnAgregarAlergia" class="btn btn-success btn-block">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
            </div>

            <!-- Lista de Alergias Actuales -->
            <div id="listaAlergias" class="mb-3">
                {% if clinical_form.instance.alergias.exists %}
                    {% for alergia in clinical_form.instance.alergias.all %}
                        <span class="badge bg-warning text-dark me-1 mb-1" id="badge-alergia-{{ alergia.id }}">
                            {{ alergia.ale_nombre }}
                            <i class="fas fa-times ms-1 text-danger cursor-pointer btn-eliminar-alergia" 
                               data-paciente-id="{{ clinical_form.instance.id }}" 
                               data-alergia-id="{{ alergia.id }}" 
                               style="cursor: pointer;"></i>
                        </span>
                    {% endfor %}
                {% else %}
                    <span id="no-alergias-msg" class="text-muted small">Sin alergias registradas.</span>
                {% endif %}
            </div>

            <div class="mb-3">
              <label for="{{ clinical_form.alergias_libre.id_for_label }}">Otras Alergias (Texto Libre)</label>
              {{ clinical_form.alergias_libre }}
            </div>

            <hr>
            <!-- Campos restantes del formulario clínico -->
            <div class="mb-3">
              <label for="{{ clinical_form.detalles_alta.id_for_label }}">Detalles de Alta (Antecedentes
                previos)</label>
              {{ clinical_form.detalles_alta }}
            </div>

            <!-- Renderizamos el formulario principal de la Ficha (diagnóstico, etc) -->
            <h6 class="font-weight-bold text-primary mt-4">Datos de la Ficha</h6>
            {{ form.as_p }}

            <button type="submit" class="btn btn-primary btn-block mt-3">
              <i class="fas fa-save"></i> Guardar Ficha y Datos Clínicos
            </button>
            <a href="{% url 'ficha_list' %}" class="btn btn-secondary btn-block">Cancelar</a>
          </form>
        </div>
      </div>
    </div>

    <!-- Columna Derecha: Información de Referencia -->
    <div class="col-md-6">
      <div class="card shadow mb-4">
        <div class="card-header py-3 bg-secondary text-white">
          <h6 class="m-0 font-weight-bold">Resumen del Paciente</h6>
        </div>
        <div class="card-body">
          <p><strong>RUT:</strong> {{ clinical_form.instance.rut }}</p>
          <p><strong>Edad:</strong> {{ clinical_form.instance.edad }} años</p>
          <p><strong>Sexo:</strong> {{ clinical_form.instance.get_sexo_display }}</p>
          <p><strong>Teléfono:</strong> {{ clinical_form.instance.telefono }}</p>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function () {
    const categoriaSelect = document.getElementById('categoriaSelect');
    const alergiaSelect = document.getElementById('alergiaSelect');
    const btnAgregar = document.getElementById('btnAgregarAlergia');
    const pacienteId = "{{ clinical_form.instance.id }}";

    // Cargar alergias al cambiar categoría
    categoriaSelect.addEventListener('change', function () {
      const catId = this.value;
      alergiaSelect.innerHTML = '<option value="">Seleccione Alergia...</option>';
      alergiaSelect.disabled = true;

      if (catId) {
        fetch(`/api/alergias/categoria/${catId}/`)
          .then(response => response.json())
          .then(data => {
            data.forEach(alergia => {
              const option = document.createElement('option');
              option.value = alergia.id;
              option.textContent = alergia.ale_nombre;
              alergiaSelect.appendChild(option);
            });
            alergiaSelect.disabled = false;
          });
      }
    });

    // Agregar Alergia
    btnAgregar.addEventListener('click', function () {
      const alergiaId = alergiaSelect.value;
      const alergiaNombre = alergiaSelect.options[alergiaSelect.selectedIndex]?.text;

      if (alergiaId && pacienteId) {
        fetch('/api/alergias/agregar/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify({
            paciente_id: pacienteId,
            alergia_id: alergiaId
          })
        })
          .then(response => response.json())
          .then(data => {
            if (data.status === 'success') {
              // Agregar badge visualmente
              const lista = document.getElementById('listaAlergias');

              // Remove empty message if exists
              const emptyMsg = document.getElementById('no-alergias-msg');
              if (emptyMsg) emptyMsg.remove();

              // Verificar si ya existe para no duplicar visualmente (aunque el backend lo maneje)
              if (!document.getElementById(`badge-alergia-${alergiaId}`)) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-warning text-dark me-1 mb-1';
                badge.id = `badge-alergia-${alergiaId}`;
                badge.innerHTML = `${alergiaNombre} <i class="fas fa-times ms-1 text-danger cursor-pointer btn-eliminar-alergia" data-paciente-id="${pacienteId}" data-alergia-id="${alergiaId}" style="cursor: pointer;"></i>`;
                lista.appendChild(badge);
              }
              // Resetear selects
              alergiaSelect.value = "";
            } else {
              alert('Error al agregar alergia: ' + data.message);
            }
          });
      }
    });

    // Event delegation para eliminar alergia
    document.getElementById('listaAlergias').addEventListener('click', function (e) {
      if (e.target.classList.contains('btn-eliminar-alergia')) {
        const pacienteId = e.target.dataset.pacienteId;
        const alergiaId = e.target.dataset.alergiaId;
        eliminarAlergia(pacienteId, alergiaId);
      }
    });
  });

  // Función global para eliminar alergia
  function eliminarAlergia(pacienteId, alergiaId) {
    if (confirm('¿Está seguro de eliminar esta alergia?')) {
      fetch('/api/alergias/eliminar/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
          paciente_id: pacienteId,
          alergia_id: alergiaId
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            const badge = document.getElementById(`badge-alergia-${alergiaId}`);
            if (badge) badge.remove();
          } else {
            alert('Error al eliminar alergia: ' + data.message);
          }
        });
    }
  }
</script>
{% endblock %}"""

file_path = os.path.join('templates', 'clinica', 'fichas', 'ficha_form.html')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully wrote to {file_path}")
