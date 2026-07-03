texto = "hola mundo desde python"
frecuencia = {}

for caracter in texto:
    if caracter != " ":
        frecuencia[caracter] = frecuencia.get(caracter, 0) + 1

# Ordenamos el diccionario por sus valores (los conteos) de mayor a menor
# sorted() nos devuelve una lista de tuplas ordenadas
frecuencia_ordenada = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)

print("--- Histograma Ordenado (Mayor a Menor) ---")
for letra, conteo in frecuencia_ordenada:
    print(f"Letra '{letra}': {conteo} veces")