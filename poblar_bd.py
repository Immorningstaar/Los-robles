import os
import django

# 1. Conectar el script con las configuraciones del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'los_robles.settings')
django.setup()

# Importar los modelos
from gestion.models import Residente, Medicamento

def poblar():
    print("Iniciando la inyección de datos médicos... ")

    # 2. Catálogo de Medicamentos de uso común en adultos mayores
    medicamentos_data = [
        {"nombre_comercial": "Tapsin", "nombre_generico": "Paracetamol", "miligramos": 500, "presentacion": "Comprimidos"},
        {"nombre_comercial": "Glafornil", "nombre_generico": "Metformina", "miligramos": 850, "presentacion": "Comprimidos"},
        {"nombre_comercial": "Cozaar", "nombre_generico": "Losartán", "miligramos": 50, "presentacion": "Comprimidos"},
        {"nombre_comercial": "Losec", "nombre_generico": "Omeprazol", "miligramos": 20, "presentacion": "Cápsulas"},
        {"nombre_comercial": "Eutirox", "nombre_generico": "Levotiroxina", "miligramos": 100, "presentacion": "Comprimidos"},
        {"nombre_comercial": "Aspirina", "nombre_generico": "Ácido Acetilsalicílico", "miligramos": 100, "presentacion": "Comprimidos"},
    ]

    # Usamos get_or_create para evitar duplicados si corremos el script dos veces
    for med in medicamentos_data:
        Medicamento.objects.get_or_create(**med)
    print(f" Se cargaron {len(medicamentos_data)} medicamentos en el catálogo.")

    # 3. Residentes de prueba
    residentes_data = [
        {"rut": "11222333-4", "nombre": "Carmen", "apellido": "Salinas", "habitacion_numero": 101, "alertas_criticas": "Alérgica a la Penicilina y derivados."},
        {"rut": "22333444-5", "nombre": "Pedro", "apellido": "Cáceres", "habitacion_numero": 102, "alertas_criticas": "Hipertensión severa. Monitoreo constante."},
        {"rut": "33444555-6", "nombre": "Marta", "apellido": "Villanueva", "habitacion_numero": 103, "alertas_criticas": ""},
    ]

    for res in residentes_data:
        Residente.objects.get_or_create(**res)
    print(f" Se registraron {len(residentes_data)} residentes de prueba.")

    print("¡Base de datos poblada con éxito!")

if __name__ == '__main__':
    poblar()