import pandas as pd
import numpy as np
import random
import os

class DataGenerator:
    def __init__(self, output_dir='src/data/'):
        """Inicializa o gerador de dados simulados para o cenário pós-desastre.
        
        Args:
            output_dir (str): Diretório onde os arquivos CSV serão salvos.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def criar_dados_areas(self, num_areas=15):
        """Cria dados simulados para áreas afetadas por desastres.
        
        Args:
            num_areas (int): Número de áreas afetadas a serem geradas.
            
        Returns:
            pandas.DataFrame: DataFrame com os dados gerados.
        """
        areas = []
        for i in range(1, num_areas + 1):
            areas.append({
                'id': i,
                'nome': f'Área {i}',
                'latitude': round(random.uniform(-23.5, -23.7), 6),
                'longitude': round(random.uniform(-46.6, -46.8), 6),
                'pessoas_afetadas': random.randint(50, 500),
                'nivel_agua_cm': random.randint(0, 200),
                'necessidade_agua': random.randint(100, 1000),
                'necessidade_alimentos': random.randint(100, 1000),
                'necessidade_medicamentos': random.randint(50, 500),
                'ultimo_abastecimento_horas': random.randint(6, 72)
            })
        df = pd.DataFrame(areas)
        df.to_csv(f'{self.output_dir}areas_afetadas.csv', index=False)
        return df

    def criar_dados_rotas(self, num_areas=15):
        """Cria dados simulados para rotas entre áreas afetadas.
        
        Args:
            num_areas (int): Número de áreas para gerar conexões.
            
        Returns:
            pandas.DataFrame: DataFrame com os dados de rotas.
        """
        rotas = []
        for i in range(1, num_areas + 1):
            for j in range(i+1, num_areas + 1):
                if random.random() < 0.4:  # 40% de chance de haver uma rota direta
                    distancia = random.randint(5, 30)
                    rotas.append({
                        'origem': i,
                        'destino': j,
                        'distancia_km': distancia,
                        'tempo_percurso_min': distancia * random.randint(2, 4),
                        'status': random.choice(['bloqueada', 'parcial', 'livre'])
                    })
        df = pd.DataFrame(rotas)
        df.to_csv(f'{self.output_dir}rotas.csv', index=False)
        return df
        
    def criar_dados_centros(self, num_centros=5):
        """Cria dados simulados para centros de distribuição.
        
        Args:
            num_centros (int): Número de centros de distribuição.
            
        Returns:
            pandas.DataFrame: DataFrame com os dados dos centros.
        """
        centros = []
        for i in range(1, num_centros + 1):
            centros.append({
                'id': i,
                'nome': f'Centro {i}',
                'latitude': round(random.uniform(-23.5, -23.7), 6),
                'longitude': round(random.uniform(-46.6, -46.8), 6),
                'estoque_agua': random.randint(1000, 5000),
                'estoque_alimentos': random.randint(1000, 5000),
                'estoque_medicamentos': random.randint(500, 2000),
                'capacidade_veiculos': random.randint(3, 10)
            })
        df = pd.DataFrame(centros)
        df.to_csv(f'{self.output_dir}centros_distribuicao.csv', index=False)
        return df
        
    def gerar_todos_dados(self):
        """Gera todos os conjuntos de dados simulados."""
        print("Gerando dados simulados para o cenário pós-desastre...")
        areas_df = self.criar_dados_areas()
        rotas_df = self.criar_dados_rotas()
        centros_df = self.criar_dados_centros()
        print(f"Dados gerados com sucesso! {len(areas_df)} áreas, {len(rotas_df)} rotas, {len(centros_df)} centros.")
        return {
            'areas': areas_df,
            'rotas': rotas_df,
            'centros': centros_df
        }

# Exemplo de uso
if __name__ == "__main__":
    generator = DataGenerator()
    dados = generator.gerar_todos_dados()
    print("Arquivos CSV salvos no diretório src/data/")
