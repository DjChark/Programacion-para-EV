# Lee archivo con nombre, apellido y nota; suma por estudiante y genera informe ordenado.

nombre_archivo = input("Introduce el nombre del archivo: ")

try:
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
except FileNotFoundError:
    print("Archivo no encontrado.")
    exit()

# Diccionario con clave (nombre, apellido) -> suma de puntos
sumas = {}
for linea in lineas:
    partes = linea.strip().split()
    if len(partes) < 3:
        continue   # línea mal formada
    nombre, apellido, nota_str = partes[0], partes[1], partes[2]
    try:
        nota = float(nota_str)
    except ValueError:
        continue
    clave = (nombre, apellido)
    sumas[clave] = sumas.get(clave, 0.0) + nota

# Ordenar por nombre (y luego apellido) alfabéticamente
estudiantes_ordenados = sorted(sumas.keys(), key=lambda x: (x[0], x[1]))

# Mostrar informe
for nombre, apellido in estudiantes_ordenados:
    print(f"{nombre} {apellido} {sumas[(nombre, apellido)]:.1f}")