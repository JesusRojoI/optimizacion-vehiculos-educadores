import requests
import pandas as pd
import numpy as np
from tqdm import tqdm

class CalculadorRutas:
    def __init__(self, use_osrm=True):
        self.use_osrm = use_osrm
        self.cache = {}
    
    def obtener_ruta_osrm(self, origen_lat, origen_lon, dest_lat, dest_lon):
        """Consulta OSRM para obtener distancia (metros) y tiempo (segundos)"""
        key = (origen_lat, origen_lon, dest_lat, dest_lon)
        if key in self.cache:
            return self.cache[key]
        
        if not self.use_osrm:
            # Simular distancia y tiempo
            distancia_km = np.sqrt((origen_lat - dest_lat)**2 + (origen_lon - dest_lon)**2) * 100
            tiempo_seg = distancia_km * 60  # 60 seg por km
            self.cache[key] = (distancia_km * 1000, tiempo_seg)
            return self.cache[key]
        
        # Consulta real a OSRM (público, respetar límites)
        url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(
            origen_lon, origen_lat, dest_lon, dest_lat
        )
        try:
            response = requests.get(url, params={'overview': 'false'})
            if response.status_code == 200:
                data = response.json()
                distancia = data['routes'][0]['distance']
                tiempo = data['routes'][0]['duration']
                self.cache[key] = (distancia, tiempo)
                return distancia, tiempo
        except:
            pass
        
        # Fallback a simulación aa
        distancia_km = np.sqrt((origen_lat - dest_lat)**2 + (origen_lon - dest_lon)**2) * 111
        tiempo_seg = distancia_km * 3600 / 60  # 60 km/h promedio
        self.cache[key] = (distancia_km * 1000, tiempo_seg)
        return self.cache[key]
    
    def construir_matriz_costos(self, educadores_df, hospitales_df):
        """Construye matriz distancia/tiempo entre educadores y sus hospitales"""
        matriz = []
        
        for _, educador in tqdm(educadores_df.iterrows(), total=len(educadores_df), desc="Calculando rutas"):
            for _, hospital in hospitales_df.iterrows():
                if hospital['id_educador'] == educador['id_educador']:
                    distancia, tiempo = self.obtener_ruta_osrm(
                        educador['lat_base'], educador['lon_base'],
                        hospital['lat'], hospital['lon']
                    )
                    matriz.append({
                        'id_educador': educador['id_educador'],
                        'id_hospital': hospital['id_hospital'],
                        'distancia_m': distancia,
                        'tiempo_seg': tiempo
                    })
        
        return pd.DataFrame(matriz)

if __name__ == "__main__":
    educadores = pd.read_csv('data/raw/educadores.csv')
    hospitales = pd.read_csv('data/raw/hospitales.csv')
    
    calc = CalculadorRutas(use_osrm=False)  # False para simular rápido
    matriz = calc.construir_matriz_costos(educadores, hospitales)
    matriz.to_csv('data/processed/matriz_distancias_tiempos.csv', index=False)
    print("Matriz de costos guardada")