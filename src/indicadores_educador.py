import pandas as pd
import numpy as np
from config import PESOS, PRIORIDAD_PESOS, DIFICULTAD_PESOS

class IndicadoresEducador:
    def __init__(self, hospitales_df, matriz_costos_df, catalogos):
        self.hospitales = hospitales_df
        self.matriz_costos = matriz_costos_df
        self.catalogos = catalogos
    
    def calcular_indicadores(self, educador_id):
        """Calcula todos los indicadores para un educador"""
        hospitales_educador = self.hospitales[self.hospitales['id_educador'] == educador_id]
        costos_educador = self.matriz_costos[self.matriz_costos['id_educador'] == educador_id]
        
        if len(hospitales_educador) == 0:
            return None
        
        # 1. Cuentas asignadas
        cuentas = len(hospitales_educador)
        
        # 2. Pacientes 2025
        pacientes = hospitales_educador['pacientes_2025'].sum()
        
        # 3. Prioridad comercial ponderada
        prioridad_peso_map = dict(zip(self.catalogos['prioridad']['prioridad'], self.catalogos['prioridad']['peso']))
        hospitales_educador['peso_prioridad'] = hospitales_educador['prioridad'].map(prioridad_peso_map)
        prioridad_prom = hospitales_educador['peso_prioridad'].mean()
        
        # 4. Distancia acumulada (km)
        distancia_km = costos_educador['distancia_m'].sum() / 1000
        
        # 5. Tiempo acumulado (horas)
        tiempo_horas = costos_educador['tiempo_seg'].sum() / 3600
        
        # 6. Dificultad de zona ponderada
        dificultad_map = dict(zip(self.catalogos['dificultad']['dificultad'], self.catalogos['dificultad']['peso']))
        hospitales_educador['peso_dificultad'] = hospitales_educador['dificultad_zona'].map(dificultad_map)
        dificultad_prom = hospitales_educador['peso_dificultad'].mean()
        
        # 7. Cuentas fuera del estado base
        educador = pd.read_csv('data/raw/educadores.csv')
        estado_base = educador[educador['id_educador'] == educador_id]['estado_base'].values[0]
        cuentas_fuera = len(hospitales_educador[hospitales_educador['estado'] != estado_base])
        
        # 8. Dispersión geográfica (desviación estándar de coordenadas)
        if len(hospitales_educador) > 1:
            dispersion_lat = hospitales_educador['lat'].std()
            dispersion_lon = hospitales_educador['lon'].std()
            dispersion = np.sqrt(dispersion_lat**2 + dispersion_lon**2) * 111  # km aprox
        else:
            dispersion = 0
        
        return {
            'id_educador': educador_id,
            'cuentas': cuentas,
            'pacientes': pacientes,
            'prioridad_prom': prioridad_prom,
            'distancia_km': distancia_km,
            'tiempo_horas': tiempo_horas,
            'dificultad_prom': dificultad_prom,
            'cuentas_fuera_estado': cuentas_fuera,
            'dispersion_km': dispersion
        }
    
    def calcular_todos_indicadores(self):
        """Calcula indicadores para todos los educadores"""
        todos = []
        for edu in range(1, 17):
            ind = self.calcular_indicadores(edu)
            if ind:
                todos.append(ind)
        return pd.DataFrame(todos)
    
    def normalizar_y_score(self, indicadores_df):
        """Normaliza variables y calcula ScoreNecesidad"""
        df = indicadores_df.copy()
        
        # Normalización Min-Max por columna
        columnas_norm = ['cuentas', 'pacientes', 'prioridad_prom', 'distancia_km', 
                         'tiempo_horas', 'dificultad_prom', 'cuentas_fuera_estado', 'dispersion_km']
        
        for col in columnas_norm:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df[col + '_norm'] = (df[col] - min_val) / (max_val - min_val)
            else:
                df[col + '_norm'] = 0
        
        # Calcular Score Necesidad con ponderación
        df['ScoreNecesidad'] = (
            df['cuentas_norm'] * PESOS['cuentas'] +
            df['pacientes_norm'] * PESOS['pacientes'] +
            df['prioridad_prom_norm'] * PESOS['prioridad'] +
            df['distancia_km_norm'] * PESOS['distancia'] +
            df['tiempo_horas_norm'] * PESOS['tiempo'] +
            df['dificultad_prom_norm'] * PESOS['dificultad'] +
            df['cuentas_fuera_estado_norm'] * PESOS['cuentas_fuera_estado']
        )
        
        return df.sort_values('ScoreNecesidad', ascending=False)

if __name__ == "__main__":
    hospitales = pd.read_csv('data/raw/hospitales.csv')
    matriz = pd.read_csv('data/processed/matriz_distancias_tiempos.csv')
    prioridad = pd.read_csv('data/raw/catalogos_auxiliares_prioridad.csv')
    dificultad = pd.read_csv('data/raw/catalogos_auxiliares_dificultad.csv')
    catalogos = {'prioridad': prioridad, 'dificultad': dificultad}
    
    indicador = IndicadoresEducador(hospitales, matriz, catalogos)
    indicadores_df = indicador.calcular_todos_indicadores()
    scores_df = indicador.normalizar_y_score(indicadores_df)
    
    scores_df.to_csv('data/processed/scores_educadores.csv', index=False)
    print("Scores de necesidad calculados")
    print(scores_df[['id_educador', 'ScoreNecesidad']].head())