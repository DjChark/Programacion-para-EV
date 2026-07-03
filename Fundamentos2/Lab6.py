import calendar

# 1. Creamos nuestra clase heredando de la clase original Calendar
class MyCalendar(calendar.Calendar):
    
    # 2. Definimos el nuevo método solicitado
    def count_weekday_in_year(self, year, weekday):
        contador = 0
        
        # Iteramos por los 12 meses del año
        for mes in range(1, 13):
            # monthdays2calendar devuelve semanas; cada semana tiene parejas de (día_del_mes, número_de_día_semana)
            semanas_del_mes = self.monthdays2calendar(year, mes)
            
            for semana in semanas_del_mes:
                for dia_del_mes, dia_semana in semana:
                    # El día 0 significa que ese cuadro del calendario está vacío (pertenece a otro mes)
                    # Si el día no es 0 y coincide con el día de la semana que buscamos (0 a 6), sumamos 1
                    if dia_del_mes != 0 and dia_semana == weekday:
                        contador += 1
                        
        return contador

# Pruebas de ejecución
mi_calendario = MyCalendar()

# ¿Cuántos lunes (0) hubo en 2019?
print(mi_calendario.count_weekday_in_year(2019, 0)) # Salida esperada: 52

# ¿Cuántos domingos (6) hubo en 2000?
print(mi_calendario.count_weekday_in_year(2000, 6)) # Salida esperada: 53