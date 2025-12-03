import os
import django
import random
from datetime import date

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_pacientes.settings')
django.setup()

from django.contrib.auth.models import User
from principal.models import PersonalSalud
from clinica.models import CentroSalud, Area, Paciente, IngresoPaciente, AsignacionClinica

def create_users():
    print("Creando usuarios y personal de salud...")
    
    # Crear Superusuario
    if not User.objects.filter(username='adm').exists():
        User.objects.create_superuser('adm', 'adm@saludmaule.cl', 'adm2025')
        print("Superusuario 'adm' creado.")
    else:
        print("Superusuario 'adm' ya existe.")

    users_data = [
        {
            'username': 'doctor',
            'password': 'doctor2025',
            'cargo': 'medico',
            'rut': '11111111-1',
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'email': 'doctor@saludmaule.cl'
        },
        {
            'username': 'pingreso',
            'password': 'pingreso2025',
            'cargo': 'administrativo_ingreso',
            'rut': '22222222-2',
            'nombres': 'María',
            'apellidos': 'González',
            'email': 'ingreso@saludmaule.cl'
        },
        {
            'username': 'director',
            'password': 'director2025',
            'cargo': 'director',
            'rut': '33333333-3',
            'nombres': 'Carlos',
            'apellidos': 'Rodríguez',
            'email': 'director@saludmaule.cl'
        }
    ]

    for data in users_data:
        user, created = User.objects.get_or_create(username=data['username'])
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"Usuario {data['username']} creado.")
        else:
            print(f"Usuario {data['username']} ya existe.")

        if not hasattr(user, 'perfil_salud'):
            PersonalSalud.objects.create(
                usuario=user,
                rut=data['rut'],
                nombres=data['nombres'],
                apellidos=data['apellidos'],
                correo_institucional=data['email'],
                cargo=data['cargo']
            )
            print(f"Perfil de salud para {data['username']} creado.")
        else:
            print(f"Perfil de salud para {data['username']} ya existe.")

def create_doctors_for_areas(areas):
    print("\nCreando doctores por área...")
    for i, area in enumerate(areas, 1):
        username = f"doctor{i}"
        password = f"doctor{i}2025"
        rut = f"{10000000 + i}-{(i % 9) + 1}"
        email = f"doctor{i}@saludmaule.cl"
        nombres = f"Doctor {area.nombre}"
        apellidos = f"Area {area.centro.nombre}"
        
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            print(f"Usuario {username} creado.")
        
        if not hasattr(user, 'perfil_salud'):
            personal = PersonalSalud.objects.create(
                usuario=user,
                rut=rut,
                nombres=nombres,
                apellidos=apellidos,
                correo_institucional=email,
                cargo='medico'
            )
            
            # Asignar al área
            AsignacionClinica.objects.create(
                personal=personal,
                centro=area.centro,
                area=area,
                activo=True
            )
            print(f"  - Asignado a {area.nombre} ({area.centro.nombre})")

def create_centers_and_areas():
    print("\nCreando centros y áreas...")
    centros_data = [
        {
            'nombre': 'Hospital Regional',
            'tipo': 'hospital',
            'ciudad': 'Talca',
            'areas': [
                'UCI', 'Hospitalización', 'Urgencias', 'Parto',
                'Laboratorio', 'Banco de sangre', 'Imagenología', 'Sala de espera'
            ]
        },
        {
            'nombre': 'CESFAM Norte',
            'tipo': 'cesfam',
            'ciudad': 'Talca',
            'areas': [
                'Banco de sangre', 'Odontología', 'Sala de espera'
            ]
        }
    ]

    created_areas = []

    for c_data in centros_data:
        centro, created = CentroSalud.objects.get_or_create(
            nombre=c_data['nombre'],
            defaults={'tipo': c_data['tipo'], 'ciudad': c_data['ciudad']}
        )
        if created:
            print(f"Centro {centro.nombre} creado.")
        else:
            print(f"Centro {centro.nombre} ya existe.")

        for area_nombre in c_data['areas']:
            area, a_created = Area.objects.get_or_create(
                centro=centro,
                nombre=area_nombre
            )
            created_areas.append(area)
            if a_created:
                print(f"  - Área {area.nombre} creada.")
    
    return created_areas

def create_patients_and_admissions(areas):
    print("\nCreando pacientes y admisiones...")
    if not areas:
        print("No hay áreas disponibles para ingresar pacientes.")
        return

    nombres_lista = ['Ana', 'Luis', 'Pedro', 'Carmen', 'Diego', 'Sofia', 'Lucia', 'Miguel', 'Javier', 'Elena']
    apellidos_lista = ['Silva', 'Rojas', 'Molina', 'Castro', 'Ortiz', 'Morales', 'López', 'Diaz', 'Romero', 'Torres']

    for i in range(10):
        rut = f"{15000000 + i}-{(i % 9) + 1}"
        nombre = nombres_lista[i % len(nombres_lista)]
        apellido = apellidos_lista[i % len(apellidos_lista)]
        
        paciente, created = Paciente.objects.get_or_create(
            rut=rut,
            defaults={
                'nombres': nombre,
                'apellidos': apellido,
                'correo': f"{nombre.lower()}.{apellido.lower()}@saludmaule.cl",
                'telefono': f"+5691111111{i}",
                'sexo': 'M' if i % 2 == 0 else 'F',
                'fecha_nacimiento': date(1980 + i, 1, 1),
                'user_estado': 1
            }
        )
        
        if created:
            print(f"Paciente {paciente} creado.")
        else:
            print(f"Paciente {paciente} ya existe.")

        # Crear ingreso si no tiene uno activo
        if not IngresoPaciente.objects.filter(paciente=paciente, activo=True).exists():
            area_destino = random.choice(areas)
            IngresoPaciente.objects.create(
                paciente=paciente,
                centro=area_destino.centro,
                area=area_destino,
                estado='tratamiento',
                activo=True
            )
            print(f"  - Ingresado a {area_destino.centro.nombre} - {area_destino.nombre}")
        else:
            print(f"  - Ya tiene ingreso activo.")

def assign_static_doctor(areas):
    print("\nAsignando doctor estático (Juan Pérez)...")
    try:
        user = User.objects.get(username='doctor')
        personal = user.perfil_salud
        
        # Assign to first area (usually UCI or similar from Hospital Regional)
        if areas:
            area = areas[0]
            if not AsignacionClinica.objects.filter(personal=personal, activo=True).exists():
                AsignacionClinica.objects.create(
                    personal=personal,
                    centro=area.centro,
                    area=area,
                    activo=True
                )
                print(f"  - Doctor Juan Pérez asignado a {area.nombre} ({area.centro.nombre})")
            else:
                print("  - Doctor Juan Pérez ya tiene asignación.")
    except User.DoesNotExist:
        print("  - Usuario 'doctor' no encontrado.")

if __name__ == '__main__':
    create_users()
    areas = create_centers_and_areas()
    assign_static_doctor(areas)
    create_doctors_for_areas(areas)
    create_patients_and_admissions(areas)
    print("\nSemilla ejecutada correctamente.")
