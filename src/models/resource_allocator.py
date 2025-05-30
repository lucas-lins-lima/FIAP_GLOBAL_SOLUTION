import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict
import os

class ResourceAllocator:
    def __init__(self, input_dir='src/data/', output_dir='src/data/'):
        """Otimizador de alocação de recursos para ajuda humanitária.
        
        Args:
            input_dir (str): Diretório onde os dados de entrada estão armazenados.
            output_dir (str): Diretório onde os resultados serão salvos.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.G = None
        
    def alocar_recursos(self):
        """Aloca recursos para áreas afetadas otimizando rotas e prioridades.
        
        Returns:
            list: Lista de planos de alocação para cada área.
        """
        print("Iniciando alocação otimizada de recursos...")
        
        # Carregando dados necessários
        self.G = nx.read_gpickle(f"{self.input_dir}rede_logistica.gpickle")
        areas_df = pd.read_csv(f'{self.input_dir}areas_afetadas_classificadas.csv')
        centros_df = pd.read_csv(f'{self.input_dir}centros_distribuicao.csv')
        
        # Ordenar áreas por criticidade e pessoas afetadas
        # Usamos criticidade_num se disponível, senão tentamos mapear diretamente
        if 'criticidade_num' in areas_df.columns:
            areas_ordenadas = areas_df.sort_values(
                by=['criticidade_num', 'pessoas_afetadas'], 
                ascending=[False, False]
            )
        else:
            # Tentar mapear criticidade para valores numéricos
            criticidade_map = {'alta': 2, 'média': 1, 'baixa': 0, np.nan: -1}
            areas_df['criticidade_temp'] = areas_df['nivel_criticidade'].map(criticidade_map)
            areas_ordenadas = areas_df.sort_values(
                by=['criticidade_temp', 'pessoas_afetadas'], 
                ascending=[False, False]
            )
        
        # Recursos disponíveis por centro
        recursos_centros = {}
        for _, centro in centros_df.iterrows():
            centro_id = f"C{centro['id']}"
            recursos_centros[centro_id] = {
                'agua': centro['estoque_agua'],
                'alimentos': centro['estoque_alimentos'],
                'medicamentos': centro['estoque_medicamentos'],
                'veiculos': centro['capacidade_veiculos']
            }
        
        # Plano de alocação
        plano_alocacao = []
        
        # Para cada área, encontrar o melhor centro e planejar a entrega
        for _, area in areas_ordenadas.iterrows():
            area_id = f"A{area['id']}"
            necessidades = {
                'agua': area['necessidade_agua'],
                'alimentos': area['necessidade_alimentos'],
                'medicamentos': area['necessidade_medicamentos']
            }
            
            # Encontrar centro mais próximo com recursos suficientes
            melhor_centro = None
            melhor_rota = None
            menor_tempo = float('inf')
            
            for centro_id, recursos in recursos_centros.items():
                if recursos['veiculos'] <= 0:
                    continue  # Pula centros sem veículos disponíveis
                    
                # Verificar se o centro tem pelo menos 50% dos recursos necessários
                recursos_suficientes = all(
                    recursos[tipo] >= necessidades[tipo] * 0.5 
                    for tipo in necessidades
                )
                
                if not recursos_suficientes:
                    continue
                    
                # Calcular rota mais rápida do centro para a área
                try:
                    rota = nx.shortest_path(self.G, centro_id, area_id, weight='weight')
                    tempo = sum(self.G[rota[i]][rota[i+1]]['weight'] for i in range(len(rota)-1))
                    
                    if tempo < menor_tempo:
                        menor_tempo = tempo
                        melhor_centro = centro_id
                        melhor_rota = rota
                except nx.NetworkXNoPath:
                    continue  # Sem caminho disponível
            
            # Se encontrou uma rota viável
            if melhor_centro and melhor_rota:
                # Calcular recursos a enviar (limitado pelo disponível)
                recursos_enviados = {}
                for tipo, quantidade in necessidades.items():
                    disponivel = recursos_centros[melhor_centro][tipo]
                    recursos_enviados[tipo] = min(quantidade, disponivel)
                    # Atualizar estoque do centro
                    recursos_centros[melhor_centro][tipo] -= recursos_enviados[tipo]
                
                # Atualizar veículos disponíveis
                recursos_centros[melhor_centro]['veiculos'] -= 1
                
                # Adicionar ao plano
                plano_alocacao.append({
                    'centro_origem': melhor_centro,
                    'area_destino': area_id,
                    'criticidade': area.get('nivel_criticidade', 'não classificada'),
                    'pessoas_atendidas': area['pessoas_afetadas'],
                    'recursos': recursos_enviados,
                    'rota': melhor_rota,
                    'tempo_estimado_min': menor_tempo
                })
        
        # Salvar o plano em formato CSV para fácil visualização
        plano_df = pd.DataFrame([
            {
                'centro_origem': p['centro_origem'],
                'area_destino': p['area_destino'],
                'criticidade': p['criticidade'],
                'pessoas_atendidas': p['pessoas_atendidas'],
                'agua': p['recursos']['agua'],
                'alimentos': p['recursos']['alimentos'],
                'medicamentos': p['recursos']['medicamentos'],
                'tempo_estimado_min': p['tempo_estimado_min'],
                'rota': '->'.join(p['rota'])
            }
            for p in plano_alocacao
        ])
        plano_df.to_csv(f'{self.output_dir}plano_logistico.csv', index=False)
        
        print(f"Plano logístico gerado para {len(plano_alocacao)} áreas afetadas")
        return plano_alocacao
    
    def exibir_resumo_plano(self, plano):
        """Exibe um resumo do plano de alocação gerado.
        
        Args:
            plano (list): Lista com o plano de alocação.
        """
        print("\nResumo do plano de alocação:")
        for i, p in enumerate(plano[:5], 1):  # Mostrar primeiras 5 entregas
            print(f"\nEntrega {i}:")
            print(f"  Centro: {p['centro_origem']} → Área: {p['area_destino']} (Criticidade: {p['criticidade']})")
            print(f"  Recursos: Água: {p['recursos']['agua']}, Alimentos: {p['recursos']['alimentos']}, Medicamentos: {p['recursos']['medicamentos']}")
            print(f"  Rota: {' → '.join(p['rota'])}")
            print(f"  Tempo estimado: {p['tempo_estimado_min']:.1f} minutos")

# Exemplo de uso
if __name__ == "__main__":
    allocator = ResourceAllocator()
    plano = allocator.alocar_recursos()
    allocator.exibir_resumo_plano(plano)
