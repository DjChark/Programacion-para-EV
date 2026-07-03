import os

def find(path, dir):
    # Intentamos acceder al directorio (usamos try/except por si hay carpetas sin permiso de lectura)
    try:
        # Listamos todo lo que hay dentro de la ruta actual
        for elemento in os.listdir(path):
            # Creamos la ruta completa uniendo la ruta actual y el nombre del elemento
            ruta_actual = os.path.join(path, elemento)
            
            # Verificamos si este elemento es una carpeta (directorio)
            if os.path.isdir(ruta_actual):
                # Si el nombre de la carpeta coincide con lo que buscamos, imprimimos su ruta absoluta
                if elemento == dir:
                    print(os.path.abspath(ruta_actual))
                
                # RECURSIÓN: Llamamos a la misma función para que busque dentro de esta nueva carpeta
                find(ruta_actual, dir)
    except PermissionError:
        pass # Si no tenemos permisos, simplemente ignoramos esa carpeta

# Prueba de ejecución (ajusta el path inicial según donde estés ejecutando)
print("Buscando el directorio 'python'...")
find(".", "python")