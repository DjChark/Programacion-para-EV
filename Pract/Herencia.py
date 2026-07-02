class Empleado:
    def __init__(self, nombre):
        self.nombre = nombre
        
    def presentarse(self):
        print(f"Hola, soy {self.nombre}.")
        
class Cocinero(Empleado):
    def cocinar(self):
        print(f"{self.nombre} esta preparando un Menudo.")
        
chef = Cocinero("Angel")
chef.presentarse()
chef.cocinar()
    