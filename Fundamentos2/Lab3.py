# Lista de registros simulando la lectura de un archivo de notas
notas_estudiantes = [
    {"nombre": "Luis", "nota": 90},
    {"nombre": "Angel", "nota": 85},
    {"nombre": "Chuy", "nota": 100},
    {"nombre": "Migue", "nota": 95},
    {"nombre": "Pedro", "nota": 80}
]

# Diccionario para agrupar las notas por alumno
registro = {}

for registro_alumno in notas_estudiantes:
    nombre = registro_alumno["nombre"]
    nota = registro_alumno["nota"]
    
    # Si el alumno no existe en el registro, le creamos una lista vacía
    if nombre not in registro:
        registro[nombre] = []
    # Agregamos la nota a su lista
    registro[nombre].append(nota)

print("--- Promedios Finales de Estudiantes ---")
# Calculamos el promedio para cada estudiante
for nombre, notas in registro.items():
    promedio = sum(notas) / len(notas)
    print(f"Estudiante: {nombre} -> Promedio: {promedio:.1f}")