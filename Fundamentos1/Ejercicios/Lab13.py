word_without_vowels = ""

# Pedir al usuario que ingrese una palabra y convertirla a mayúsculas
user_word = input("Ingresa una palabra: ")
user_word = user_word.upper()

for letter in user_word:
    # Condición para "devorar" (saltar) las vocales
    if letter in "AEIOU":
        continue
    # Concatenar las letras no consumidas
    word_without_vowels += letter

# Imprimir la palabra sin vocales
print(word_without_vowels)