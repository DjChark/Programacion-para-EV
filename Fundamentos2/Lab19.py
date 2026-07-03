# Solicita el nombre del archivo, cuenta letras latinas (mayúsculas/minúsculas igual) e imprime histograma alfabético.

nombre_archivo = input("Introduce el nombre del archivo: ")

try:
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        texto = f.read()
except FileNotFoundError:
    print("Archivo no encontrado.")
    exit()

# Contar solo letras del alfabeto latino (a-z)
conteo = {}
for letra in texto.lower():
    if 'a' <= letra <= 'z':
        conteo[letra] = conteo.get(letra, 0) + 1

# Imprimir en orden alfabético solo las que aparecen
for letra in sorted(conteo.keys()):
    print(f"{letra} -> {conteo[letra]}")