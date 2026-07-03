def is_year_leap(year):
    # Si no es divisible entre 4, no es bisiesto
    if year % 4 != 0:
        return False
    # Si es divisible entre 4 y no entre 100, es bisiesto
    elif year % 100 != 0:
        return True
    # Si es divisible entre 100 pero no entre 400, no es bisiesto
    elif year % 400 != 0:
        return False
    # Si es divisible entre 400, es bisiesto
    else:
        return True

# Código de prueba proporcionado por el laboratorio
test_data = [1900, 2001, 2016, 1987]
test_results = [False, True, True, False]
for i in range(len(test_data)):
    yr = test_data[i]
    print(yr,"->",end="")
    result = is_year_leap(yr)
    if result == test_results[i]:
        print("OK")
    else:
        print("Falló")