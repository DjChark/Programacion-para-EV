# Nivel 1: La clase más general (Abuelo)
class Persona:
    def __init__(self, nombre):
        self.nombre = nombre

    def respirar(self):
        print(f"{self.nombre} está chambeando.")

# Nivel 2: La clase intermedia (Padre)
class Empleado(Persona):
    def __init__(self, nombre, sueldo):
        # super() llama al constructor de la clase superior (Persona)
        super().__init__(nombre) 
        self.sueldo = sueldo

    def cobrar(self):
        print(f"{self.nombre} recibió su sueldo de ${self.sueldo}.")

# Nivel 3: La clase más específica (Hijo)
class Cocinero(Empleado):
    def preparar_comida(self):
        print(f"{self.nombre} está preparando un platillo.")

# El objeto de nivel más bajo de la jerarquía
chef = Cocinero("Luis", 5000)

# Demostración de la jerarquía:
chef.respirar()        # Método heredado del Nivel 1 (Persona)
chef.cobrar()          # Método heredado del Nivel 2 (Empleado)
chef.preparar_comida() # Método propio del Nivel 3 (Cocinero)