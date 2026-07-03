text1 = input("Ingresa el primer texto: ")
text2 = input("Ingresa el segundo texto: ")

# Limpiar las cadenas: sin espacios y todo a minúsculas
clean_text1 = text1.replace(" ", "").lower()
clean_text2 = text2.replace(" ", "").lower()

# Si alguna cadena está vacía tras limpiar, no son anagramas
if len(clean_text1) == 0 or len(clean_text2) == 0:
    print("No son anagramas")
# Al ordenar los caracteres de ambas cadenas, deben ser idénticos
elif sorted(clean_text1) == sorted(clean_text2):
    print("Anagramas")
else:
    print("No son anagramas")