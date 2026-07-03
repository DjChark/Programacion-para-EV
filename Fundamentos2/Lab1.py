# Texto de prueba (puedes cambiarlo por el que quieras)
texto = "hola mundo desde python"

frecuencia = {}

# Recorremos cada carácter del texto
for caracter in texto:
    # Ignoramos los espacios en blanco para limpiar el histograma
    if caracter != " ":
        # Si ya existe, le suma 1; si no existe, lo crea iniciando en 0 y le suma 1
        frecuencia[caracter] = frecuencia.get(caracter, 0) + 1

# Imprimimos el resultado de forma clara
print("--- Soy Leyenda cuatro ---")
for letra, conteo in frecuencia.items():
    print(f"Letra '{letra}': {conteo} veces")