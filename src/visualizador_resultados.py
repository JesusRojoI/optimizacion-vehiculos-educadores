import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from config import ESTADOS_MEXICO

class Visualizador:
    def __init__(self, scores_df, mejor_seleccion):
        self.scores = scores_df
        self.seleccion = mejor_seleccion
        self.scores['seleccionado'] = self.scores['id_educador'].isin(mejor_seleccion)
    
    def ranking_educadores(self):
        """Genera ranking visual"""
        plt.figure(figsize=(12, 6))
        colores = ['green' if x else 'lightgray' for x in self.scores['seleccionado']]
        sns.barplot(data=self.scores, x='id_educador', y='ScoreNecesidad', palette=colores)
        plt.title('Ranking de necesidad de vehículo por educador')
        plt.xlabel('ID Educador')
        plt.ylabel('Score Necesidad')
        plt.axhline(y=self.scores['ScoreNecesidad'].quantile(0.6), color='red', linestyle='--', label='Corte selección')
        plt.legend()
        plt.savefig('data/resultados/ranking_educadores.png')
        plt.show()
    
    def justificacion_seleccion(self):
        """Tabla justificativa"""
        justif = self.scores[self.scores['seleccionado']].copy()
        columnas_mostrar = ['id_educador', 'cuentas', 'pacientes', 'prioridad_prom', 
                            'distancia_km', 'tiempo_horas', 'dificultad_prom', 
                            'cuentas_fuera_estado', 'dispersion_km', 'ScoreNecesidad']
        return justif[columnas_mostrar].round(2)
    
    def mapa_geografico(self, educadores_df):
        """Mapa con educadores seleccionados"""
        mapa = folium.Map(location=[23.6345, -102.5528], zoom_start=5)
        
        # Educadores seleccionados
        selec_data = educadores_df[educadores_df['id_educador'].isin(self.seleccion)]
        for _, row in selec_data.iterrows():
            folium.Marker(
                [row['lat_base'], row['lon_base']],
                popup=f"Educador {row['id_educador']} - {row['ciudad_base']} (Seleccionado)",
                icon=folium.Icon(color='green', icon='car')
            ).add_to(mapa)
        
        # Educadores no seleccionados
        no_selec = educadores_df[~educadores_df['id_educador'].isin(self.seleccion)]
        for _, row in no_selec.iterrows():
            folium.Marker(
                [row['lat_base'], row['lon_base']],
                popup=f"Educador {row['id_educador']} - {row['ciudad_base']}",
                icon=folium.Icon(color='gray', icon='user')
            ).add_to(mapa)
        
        mapa.save('data/resultados/mapa_educadores.html')
        return mapa
    
    def reporte_ejecutivo(self):
        """Reporte en consola"""
        print("\n" + "="*60)
        print("RECOMENDACIÓN DE ASIGNACIÓN DE VEHÍCULOS")
        print("="*60)
        print(f"\n🎯 Educadores seleccionados (6 de 16): {sorted(self.seleccion)}")
        print(f"\n📊 Score total de necesidad cubierta: {self.scores[self.scores['seleccionado']]['ScoreNecesidad'].sum():.2f}")
        print("\n📋 Justificación por educador:")
        print(self.justificacion_seleccion().to_string(index=False))
        print("\n✅ Criterio basado en: Cuentas, Pacientes, Prioridad Comercial, Distancia, Tiempo, Dificultad y Movilidad interestatal")
        print("="*60)

if __name__ == "__main__":
    scores = pd.read_csv('data/processed/scores_educadores.csv')
    mejor_seleccion = [2, 5, 7, 9, 12, 15]  # Ejemplo
    vis = Visualizador(scores, mejor_seleccion)
    vis.ranking_educadores()
    print(vis.justificacion_seleccion())