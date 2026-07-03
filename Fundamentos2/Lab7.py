def mysplit(strng):
    # Si la cadena está vacía o contiene puros espacios, regresamos lista vacía
    if strng == "" or strng.isspace():
        return []
    
    words = []
    word = ""
    
    for char in strng:
        if char != " ":
            word += char # Construimos la palabra letra por letra
        else:
            if word != "": # Al encontrar un espacio, guardamos la palabra si no está vacía
                words.append(word)
                word = ""
                
    # Agregar la última palabra si la cadena no terminó en espacio
    if word != "":
        words.append(word)
        
    return words

# Código de prueba
print(mysplit("Ser o no ser, esa es la pregunta"))
print(mysplit("Ser o no ser, esa es la pregunta")) # Equivalente con diferentes espacios
print(mysplit("   "))
print(mysplit(" abc "))
print(mysplit(""))