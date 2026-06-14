# config.py
# Parámetros del modelo
NUM_EDUCADORES = 16
NUM_VEHICULOS = 6
PESOS = {
    'cuentas': 0.15,
    'pacientes': 0.20,
    'prioridad': 0.20,
    'distancia': 0.15,
    'tiempo': 0.10,
    'dificultad': 0.10,
    'cuentas_fuera_estado': 0.10
}

# Parámetros del algoritmo genético
TAMANO_POBLACION = 50
GENERACIONES = 100
TASA_MUTACION = 0.1
TASA_CRUZAMIENTO = 0.8
TORNEO_SIZE = 3
ELITISMO = True

# Datos geográficos
ESTADOS_MEXICO = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
    "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato",
    "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán", "Morelos",
    "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
    "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala",
    "Veracruz", "Yucatán", "Zacatecas", "Ciudad de México"
]

# Prioridades comerciales
PRIORIDAD_PESOS = {'GROW': 3, 'PROTECT': 2, 'SELECT': 1}
DIFICULTAD_PESOS = {'Alta': 3, 'Media': 2, 'Baja': 1}