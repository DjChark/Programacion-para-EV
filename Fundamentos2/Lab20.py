# Similar al anterior, pero ordenado por frecuencia descendente y escribiendo en archivo .hist

import os

nombre_entrada = input("Introduce el nombre del archivo: ")

try:
    with open(nombre_entrada, 'r', encoding='utf-8') as f:
        texto = f.read()
except FileNotFoundError:
    print("Archivo no encontrado.")
    exit()

conteo = {}
for letra in texto.lower():
    if 'a' <= letra <= 'z':
        conteo[letra] = conteo.get(letra, 0) + 1

# Ordenar por frecuencia descendente (y alfabéticamente para iguales)
items_ordenados = sorted(conteo.items(), key=lambda x: (-x[1], x[0]))

# Nombre de salida: mismo nombre base + .hist
base, _ = os.path.splitext(nombre_entrada)
nombre_salida = base + ".hist"

with open(nombre_salida, 'w', encoding='utf-8') as salida:
    for letra, cant in items_ordenados:
        salida.write(f"{letra} -> {cant}\n")

print(f"Histograma guardado en {nombre_salida}")