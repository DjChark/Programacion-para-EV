# Patrones de los dígitos del 0 al 9 (cada uno tiene 5 filas)
digits = [
    ["###", "# #", "# #", "# #", "###"], # 0
    ["  #", "  #", "  #", "  #", "  #"], # 1
    ["###", "  #", "###", "#  ", "###"], # 2
    ["###", "  #", "###", "  #", "###"], # 3
    ["# #", "# #", "###", "  #", "  #"], # 4
    ["###", "#  ", "###", "  #", "###"], # 5
    ["###", "#  ", "###", "# #", "###"], # 6
    ["###", "  #", "  #", "  #", "  #"], # 7
    ["###", "# #", "###", "# #", "###"], # 8
    ["###", "# #", "###", "  #", "###"]  # 9
]

# Pedimos el número como cadena para poder iterar sobre sus dígitos
num_str = input("Ingresa un número entero no negativo: ")

# Imprimimos línea por línea (de la 0 a la 4)
for row in range(5):
    line = ""
    for char in num_str:
        digit = int(char)
        # Añadimos la fila correspondiente del dígito actual, separando por espacios
        line += digits[digit][row] + "  "
    print(line)