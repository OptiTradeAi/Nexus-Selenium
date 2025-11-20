# Nexus Selenium – HomeBroker Automation

Sistema automático de login e coleta baseado em Selenium com suporte para Render.

## Arquivos principais
- `agent.py` – Loop principal
- `selenium_core.py` – Login + automação
- `main.py` – API básica
- `Dockerfile` – Deploy no Render
- `requirements.txt` – Dependências

## Login

Campos mapeados pelo scan:

- E-mail → `input#\\:rb\\:-form-item`
- Senha → `div#\\:rc\\:-form-item > input`
- Botão → `form button[type='submit']`

## Deploy no Render
1. Subir tudo para o GitHub
2. Criar Web Service
3. Porta padrão = **8000**

## Testar
Visite:
