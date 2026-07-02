class Empleado:
    def __init__(self, nombre):
        self.nombre = nombre

    def presentarse(self):
        print(f"Hola, soy {self.nombre}.")

class Cocinero:
    def __init__(self, nombre):
        # Se repete este código
        self.nombre = nombre 

    def presentarse(self):
        # Se repite este método también
        print(f"Hola, soy {self.nombre}.")

    def preparar_platillo(self):
        print(f"{self.nombre} está preparando un ceviche.")

# Creando los objetos
mesero = Empleado("Carlos")
chef = Cocinero("Luis")

mesero.presentarse()
chef.presentarse()
chef.preparar_platillo()