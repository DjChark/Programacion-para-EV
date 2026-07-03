import random

def mostrar_tablero(tablero):
    # Dibuja el tablero en la consola de manera similar al ejemplo del curso
    print("+-------+-------+-------+")
    print(f"|   {tablero[0]}   |   {tablero[1]}   |   {tablero[2]}   |")
    print("+-------+-------+-------+")
    print(f"|   {tablero[3]}   |   {tablero[4]}   |   {tablero[5]}   |")
    print("+-------+-------+-------+")
    print(f"|   {tablero[6]}   |   {tablero[7]}   |   {tablero[8]}   |")
    print("+-------+-------+-------+")

def movimiento_usuario(tablero):
    # Pide el movimiento al usuario y lo valida
    while True:
        try:
            movimiento = int(input("Ingresa tu movimiento (1-9): "))
            if movimiento < 1 or movimiento > 9:
                print("¡Error! Debes ingresar un número entre 1 y 9.")
            elif tablero[movimiento - 1] in ['X', 'O']:
                print("¡Esa casilla ya está ocupada! Intenta otra.")
            else:
                tablero[movimiento - 1] = 'O'
                break
        except ValueError:
            print("Por favor, introduce un número válido.")

def movimiento_maquina(tablero):
    # La máquina elije una casilla libre al azar
    casillas_libres = [i for i in range(9) if tablero[i] not in ['X', 'O']]
    if casillas_libres:
        movimiento = random.choice(casillas_libres)
        tablero[movimiento] = 'X'
        print(f"La máquina ha elegido la casilla: {movimiento + 1}")

def verificar_ganador(tablero, jugador):
    # Combinaciones ganadoras posibles
    lineas_ganadoras = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontales
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Verticales
        [0, 4, 8], [2, 4, 6]              # Diagonales
    ]
    for linea in lineas_ganadoras:
        if tablero[linea[0]] == tablero[linea[1]] == tablero[linea[2]] == jugador:
            return True
    return False

def juego_principal():
    # Inicializamos el tablero con los números del 1 al 9
    tablero = [str(i) for i in range(1, 10)]
    
    print("¡Bienvenido al proyecto Tic-Tac-Toe de Python!")
    
    # REGLA CLAVE (image_7f155e.png): La máquina empieza y siempre pone 'X' en el centro (casilla 5, índice 4)
    tablero[4] = 'X'
    
    while True:
        mostrar_tablero(tablero)
        
        # 1. Turno del Usuario ('O')
        movimiento_usuario(tablero)
        if verificar_ganador(tablero, 'O'):
            mostrar_tablero(tablero)
            print("¡Felicidades! Has ganado el juego.")
            break
            
        # Verificar si hay empate
        if all(casilla in ['X', 'O'] for casilla in tablero):
            mostrar_tablero(tablero)
            print("¡Es un empate!")
            break
            
        # 2. Turno de la Máquina ('X')
        movimiento_maquina(tablero)
        if verificar_ganador(tablero, 'X'):
            mostrar_tablero(tablero)
            print("La máquina ha ganado. ¡Suerte la próxima vez!")
            break
            
        # Verificar si hay empate después del turno de la máquina
        if all(casilla in ['X', 'O'] for casilla in tablero):
            mostrar_tablero(tablero)
            print("¡Es un empate!")
            break

# Ejecutar el juego
if __name__ == "__main__":
    juego_principal()