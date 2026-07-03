import calendar

class MyCalendar(calendar.Calendar):
    def count_weekday_in_year(self, year, weekday):
        """
        Devuelve el número de ocurrencias del día de la semana (0=lunes, ..., 6=domingo)
        en el año dado.
        """
        count = 0
        for month in range(1, 13):
            # monthdays2calendar devuelve una lista de semanas, cada semana es una lista
            # de tuplas (día, día_semana), donde día=0 significa fuera del mes.
            weeks = self.monthdays2calendar(year, month)
            for week in weeks:
                for day, wd in week:
                    if day != 0 and wd == weekday:
                        count += 1
        return count


# Ejemplo de prueba (descomentar para ejecutar)
if __name__ == "__main__":
    mc = MyCalendar()
    print(mc.count_weekday_in_year(2019, 0))   # Esperado: 52
    print(mc.count_weekday_in_year(2000, 6))   # Esperado: 53