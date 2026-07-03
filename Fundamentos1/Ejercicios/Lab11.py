hora = int(input("Hora de inicio (horas): "))
minuto = int(input("Minuto de inicio (minutos): "))
duracion = int(input("Duración del evento (minutos): "))

# Calcular el total de minutos sumando los minutos iniciales y la duración
minutos_totales = minuto + duracion

# Calcular los minutos finales (el residuo de dividir entre 60)
minuto_final = minutos_totales % 60

# Calcular las horas extra generadas por los minutos
horas_extra = minutos_totales // 60

# Calcular la hora final asegurando el formato de 24 horas (0-23)
hora_final = (hora + horas_extra) % 24

# Imprimir el resultado sin espacios utilizando concatenación o sep=""
print(str(hora_final) + ":" + str(minuto_final))