from datetime import datetime

# 1. Creamos el objeto datetime con la fecha y hora específica solicitada
fecha = datetime(2026, 6, 4, 16, 00, 0)

# 2. Imprimimos usando las directivas strftime requeridas
print(fecha.strftime("%Y/%m/%d %H:%M:%S"))
print(fecha.strftime("%y/%B/%d %H:%M:%S %p"))
print(fecha.strftime("%a, %Y %b %d"))
print(fecha.strftime("%A, %Y %B %d"))
print(fecha.strftime("Día de la semana: %w"))
print(fecha.strftime("Día del año: %j"))
print(fecha.strftime("Número de semana en el año: %W"))