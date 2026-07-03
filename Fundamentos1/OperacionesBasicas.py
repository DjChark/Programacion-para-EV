# Entrada: Pedir datos al usuario
nombre = input("¿Cuál es tu nombre? ")
horas_estudio = input("¿Cuántas horas estudiaste hoy?: ")

# Conversión: Transformamos el texto de las horas a un número entero
horas_enteras = int(horas_estudio)

# Operación matemática básica
horas_semanales_estimadas = horas_enteras * 7

# Salida: Mostrar los resultados usando f-strings para formatear el texto
print("\n--- RESUMEN ---")
print(f"¡Hola, {nombre}!")
print(f"Si sigues estudiando {horas_enteras} horas al día, en una semana acumularás {horas_semanales_estimadas} horas. ¡Buen ritmo!")