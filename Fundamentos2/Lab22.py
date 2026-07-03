import os

def find(path, dir_name):
    """
    Busca recursivamente todos los directorios con nombre `dir_name` dentro de `path`.
    Imprime las rutas absolutas de cada uno.
    """
    # Convertir a ruta absoluta para salida limpia
    path_abs = os.path.abspath(path)

    for root, dirs, files in os.walk(path_abs):
        # Verificar si el directorio actual (root) tiene el nombre buscado
        if os.path.basename(root) == dir_name:
            print(root)
        # También se puede buscar en los subdirectorios, pero os.walk ya los recorre

# Ejemplo de uso (descomentar para probar)
# find("../tree", "python")