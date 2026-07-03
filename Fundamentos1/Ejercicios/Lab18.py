def is_prime(num):
    # Los números menores o iguales a 1 no son primos
    if num <= 1:
        return False
    # Verificamos divisores desde 2 hasta la raíz cuadrada del número
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

# Código de prueba
for i in range(1, 20):
    if is_prime(i + 1):
        print(i + 1, end=" ")
print()