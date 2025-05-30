import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os

class RouteNetwork:
    def __init__(self, input_dir='src/data/', output_dir='src/data/'):
        """Modelagem da rede de rotas para logística humanitária.
        
        Args:
            input_dir (str): Diretório onde os dados de entrada estão armazenados.
            output_dir (str): Diretório onde os resultados serão salvos.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.G = None
        self.visualization_dir = 'src/visualization/'
        os.makedirs(self.visualization_dir, exist_ok=True)
        
    def criar_rede(self):
        """Cria o grafo da rede logística.
        
        Returns:
            networkx.Graph: Grafo representando a rede logística.
        """
        print("Criando rede de rotas para logística humanitária...")
        
        # Carregando dados
        areas_df = pd.read_csv(f'{self.input_dir}areas_afetadas_classificadas.csv')
        rotas_df = pd.read_csv(f'{self.input_dir}rotas.csv')
        centros_df = pd.read_csv(f'{self.input_dir}centros_distribuicao.csv')
        
        # Criando o grafo
        G = nx.Graph()
        
        # Adicionando nós (áreas afetadas e centros de distribuição)
        for _, area in areas_df.iterrows():
            G.add_node(f"A{area['id']}", 
                      pos=(area['longitude'], area['latitude']),
                      tipo='area',
                      criticidade=area.get('nivel_criticidade', 'não classificada'),
                      pessoas=area['pessoas_afetadas'])
        
        for _, centro in centros_df.iterrows():
            G.add_node(f"C{centro['id']}", 
                      pos=(centro['longitude'], centro['latitude']),
                      tipo='centro',
                      capacidade=centro['capacidade_veiculos'])
        
        # Adicionando arestas (rotas)
        for _, rota in rotas_df.iterrows():
            if rota['status'] != 'bloqueada':  # Só adicionamos rotas não bloqueadas
                # Fator de peso - rotas parciais são mais "custosas"
                peso = rota['tempo_percurso_min'] * (2 if rota['status'] == 'parcial' else 1)
                G.add_edge(f"A{rota['origem']}", f"A{rota['destino']}", 
                          weight=peso, 
                          status=rota['status'],
                          origem=rota['origem'],
                          destino=rota['destino'])
        
        # Conectando centros às áreas mais próximas
        for _, centro in centros_df.iterrows():
            centro_coord = (centro['longitude'], centro['latitude'])
            # Encontra as 3 áreas mais próximas para conectar
            for _, area in areas_df.head(3).iterrows():
                area_coord = (area['longitude'], area['latitude'])
                distancia = ((centro_coord[0] - area_coord[0])**2 + 
                            (centro_coord[1] - area_coord[1])**2)**0.5 * 100  # Distância aproximada
                G.add_edge(f"C{centro['id']}", f"A{area['id']}", 
                          weight=distancia*2,  # Tempo estimado
                          status='livre')
        
        # Salvando o grafo para uso posterior
        nx.write_gpickle(G, f"{self.output_dir}rede_logistica.gpickle")
        
        self.G = G
        print(f"Rede de rotas criada com {len(G.nodes())} nós e {len(G.edges())} conexões")
        return G
        
    def visualizar_rede(self, filename='rede_logistica.png'):
        """Gera visualização da rede logística.
        
        Args:
            filename (str): Nome do arquivo para salvar a visualização.
            
        Returns:
            str: Caminho do arquivo de visualização gerado.
        """
        if self.G is None:
            self.G = nx.read_gpickle(f"{self.output_dir}rede_logistica.gpickle")
            
        # Visualização do grafo
        pos = nx.get_node_attributes(self.G, 'pos')
        node_colors = ['red' if self.G.nodes[n]['tipo'] == 'centro' else 
                      ('green' if self.G.nodes[n].get('criticidade') == 'baixa' else
                      ('yellow' if self.G.nodes[n].get('criticidade') == 'média' else 'orange'))
                      for n in self.G.nodes()]
        
        plt.figure(figsize=(12, 10))
        nx.draw(self.G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=8)
        edge_labels = {(u, v): f"{d['status']}\n{d['weight']:.1f}min" for u, v, d in self.G.edges(data=True)}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=7)
        plt.title('Rede Logística de Ajuda Humanitária')
        
        # Salvar a visualização
        filepath = f'{self.visualization_dir}{filename}'
        plt.savefig(filepath)
        plt.close()
        
        print(f"Visualização da rede salva em {filepath}")
        return filepath

# Exemplo de uso
if __name__ == "__main__":
    network = RouteNetwork()
    network.criar_rede()
    network.visualizar_rede()
    print("Rede de rotas modelada com sucesso!")
