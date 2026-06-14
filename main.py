import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. Generar datos si no existen
from src import generador_datos
from src import calculo_rutas
from src import indicadores_educador
from src import algoritmo_genetico
from src import visualizador_resultados
import pandas as pd

def main():
    print("=== OPTIMIZACIÓN DE ASIGNACIÓN DE VEHÍCULOS PARA EDUCADORES CLÍNICOS ===\n")
    
    # Verificar existencia de datos o generarlos
    if not os.path.exists('data/raw/educadores.csv'):
        print("📁 Generando datos sintéticos realistas...")
        generador_datos.main()
    
    if not os.path.exists('data/processed/matriz_distancias_tiempos.csv'):
        print("🗺️ Calculando matriz de distancias y tiempos...")
        educadores = pd.read_csv('data/raw/educadores.csv')
        hospitales = pd.read_csv('data/raw/hospitales.csv')
        calc = calculo_rutas.CalculadorRutas(use_osrm=False)
        matriz = calc.construir_matriz_costos(educadores, hospitales)
        matriz.to_csv('data/processed/matriz_distancias_tiempos.csv', index=False)
    
    if not os.path.exists('data/processed/scores_educadores.csv'):
        print("📊 Calculando indicadores y scores de necesidad...")
        hospitales = pd.read_csv('data/raw/hospitales.csv')
        matriz = pd.read_csv('data/processed/matriz_distancias_tiempos.csv')
        prioridad = pd.read_csv('data/raw/catalogos_auxiliares_prioridad.csv')
        dificultad = pd.read_csv('data/raw/catalogos_auxiliares_dificultad.csv')
        catalogos = {'prioridad': prioridad, 'dificultad': dificultad}
        ind = indicadores_educador.IndicadoresEducador(hospitales, matriz, catalogos)
        indicadores_df = ind.calcular_todos_indicadores()
        scores_df = ind.normalizar_y_score(indicadores_df)
        scores_df.to_csv('data/processed/scores_educadores.csv', index=False)
    
    # Cargar scores
    scores = pd.read_csv('data/processed/scores_educadores.csv')
    print("\n📈 Scores de necesidad por educador:")
    print(scores[['id_educador', 'ScoreNecesidad']].to_string(index=False))
    
    # Ejecutar algoritmo genético
    print("\n🧬 Ejecutando algoritmo genético...")
    ag = algoritmo_genetico.AlgoritmoGenetico(scores)
    mejor_solucion, mejor_fitness, historial = ag.evolucionar()
    
    seleccionados = [i+1 for i, val in enumerate(mejor_solucion) if val == 1]
    print(f"\n✅ Mejor fitness alcanzado: {mejor_fitness:.4f}")
    print(f"🚗 Educadores seleccionados para vehículo: {seleccionados}")
    
    # Visualización y reporte
    educadores_df = pd.read_csv('data/raw/educadores.csv')
    vis = visualizador_resultados.Visualizador(scores, seleccionados)
    vis.reporte_ejecutivo()
    vis.ranking_educadores()
    vis.mapa_geografico(educadores_df)
    
    # Guardar resultados
    resultados = scores.copy()
    resultados['seleccionado'] = resultados['id_educador'].isin(seleccionados)
    resultados.to_csv('data/resultados/ranking_educadores.csv', index=False)
    vis.justificacion_seleccion().to_csv('data/resultados/mejor_seleccion.csv', index=False)
    
    print("\n✨ Resultados guardados en data/resultados/")
    print("📄 Archivos generados: ranking_educadores.csv, mejor_seleccion.csv, evolucion_fitness.csv, mapa_educadores.html")

if __name__ == "__main__":
    main()