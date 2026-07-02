# Creación de un diccionario sobre un artículo tecnológico
producto = {
    "nombre": "Teclado  RGB",
    "precio": 700.00,
    "stock": 15,
    "disponible": True
}

# 1. Leer un valor usando su clave
print(f"Producto: {producto['nombre']}")
print(f"Precio original: ${producto['precio']}")

# 2. Modificar un valor existente (Aplicar un descuento del 10%)
producto["precio"] = producto["precio"] * 0.10
print(f"Precio con descuento: ${producto['precio']}")

# 3. Agregar una nueva clave-valor al diccionario
producto["marca"] = "Temu"

# 4. Recorrer todo el diccionario para ver sus componentes
print("\n--- Ficha Técnica Completa ---")
for clave, valor in producto.items():
    print(f"{clave.capitalize()}: {valor}")