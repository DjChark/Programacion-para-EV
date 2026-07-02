# Clase independiente que ofrece un servicio
class Licuadora:
    def encender(self):
        print("Licuando a máxima potencia... ¡Bzzzz!")

# Clase principal
class Cocinero:
    def __init__(self, nombre):
        self.nombre = nombre

    # Aquí ocurre la DEPENDENCIA. El método recibe un objeto externo.
    def preparar_salsa(self, herramienta):
        print(f"{self.nombre} está preparando una salsa para el aguachile.")
        herramienta.encender()  # Usa el objeto que le pasaron

# 1. SE crean los objetos por separado
licuadora_industrial = Licuadora()
chef = Cocinero("Angel")

# 2. El chef usa (depende de) la licuadora en este momento específico
chef.preparar_salsa(licuadora_industrial)