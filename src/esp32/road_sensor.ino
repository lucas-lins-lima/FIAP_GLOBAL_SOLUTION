// Código simplificado para ESP32 no Wokwi - sensor de status de estradas
#include <WiFi.h>

// Pinos dos sensores
const int bloqueioPin = 34;  // Sensor de bloqueio de estrada (analógico)
const int nivelAguaPin = 35; // Sensor de nível de água (analógico)
const int ledVermelho = 25;  // LED indicador de estrada bloqueada
const int ledAmarelo = 26;   // LED indicador de estrada com restrições
const int ledVerde = 27;     // LED indicador de estrada livre

// ID da rota monitorada
const int rotaID = 7;  // ID da rota que está sendo monitorada

void setup() {
  Serial.begin(115200);
  
  // Configuração dos pinos
  pinMode(bloqueioPin, INPUT);
  pinMode(nivelAguaPin, INPUT);
  pinMode(ledVermelho, OUTPUT);
  pinMode(ledAmarelo, OUTPUT);
  pinMode(ledVerde, OUTPUT);
  
  Serial.println("Sistema de monitoramento de rotas iniciado!");
}

void loop() {
  // Leitura dos sensores
  int bloqueioValor = analogRead(bloqueioPin);
  int nivelAgua = analogRead(nivelAguaPin);
  
  // Determinação do status da rota
  String status;
  
  if (bloqueioValor > 3000 || nivelAgua > 3500) {
    status = "bloqueada";
    digitalWrite(ledVermelho, HIGH);
    digitalWrite(ledAmarelo, LOW);
    digitalWrite(ledVerde, LOW);
  } else if (bloqueioValor > 2000 || nivelAgua > 2000) {
    status = "parcial";
    digitalWrite(ledVermelho, LOW);
    digitalWrite(ledAmarelo, HIGH);
    digitalWrite(ledVerde, LOW);
  } else {
    status = "livre";
    digitalWrite(ledVermelho, LOW);
    digitalWrite(ledAmarelo, LOW);
    digitalWrite(ledVerde, HIGH);
  }
  
  // Exibir informações no Serial Monitor
  Serial.println("=== Status da Rota " + String(rotaID) + " ===");
  Serial.println("Status: " + status);
  Serial.println("Nivel de agua: " + String(nivelAgua));
  Serial.println("Nivel de bloqueio: " + String(bloqueioValor));
  
  // Saída formatada para fácil interpretação pelo Python
  Serial.print("DADOS_SENSOR:");
  Serial.print(rotaID);
  Serial.print(":");
  Serial.print(status);
  Serial.print(":");
  Serial.print(nivelAgua);
  Serial.print(":");
  Serial.println(bloqueioValor);
  
  Serial.println("--------------------");
  
  // Aguardar antes da próxima leitura
  delay(5000);  // 5 segundos
}
