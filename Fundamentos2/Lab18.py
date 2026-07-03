class WeekDayError(Exception):
    pass


class Weeker:
    __days = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

    def __init__(self, day):
        if day not in Weeker.__days:
            raise WeekDayError("Día inválido")
        self.__day = Weeker.__days.index(day)   # almacenamos índice (0-6)

    def __str__(self):
        return Weeker.__days[self.__day]

    def add_days(self, n):
        self.__day = (self.__day + n) % 7

    def subtract_days(self, n):
        self.__day = (self.__day - n) % 7


# Código de prueba (salida esperada: Lun, Mar, Dom, "Lo siento, no puedo atender tu solicitud.")
try:
    weekday = Weeker("Lun")
    print(weekday)
    weekday.add_days(1)
    print(weekday)
    weekday.subtract_days(23)
    print(weekday)
    weekday = Weeker("Lunes")   # inválido
except WeekDayError:
    print("Lo siento, no puedo atender tu solicitud.")