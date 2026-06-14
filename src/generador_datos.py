import pandas as pd
import numpy as np
import random
from config import ESTADOS_MEXICO, PRIORIDAD_PESOS, DIFICULTAD_PESOS, NUM_EDUCADORES

def generar_educadores():
    """Genera datos realistas de 16 educadores clínicos en México"""
    ciudades_base = [
        ("Ciudad de México", 19.4326, -99.1332),
        ("Guadalajara", 20.6597, -103.3496),
        ("Monterrey", 25.6866, -100.3161),
        ("Puebla", 19.0414, -98.2063),
        ("Querétaro", 20.5888, -100.3899),
        ("León", 21.1236, -101.6805),
        ("Mérida", 20.9671, -89.6237),
        ("Toluca", 19.2826, -99.6557),
        ("San Luis Potosí", 22.1565, -100.9855),
        ("Aguascalientes", 21.8818, -102.2916),
        ("Hermosillo", 29.0729, -110.9559),
        ("Cancún", 21.1619, -86.8515),
        ("Villahermosa", 17.9892, -92.9475),
        ("Chihuahua", 28.6353, -106.0889),
        ("Culiacán", 24.8091, -107.3941),
        ("Morelia", 19.7058, -101.1839)
    ]
    
    educadores = []
    for i in range(NUM_EDUCADORES):
        ciudad, lat, lon = ciudades_base[i]
        educadores.append({
            'id_educador': i + 1,
            'nombre': f"Educador_{i+1}",
            'estado_base': ciudad.split(',')[0] if ',' in ciudad else ciudad,
            'ciudad_base': ciudad,
            'lat_base': lat,
            'lon_base': lon
        })
    return pd.DataFrame(educadores)

def generar_hospitales(n_hospitales=80):
    """Genera hospitales distribuidos en México con datos realistas"""
    hospitales = []
    estados = ESTADOS_MEXICO
    prioridades = ['GROW', 'PROTECT', 'SELECT']
    dificultades = ['Alta', 'Media', 'Baja']
    
    # Coordenadas aproximadas de ciudades clave
    coord_ciudades = {
        "Ciudad de México": (19.4326, -99.1332),
        "Guadalajara": (20.6597, -103.3496),
        "Monterrey": (25.6866, -100.3161),
        "Puebla": (19.0414, -98.2063),
        "Cancún": (21.1619, -86.8515),
        "Mérida": (20.9671, -89.6237),
        "Veracruz": (19.1738, -96.1342),
        "Acapulco": (16.8531, -99.8237),
        "Tijuana": (32.5149, -117.0382),
        "Juárez": (31.6904, -106.4245)
    }
    
    for i in range(n_hospitales):
        # Asignar estado aleatorio
        estado = random.choice(estados)
        
        # Elegir una ciudad conocida o generar nombre
        if random.random() < 0.6:
            ciudad = random.choice(list(coord_ciudades.keys()))
            lat, lon = coord_ciudades[ciudad]
        else:
            ciudad = f"Hospital_{i+1}"
            lat = np.random.uniform(14.5, 32.5)
            lon = np.random.uniform(-118.5, -86.5)
        
        # Añadir pequeña variación a coordenadas
        lat += np.random.uniform(-0.05, 0.05)
        lon += np.random.uniform(-0.05, 0.05)
        
        hospitales.append({
            'id_hospital': i + 1,
            'nombre': f"Hospital_{i+1}",
            'estado': estado,
            'ciudad': ciudad,
            'lat': lat,
            'lon': lon,
            'prioridad': random.choices(prioridades, weights=[0.2, 0.5, 0.3])[0],
            'pacientes_2025': np.random.poisson(lam=15) + 1,
            'dificultad_zona': random.choices(dificultades, weights=[0.3, 0.5, 0.2])[0]
        })
    
    return pd.DataFrame(hospitales)

def asignar_hospitales_educadores(educadores_df, hospitales_df):
    """Asigna hospitales a educadores (uno a muchos)"""
    n_hospitales = len(hospitales_df)
    n_educadores = len(educadores_df)
    
    # Distribución realista: algunos educadores tienen más hospitales
    distribucion = np.random.multinomial(n_hospitales, [1/n_educadores]*n_educadores)
    
    hospitales_asignados = []
    idx_hospitales = list(range(n_hospitales))
    random.shuffle(idx_hospitales)
    
    start = 0
    for i, num in enumerate(distribucion):
        end = start + num
        if end > len(idx_hospitales):
            end = len(idx_hospitales)
        for j in range(start, end):
            idx = idx_hospitales[j]
            hospital = hospitales_df.iloc[idx].to_dict()
            hospital['id_educador'] = i + 1
            hospitales_asignados.append(hospital)
        start = end
        if start >= len(idx_hospitales):
            break
    
    return pd.DataFrame(hospitales_asignados)

def generar_catalogos_auxiliares():
    """Genera catálogos de pesos y parámetros"""
    catalogos = {
        'prioridad': pd.DataFrame(PRIORIDAD_PESOS.items(), columns=['prioridad', 'peso']),
        'dificultad': pd.DataFrame(DIFICULTAD_PESOS.items(), columns=['dificultad', 'peso'])
    }
    return catalogos

if __name__ == "__main__":
    educadores = generar_educadores()
    hospitales = generar_hospitales(80)
    hospitales_asignados = asignar_hospitales_educadores(educadores, hospitales)
    catalogos = generar_catalogos_auxiliares()
    
    educadores.to_csv('data/raw/educadores.csv', index=False)
    hospitales_asignados.to_csv('data/raw/hospitales.csv', index=False)
    catalogos['prioridad'].to_csv('data/raw/catalogos_auxiliares_prioridad.csv', index=False)
    catalogos['dificultad'].to_csv('data/raw/catalogos_auxiliares_dificultad.csv', index=False)
    
    print("Datos generados y guardados en data/raw/")