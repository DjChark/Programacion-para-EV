# Importamos el módulo 'pyplot' de la librería matplotlib y le damos el alias 'plt'
import matplotlib.pyplot as plt

# Datos para la gráfica (Meses y Ventas simuladas)
meses = ["Ene", "Feb", "Mar", "Abr", "May"]
ventas = [10, 15, 7, 22, 18]

# Crear la gráfica de línea
plt.plot(meses, ventas, marker="o", color="b", linestyle="--")

# Personalizar con títulos y etiquetas
plt.title("Ventas del Segundo Semestre")
plt.xlabel("Meses")
plt.ylabel("Unidades en Venta")

# Mostrar la gráfica en una ventana emergente
plt.show()