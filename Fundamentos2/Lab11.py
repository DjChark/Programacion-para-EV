def read_int(prompt, min, max):
    # Ciclo infinito hasta que el usuario ingrese un valor válido
    while True:
        try:
            # Intentar convertir la entrada en entero
            value = int(input(prompt))
            # Verificar rango
            if min <= value <= max:
                return value
            else:
                print(f"Error: el valor no está dentro del rango permitido ({min}..{max})")
        except ValueError:
            # Atrapar si el usuario ingresa letras u otros caracteres
            print("Error: entrada incorrecta")

# Código de prueba
v = read_int("Ingresa un número entre -10 a 10: ", -10, 10)
print("El número es:", v)