blocks = int(input("Ingresa el número de bloques: "))

height = 0
layer_blocks = 1 # Bloques necesarios para la capa actual

# Mientras los bloques disponibles sean mayores o iguales a los que requiere la capa
while blocks >= layer_blocks:
    blocks -= layer_blocks # Restamos los bloques utilizados
    height += 1            # Aumentamos la altura completada
    layer_blocks += 1      # La siguiente capa requerirá un bloque extra

print("La altura de la pirámide es:", height)