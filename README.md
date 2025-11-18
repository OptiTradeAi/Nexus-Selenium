# Nexus Selenium
Robô navegador do projeto Nexus Mobile AI.

## Funções
- Login automático no HomeBroker
- Troca entre 7 pares OTC
- Captura do gráfico
- Envio via WebSocket para Nexus Mobile AI
- Reconexão automática infinita

## Instalação (LOCAL)
pip install -r requirements.txt
python agent.py

## Deploy na Render
- Crie novo serviço
- Runtime: Docker
- Porta: não precisa
- Deploy: auto
- Incluir arquivo `.env` com:
  HB_EMAIL=
  HB_PASSWORD=
  NEXUS_WS=
