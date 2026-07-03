from datetime import datetime

# Crear el objeto datetime para el 4 de noviembre de 2020, 14:53:00
dt = datetime(2020, 11, 4, 14, 53, 0)

# Mostrar en los formatos solicitados
print(dt.strftime("%Y/%m/%d %H:%M:%S"))
print(dt.strftime("%y/%B/%d %H:%M:%S %p"))
print(dt.strftime("%a, %Y %b %d"))
print(dt.strftime("%A, %Y %B %d"))
print(f"Día de la semana: {dt.isoweekday()}")          # 3 (miércoles según ISO)
print(f"Día del año: {dt.timetuple().tm_yday}")        # 309
print(f"Número de semana en el año: {dt.strftime('%U')}")  # 44 (semana con domingo como primer día)