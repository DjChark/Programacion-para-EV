# Importamos la librería y le asignamos el alias 'plt' por convención
import matplotlib.pyplot as plt

# 1. Preparamos los datos
platillos = ['Ceviche', 'Filete Empanizado', 'Coctel de Camarón', 'Aguachile']
ventas_fin_de_semana = [45, 30, 55, 25]

# 2. Construimos la gráfica de barras
plt.bar(platillos, ventas_fin_de_semana, color=['#3498db', '#e67e22', '#e74c3c', '#2ecc71'])

# 3. Personalizamos el diseño
plt.title("Ventas de Fin de Semana - Marisquería Don Camarón")
plt.xlabel("Tipo de Platillo")
plt.ylabel("Cantidad Vendida")

# 4. Renderizamos la ventana
plt.show()