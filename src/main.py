import os
import time
import argparse
from data.data_generator import DataGenerator
from models.criticality_classifier import CriticalityClassifier
from models.route_network import RouteNetwork
from models.resource_allocator import ResourceAllocator
from api.sensor_integration import SensorIntegration

class HumanitarianLogisticsSystem:
    def __init__(self):
        """Sistema de Apoio à Tomada de Decisão e Gestão de Logística para Ajuda Humanitária"""
        # Configurar diretórios
        self.data_dir = 'src/data/'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Inicializar componentes
        self.data_generator = DataGenerator(output_dir=self.data_dir)
        self.classifier = CriticalityClassifier(input_dir=self.data_dir, output_dir=self.data_dir)
        self.network = RouteNetwork(input_dir=self.data_dir, output_dir=self.data_dir)
        self.allocator = ResourceAllocator(input_dir=self.data_dir, output_dir=self.data_dir)
        self.sensor = SensorIntegration(input_dir=self.data_dir, output_dir=self.data_dir)
        
    def inicializar_sistema(self):
        """Inicializa todo o sistema em sequência"""
        print("\n" + "="*80)
        print("Inicializando Sistema de Apoio à Tomada de Decisão e Gestão de Logística...")
        print("="*80 + "\n")
        
        # Etapa 1: Gerar dados simulados
        print("\n--- ETAPA 1: GERAÇÃO DE DADOS SIMULADOS ---\n")
        self.data_generator.gerar_todos_dados()
        
        # Etapa 2: Classificar áreas críticas
        print("\n--- ETAPA 2: CLASSIFICAÇÃO DE ÁREAS CRÍTICAS ---\n")
        self.classifier.classificar_areas()
        
        # Etapa 3: Modelar rede de rotas
        print("\n--- ETAPA 3: MODELAGEM DA REDE DE ROTAS ---\n")
        self.network.criar_rede()
        self.network.visualizar_rede()
        
        # Etapa 4: Gerar plano logístico inicial
        print("\n--- ETAPA 4: GERAÇÃO DO PLANO LOGÍSTICO ---\n")
        plano = self.allocator.alocar_recursos()
        self.allocator.exibir_resumo_plano(plano)
        
        print("\n" + "="*80)
        print("Sistema inicializado com sucesso!")
        print("="*80 + "\n")
        
        return True
        
    def simular_atualizacao_sensor(self):
        """Simula a recepção de dados do sensor ESP32 e atualiza o sistema"""
        print("\n" + "="*80)
        print("SIMULAÇÃO: Atualizando status de rota via sensor ESP32")
        print("="*80 + "\n")
        
        # Simular dados do sensor
        sensor_data = self.sensor.simular_dados_sensor()
        print(f"Dados recebidos do sensor:")
        print(f"  Rota: {sensor_data['origem']} → {sensor_data['destino']}")
        print(f"  Novo status: {sensor_data['status']}")
        print(f"  Nível de água: {sensor_data['nivel_agua']}")
        print(f"  Nível de bloqueio: {sensor_data['nivel_bloqueio']}")
        
        # Atualizar o grafo
        self.sensor.atualizar_grafo(sensor_data)
        
        # Visualizar a rede atualizada
        self.network.visualizar_rede('rede_logistica_atualizada.png')
        
        # Recalcular plano logístico
        if sensor_data['status'] == 'bloqueada':
            print("\nRota bloqueada detectada! Recalculando plano logístico...\n")
            plano = self.allocator.alocar_recursos()
            self.allocator.exibir_resumo_plano(plano)
        
        return True
    
    def executar_simulacao_completa(self):
        """Executa uma simulação completa do sistema"""
        self.inicializar_sistema()
        
        # Aguardar um momento para simular passagem de tempo
        print("\nAguardando 3 segundos para simular passagem de tempo...\n")
        time.sleep(3)
        
        # Simular múltiplas atualizações do sensor
        print("\n--- ETAPA 5: SIMULAÇÃO DE MONITORAMENTO ESP32 ---\n")
        self.sensor.monitorar_simulado(intervalo_segundos=2, num_atualizacoes=3)
        
        # Recalcular plano após mudanças
        print("\n--- ETAPA 6: RECÁLCULO DO PLANO LOGÍSTICO ---\n")
        plano = self.allocator.alocar_recursos()
        self.allocator.exibir_resumo_plano(plano)
        
        # Visualizar rede final
        self.network.visualizar_rede('rede_logistica_final.png')
        
        print("\n" + "="*80)
        print("Simulação concluída com sucesso!")
        print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Sistema de Logística para Ajuda Humanitária')
    parser.add_argument('--init', action='store_true', help='Inicializar o sistema')
    parser.add_argument('--sensor', action='store_true', help='Simular atualização de sensor')
    parser.add_argument('--full', action='store_true', help='Executar simulação completa')
    
    args = parser.parse_args()
    
    system = HumanitarianLogisticsSystem()
    
    if args.init:
        system.inicializar_sistema()
    elif args.sensor:
        system.simular_atualizacao_sensor()
    elif args.full:
        system.executar_simulacao_completa()
    else:
        # Se nenhum argumento for fornecido, executar a simulação completa
        system.executar_simulacao_completa()

if __name__ == "__main__":
    main()
