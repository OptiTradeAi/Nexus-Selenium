# Nexus-Selenium — Quick Start

## O que este repositório contém
- Serviço que roda no Render (ou Docker) com Selenium (undetected-chromedriver).
- Endpoint `/injector.js` e instruções para criar um *bookmarklet* que, ao executar na página da HomeBroker, envia captura de DOM/seletores para o Nexus.
- Agent que usa os dados capturados para realizar login automático.

## Arquivos principais
- `agent.py` — processo principal que inicio o servidor e o loop Selenium.
- `main.py` — endpoints FastAPI: status, capture.
- `selenium_core.py` — rotinas Selenium (login automático usando seletores salvos).
- `utils.py` — helpers para salvar dados.
- `injector.js` — script que deve ser executado da HomeBroker para enviar dados para o Nexus.
- `bookmarklet.txt` — instruções para criar o bookmarklet.

## Variáveis de ambiente (Render / Environment)
Adicione estas variáveis no painel do Render (Environment > Environment Variables):

- `NEXUS_TOKEN` = token secreto que protege o endpoint `/capture`
- `NEXUS_CAPTURE_URL` = https://nexus-selenium.onrender.com/capture (ou a URL do seu serviço)
- `HB_EMAIL` = (opcional) email da conta HomeBroker para auto-login
- `HB_PASSWORD` = (opcional) senha da conta HomeBroker
- `HB_KEEP_DAYS` = tempo (dias) de retenção da sessão/credenciais (ex: 7)

## Passo-a-passo rápido (deploy + captura)
1. Substitua/adicione os arquivos neste repositório.
2. Configure as Environment Variables no Render conforme acima.
3. Deploy no Render (ou `docker build` locally).
4. Após o serviço ficar online abra `https://<sua-url>/injector.js` — ou pegue o código do `bookmarklet.txt`.
5. Crie o bookmarklet no seu navegador (ou no celular — instruções no bookmarklet.txt).
6. Acesse `https://www.homebroker.com/pt/sign-in`, clique no bookmarklet, faça login. O Nexus receberá a estrutura do DOM e salvará seletores.
7. O agent tentará usar esses seletores para logar automaticamente.

## Observações
- É necessário que você confirme consentimento: você fará o login manualmente na página quando o script for executado. O Nexus só recebe dados **com seu clique**.
- Guarde NEXUS_TOKEN e credenciais com segurança.
