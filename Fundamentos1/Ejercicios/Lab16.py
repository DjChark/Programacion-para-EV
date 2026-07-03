my_list = [1, 2, 4, 4, 1, 4, 2, 6, 2, 9]

temp_list = [] # Lista temporal para guardar los valores únicos

# Iterar sobre la lista original
for number in my_list:
    # Si el número no está en la lista temporal, lo agregamos
    if number not in temp_list:
        temp_list.append(number)

# Reemplazar la lista original con la lista filtrada
my_list = temp_list

print("La lista con elementos únicos:")
print(my_list)