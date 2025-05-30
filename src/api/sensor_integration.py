import random
import time
import pandas as pd
import networkx as nx
import os
import pickle  # Adicione esta importação

class SensorIntegration:
    def __init__(self, input_dir='src/data/', output_dir='src/data/'):
        """Integração com sensores ESP32 para atualizar status das rotas.
        
        Args:
            input_dir (str): Diretório onde os dados de entrada estão armazenados.
            output_dir (str): Diretório onde os resultados serão salvos.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.G = None
        
    def simular_dados_sensor(self):
        """Simula dados recebidos de um sensor ESP32.
        
        Returns:
            dict: Dados simulados do sensor.
        """
        # Carregar dados atuais de rotas
        rotas_df = pd.read_csv(f'{self.input_dir}rotas.csv')
        
        # Selecionar uma rota aleatória para atualizar
        rota_idx = random.randint(0, len(rotas_df) - 1)
        rota = rotas_df.iloc[rota_idx]
        
        # Simular nova leitura do sensor
        novo_status = random.choice(['livre', 'parcial', 'bloqueada'])
        
        # Estrutura semelhante à leitura serial do ESP32
        # Formato: DADOS_SENSOR:rota_id:status:nivel_agua:bloqueio
        nivel_agua = random.randint(0, 4095)
        nivel_bloqueio = random.randint(0, 4095)
        
        return {
            'rota_id': rota_idx,
            'origem': rota['origem'],
            'destino': rota['destino'],
            'status': novo_status,
            'nivel_agua': nivel_agua,
            'nivel_bloqueio': nivel_bloqueio,
            'timestamp': time.time()
        }
    
    def processar_dados_seriais(self, linha_serial):
        """Processa dados recebidos do sensor ESP32 via Serial.
        
        Args:
            linha_serial (str): Linha recebida do ESP32 com formato DADOS_SENSOR:id:status:agua:bloqueio
            
        Returns:
            dict: Dados processados ou None se o formato for inválido
        """
        try:
            if not linha_serial.startswith("DADOS_SENSOR:"):
                return None
                
            partes = linha_serial.strip().split(":")
            if len(partes) != 5:
                return None
                
            # Carregar dados de rotas para encontrar origem/destino pelo ID
            rotas_df = pd.read_csv(f'{self.input_dir}rotas.csv')
            rota_id = int(partes[1])
            
            # Encontrar a rota no DataFrame
            rota_mask = (rotas_df.index == rota_id)
            if not rota_mask.any():
                print(f"Rota ID {rota_id} não encontrada no DataFrame")
                return None
                
            rota = rotas_df.loc[rota_mask].iloc[0]
            
            return {
                'rota_id': rota_id,
                'origem': rota['origem'],
                'destino': rota['destino'],
                'status': partes[2],
                'nivel_agua': int(partes[3]),
                'nivel_bloqueio': int(partes[4]),
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"Erro ao processar dados seriais: {e}")
            return None
    
    def atualizar_grafo(self, dados_sensor):
        """Atualiza o grafo da rede com base nos dados do sensor.
        
        Args:
            dados_sensor (dict): Dados recebidos do sensor.
            
        Returns:
            networkx.Graph: Grafo atualizado.
        """
        # Carregar o grafo atual usando pickle
        if self.G is None:
            with open(f"{self.input_dir}rede_logistica.pkl", 'rb') as f:
                self.G = pickle.load(f)
        
        # Identificar a aresta correspondente à rota
        origem = f"A{dados_sensor['origem']}"
        destino = f"A{dados_sensor['destino']}"
        
        # Verificar se a aresta existe
        if self.G.has_edge(origem, destino):
            # Guardar status anterior
            status_anterior = self.G[origem][destino]['status']
            
            # Atualizar o status da rota
            self.G[origem][destino]['status'] = dados_sensor['status']
            
            # Ajustar o peso conforme o novo status
            tempo_base = self.G[origem][destino]['weight']
            if status_anterior != 'parcial' and dados_sensor['status'] == 'parcial':
                # Se a rota ficou parcialmente bloqueada, aumenta o tempo
                self.G[origem][destino]['weight'] = tempo_base * 2
            elif status_anterior == 'parcial' and dados_sensor['status'] == 'livre':
                # Se a rota foi liberada, reduz o tempo
                self.G[origem][destino]['weight'] = tempo_base / 2
            elif dados_sensor['status'] == 'bloqueada':
                # Se a rota foi bloqueada, remove a aresta
                self.G.remove_edge(origem, destino)
                print(f"Rota entre {origem} e {destino} foi removida (bloqueada)")
                
            print(f"Atualizado status da rota {origem}-{destino} para {dados_sensor['status']}")
        else:
            print(f"Aresta {origem}-{destino} não encontrada no grafo")
        
        # Salvar o grafo atualizado usando pickle
        with open(f"{self.output_dir}rede_logistica.pkl", 'wb') as f:
            pickle.dump(self.G, f)
        
        # Atualizar também o CSV de rotas
        self.atualizar_csv_rotas(dados_sensor)
        
        return self.G
    
    def atualizar_csv_rotas(self, dados_sensor):
        """Atualiza o arquivo CSV de rotas com os novos dados do sensor.
        
        Args:
            dados_sensor (dict): Dados do sensor a serem atualizados.
        """
        rotas_df = pd.read_csv(f'{self.input_dir}rotas.csv')
        
        # Identificar a rota no DataFrame
        mask = ((rotas_df['origem'] == dados_sensor['origem']) & 
                (rotas_df['destino'] == dados_sensor['destino']))
        
        if mask.any():
            # Atualizar o status da rota
            rotas_df.loc[mask, 'status'] = dados_sensor['status']
            rotas_df.to_csv(f'{self.output_dir}rotas.csv', index=False)
            print("Arquivo CSV de rotas atualizado")
        else:
            print("Rota não encontrada no arquivo CSV")
    
    def monitorar_simulado(self, intervalo_segundos=10, num_atualizacoes=3):
        """Simula o monitoramento contínuo do sensor por um tempo determinado.
        
        Args:
            intervalo_segundos (int): Intervalo entre leituras em segundos.
            num_atualizacoes (int): Número de atualizações a realizar.
            
        Returns:
            list: Lista de dados de sensores simulados.
        """
        print(f"Iniciando monitoramento simulado de rotas por {num_atualizacoes} atualizações...")
        dados_coletados = []
        
        for i in range(num_atualizacoes):
            print(f"\nAtualização {i+1}/{num_atualizacoes}")
            
            # Simular dados do sensor
            dados_sensor = self.simular_dados_sensor()
            print(f"Dados do sensor: Rota {dados_sensor['origem']}-{dados_sensor['destino']} → {dados_sensor['status']}")
            
            # Atualizar o grafo
            self.atualizar_grafo(dados_sensor)
            
            # Guardar dados coletados
            dados_coletados.append(dados_sensor)
            
            # Aguardar próxima leitura
            if i < num_atualizacoes - 1:
                print(f"Aguardando {intervalo_segundos} segundos para próxima leitura...")
                time.sleep(intervalo_segundos)
        
        print("Monitoramento simulado concluído!")
        return dados_coletados

# Exemplo de uso
if __name__ == "__main__":
    integration = SensorIntegration()
    dados_coletados = integration.monitorar_simulado(intervalo_segundos=3, num_atualizacoes=2)
    print(f"Foram coletados dados de {len(dados_coletados)} sensores")