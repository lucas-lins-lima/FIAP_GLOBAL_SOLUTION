import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os

class CriticalityClassifier:
    def __init__(self, input_dir='src/data/', output_dir='src/data/'):
        """Classificador de criticidade para áreas afetadas.
        
        Args:
            input_dir (str): Diretório onde os dados de entrada estão armazenados.
            output_dir (str): Diretório onde os resultados serão salvos.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model = None
        self.scaler = None
        
    def classificar_areas(self):
        """Classifica áreas afetadas por criticidade usando K-means.
        
        Returns:
            pandas.DataFrame: DataFrame com as áreas classificadas.
        """
        print("Classificando áreas por criticidade...")
        
        # Carregando dados
        areas_df = pd.read_csv(f'{self.input_dir}areas_afetadas.csv')
        
        # Selecionando features para classificação
        features = ['pessoas_afetadas', 'nivel_agua_cm', 'necessidade_agua', 
                    'necessidade_alimentos', 'necessidade_medicamentos', 
                    'ultimo_abastecimento_horas']
        
        # Normalizando os dados
        self.scaler = StandardScaler()
        areas_scaled = self.scaler.fit_transform(areas_df[features])
        
        # Aplicando K-means para classificar em 3 níveis de criticidade
        self.model = KMeans(n_clusters=3, random_state=42)
        areas_df['criticidade'] = self.model.fit_predict(areas_scaled)
        
        # Definindo níveis de criticidade (0=baixa, 1=média, 2=alta)
        # Analisando os centroides para determinar qual cluster é qual
        centroids = self.model.cluster_centers_
        centroid_scores = np.sum(centroids, axis=1)  # soma simples para determinar gravidade
        cluster_order = np.argsort(centroid_scores)
        
        # Mapeando clusters para níveis de criticidade
        criticidade_map = {
            cluster_order[0]: 'baixa',
            cluster_order[1]: 'média',
            cluster_order[2]: 'alta'
        }
        areas_df['nivel_criticidade'] = areas_df['criticidade'].map(criticidade_map)
        
        # Convertendo criticidade numérica para valores que facilitam a ordenação
        nivel_to_num = {'baixa': 0, 'média': 1, 'alta': 2}
        areas_df['criticidade_num'] = areas_df['nivel_criticidade'].map(nivel_to_num)
        
        # Salvando resultados
        areas_df.to_csv(f'{self.output_dir}areas_afetadas_classificadas.csv', index=False)
        
        # Informações sobre a classificação
        counts = areas_df['nivel_criticidade'].value_counts()
        print(f"Classificação concluída: {counts.get('alta', 0)} áreas de alta criticidade, "
              f"{counts.get('média', 0)} áreas de média criticidade, "
              f"{counts.get('baixa', 0)} áreas de baixa criticidade")
              
        return areas_df

# Exemplo de uso
if __name__ == "__main__":
    classifier = CriticalityClassifier()
    areas_classificadas = classifier.classificar_areas()
    print("Classificação salva em src/data/areas_afetadas_classificadas.csv")
