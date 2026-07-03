def liters_100km_to_miles_gallon(liters):
    # 100 km a millas
    miles = 100 / 1.609344
    # Litros a galones
    gallons = liters / 3.785411784
    # Retornar millas por galón
    return miles / gallons

def miles_gallon_to_liters_100km(miles):
    # 1 galón a litros
    liters = 3.785411784
    # Millas a kilómetros
    kilometers = miles * 1.609344
    # Calcular litros por cada 100 km
    return (liters / kilometers) * 100

# Código de prueba
print(liters_100km_to_miles_gallon(3.9))
print(liters_100km_to_miles_gallon(7.5))
print(liters_100km_to_miles_gallon(10.))
print(miles_gallon_to_liters_100km(60.3))
print(miles_gallon_to_liters_100km(31.4))
print(miles_gallon_to_liters_100km(23.5))