import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_pacientes.settings')
django.setup()

from clinica.models import CategoriaAlergia, Alergia

def seed_allergies():
    data = {
        'Medicamentos': [
            'Penicilina', 'Sulfamidas', 'Aspirina', 'Ibuprofeno', 'Codeína', 
            'Morfina', 'Anestesia Local', 'Contrastes Yodados'
        ],
        'Alimentos': [
            'Maní', 'Nueces', 'Leche', 'Huevos', 'Pescado', 'Mariscos', 
            'Trigo', 'Soya', 'Frutillas', 'Kiwi'
        ],
        'Ambientales': [
            'Polen', 'Ácaros del polvo', 'Moho', 'Caspa de animales', 
            'Picaduras de insectos (Abejas/Avispas)', 'Látex'
        ],
        'Otras': [
            'Níquel', 'Cromo', 'Cobalto', 'Tintes de cabello', 'Protectores solares'
        ]
    }

    print("Iniciando carga de alergias...")

    for categoria_nombre, alergias_lista in data.items():
        categoria, created = CategoriaAlergia.objects.get_or_create(nombre_categoria=categoria_nombre)
        if created:
            print(f"Categoría creada: {categoria_nombre}")
        else:
            print(f"Categoría existente: {categoria_nombre}")

        for alergia_nombre in alergias_lista:
            alergia, created = Alergia.objects.get_or_create(
                ale_nombre=alergia_nombre,
                categoria=categoria
            )
            if created:
                print(f"  - Alergia creada: {alergia_nombre}")
            else:
                print(f"  - Alergia existente: {alergia_nombre}")

    print("Carga de alergias finalizada exitosamente.")

if __name__ == '__main__':
    seed_allergies()
