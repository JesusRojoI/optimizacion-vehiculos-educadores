import numpy as np
import random
import pandas as pd
from config import NUM_EDUCADORES, NUM_VEHICULOS, TAMANO_POBLACION, GENERACIONES, TASA_MUTACION, TASA_CRUZAMIENTO, TORNEO_SIZE, ELITISMO

class AlgoritmoGenetico:
    def __init__(self, scores_df):
        self.scores = scores_df.set_index('id_educador')['ScoreNecesidad'].to_dict()
        self.num_educadores = NUM_EDUCADORES
        self.num_vehiculos = NUM_VEHICULOS
        self.tam_poblacion = TAMANO_POBLACION
        self.generaciones = GENERACIONES
        self.tasa_mutacion = TASA_MUTACION
        self.tasa_cruzamiento = TASA_CRUZAMIENTO
        self.torneo_size = TORNEO_SIZE
        self.elitismo = ELITISMO
    
    def crear_individuo(self):
        """Crea un cromosoma con exactamente num_vehiculos = 1"""
        individuo = [0] * self.num_educadores
        indices = random.sample(range(self.num_educadores), self.num_vehiculos)
        for i in indices:
            individuo[i] = 1
        return individuo
    
    def crear_poblacion(self):
        return [self.crear_individuo() for _ in range(self.tam_poblacion)]
    
    def fitness(self, individuo):
        """Calcula fitness sumando scores de educadores seleccionados"""
        total = 0
        for i, val in enumerate(individuo):
            if val == 1:
                total += self.scores.get(i+1, 0)  # id_educador = índice+1
        return total
    
    def seleccion_torneo(self, poblacion, fitnesses):
        """Selecciona padres mediante torneo"""
        seleccionados = []
        for _ in range(2):
            participantes = random.sample(list(zip(poblacion, fitnesses)), self.torneo_size)
            mejor = max(participantes, key=lambda x: x[1])
            seleccionados.append(mejor[0])
        return seleccionados[0], seleccionados[1]
    
    def cruzar(self, padre1, padre2):
        """Cruzamiento de un punto con reparación"""
        if random.random() > self.tasa_cruzamiento:
            return padre1.copy(), padre2.copy()
        
        punto = random.randint(1, self.num_educadores-1)
        hijo1 = padre1[:punto] + padre2[punto:]
        hijo2 = padre2[:punto] + padre1[punto:]
        
        # Reparación: asegurar exactamente num_vehiculos = 1
        hijo1 = self.reparar(hijo1)
        hijo2 = self.reparar(hijo2)
        return hijo1, hijo2
    
    def reparar(self, individuo):
        """Repara cromosoma para tener exactamente num_vehiculos = 1"""
        num_1 = sum(individuo)
        if num_1 == self.num_vehiculos:
            return individuo
        elif num_1 > self.num_vehiculos:
            # Eliminar unos de más
            indices_1 = [i for i, val in enumerate(individuo) if val == 1]
            eliminar = random.sample(indices_1, num_1 - self.num_vehiculos)
            nuevo = individuo.copy()
            for i in eliminar:
                nuevo[i] = 0
            return nuevo
        else:
            # Agregar unos faltantes
            indices_0 = [i for i, val in enumerate(individuo) if val == 0]
            agregar = random.sample(indices_0, self.num_vehiculos - num_1)
            nuevo = individuo.copy()
            for i in agregar:
                nuevo[i] = 1
            return nuevo
    
    def mutar(self, individuo):
        """Mutación por intercambio de un 1 y un 0"""
        if random.random() > self.tasa_mutacion:
            return individuo
        
        indices_1 = [i for i, val in enumerate(individuo) if val == 1]
        indices_0 = [i for i, val in enumerate(individuo) if val == 0]
        
        if indices_1 and indices_0:
            i1 = random.choice(indices_1)
            i0 = random.choice(indices_0)
            nuevo = individuo.copy()
            nuevo[i1] = 0
            nuevo[i0] = 1
            return nuevo
        return individuo
    
    def evolucionar(self):
        """Ejecuta el algoritmo genético"""
        poblacion = self.crear_poblacion()
        mejor_fitness_historial = []
        
        for gen in range(self.generaciones):
            # Evaluar fitness
            fitnesses = [self.fitness(ind) for ind in poblacion]
            mejor_idx = np.argmax(fitnesses)
            mejor_fitness = fitnesses[mejor_idx]
            mejor_fitness_historial.append(mejor_fitness)
            
            nueva_poblacion = []
            
            # Elitismo
            if self.elitismo:
                nueva_poblacion.append(poblacion[mejor_idx])
            
            # Generar hijos
            while len(nueva_poblacion) < self.tam_poblacion:
                padre1, padre2 = self.seleccion_torneo(poblacion, fitnesses)
                hijo1, hijo2 = self.cruzar(padre1, padre2)
                hijo1 = self.mutar(hijo1)
                hijo2 = self.mutar(hijo2)
                nueva_poblacion.extend([hijo1, hijo2])
            
            poblacion = nueva_poblacion[:self.tam_poblacion]
        
        # Mejor solución final
        fitnesses_final = [self.fitness(ind) for ind in poblacion]
        mejor_idx_final = np.argmax(fitnesses_final)
        mejor_solucion = poblacion[mejor_idx_final]
        mejor_fitness_final = fitnesses_final[mejor_idx_final]
        
        return mejor_solucion, mejor_fitness_final, mejor_fitness_historial

if __name__ == "__main__":
    scores = pd.read_csv('data/processed/scores_educadores.csv')
    ag = AlgoritmoGenetico(scores)
    mejor, fitness, historial = ag.evolucionar()
    
    seleccionados = [i+1 for i, val in enumerate(mejor) if val == 1]
    print(f"Mejor fitness: {fitness}")
    print(f"Educadores seleccionados: {seleccionados}")
    
    pd.DataFrame({'generacion': range(len(historial)), 'mejor_fitness': historial}).to_csv('data/resultados/evolucion_fitness.csv', index=False)