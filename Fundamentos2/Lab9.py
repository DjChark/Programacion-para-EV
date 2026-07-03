text = input("Ingresa una línea de texto para encriptar: ")

# Bucle para asegurar un cambio válido
while True:
    try:
        shift = int(input("Ingresa un valor de cambio (1..25): "))
        if 1 <= shift <= 25:
            break
        print("¡El valor de cambio debe estar entre 1 y 25!")
    except ValueError:
        print("Por favor, ingresa un número entero válido.")

cipher = ""

for char in text:
    # Solo encriptar letras
    if char.isalpha():
        code = ord(char) + shift
        # Verificación para mayúsculas
        if char.isupper():
            if code > ord('Z'):
                code -= 26
        # Verificación para minúsculas
        else:
            if code > ord('z'):
                code -= 26
        cipher += chr(code)
    else:
        # Los números o caracteres especiales se pasan igual
        cipher += char

print(cipher)