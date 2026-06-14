import pandas as pd
import requests
import time

class Georreferenciador:
    def __init__(self, use_api=False):
        self.use_api = use_api
        self.cache = {}
    
    def obtener_coordenadas_lugar(self, lugar):
        """Obtiene coordenadas usando Nominatim (solo si es necesario)"""
        if lugar in self.cache:
            return self.cache[lugar]
        
        if not self.use_api:
            return None
        
        # Simular o usar API con respeto a política de uso
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': lugar, 'format': 'json', 'limit': 1}
        try:
            response = requests.get(url, params=params, headers={'User-Agent': 'OptimizacionVehiculos/1.0'})
            time.sleep(1)  # Respetar política de uso
            if response.status_code == 200:
                data = response.json()
                if data:
                    coords = (float(data[0]['lat']), float(data[0]['lon']))
                    self.cache[lugar] = coords
                    return coords
        except:
            pass
        return None
    
    def geocodificar_dataframe(self, df, col_ciudad='ciudad', col_lat='lat', col_lon='lon'):
        """Verifica o completa coordenadas faltantes"""
        for idx, row in df.iterrows():
            if pd.isna(row[col_lat]) or pd.isna(row[col_lon]):
                if col_ciudad in row:
                    coords = self.obtener_coordenadas_lugar(row[col_ciudad])
                    if coords:
                        df.at[idx, col_lat] = coords[0]
                        df.at[idx, col_lon] = coords[1]
        return df