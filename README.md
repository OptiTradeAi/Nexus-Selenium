# Nexus-Selenium (OptiTradeAi) — Robust Headless Login & Discovery

## Objetivo
Rodar um agente Selenium (undetected-chromedriver) em Render para acessar a página da HomeBroker, executar varredura robusta dos elementos de login (email/senha/submit) e tentar login automático quando credenciais forem fornecidas.

## Arquivos principais
- `main.py` - FastAPI endpoints (/start_scan, /status, /start_scan_and_redirect)
- `agent.py` - wrapper para iniciar uma execução do Selenium em background
- `selenium_core.py` - implementação robusta de descoberta e login (CSS -> XPath -> JS)
- `utils.py` - utilitários (screenshot)
- `Dockerfile` - container pronto para Render
- `requirements.txt` - dependências
- `.env.example` - variáveis ambiente

## Variáveis de Environment (colocar no painel Render -> Environment)
- `HB_EMAIL` (opcional) — email da HomeBroker para login automático
- `HB_PASSWORD` (opcional) — senha
- `START_URL` — https://www.homebroker.com/pt/sign-in
- `AUTO_LOGIN` — true|false (se true, tenta login automático com HB_EMAIL/HB_PASSWORD)
- `PORT` — 10000
- `SESSION_TTL_HOURS` — TTL para sessão (não implementado full, porém reservado)

## Como usar
1. No repositório, adicione os arquivos acima.
2. No Render: configure um Web Service (Docker) apontando para o repositório.
3. Configure as **Environment Variables** conforme `.env.example`.
4. Deploy.
5. Acesse:
   - `GET /start_scan` — inicia a varredura/login (resultado disponível em `/status`)
   - `GET /status` — ver status e resultado
   - `GET /start_scan_and_redirect` — redireciona para a página da corretora (para login manual assistido)

## Assistido vs Automático
- Se preferir dar login manualmente no navegador e o agente pegar a sessão, use `/start_scan_and_redirect` (abre a página). Depois execute `/start_scan` para que o agente tente descobrir elementos e realizar ações (a lógica básica já salva um screenshot em `/app/data/login_snapshot.png`).
- Para melhor autonomia 24/7, configure `HB_EMAIL` e `HB_PASSWORD` e `AUTO_LOGIN=true`. O agent tentará fazer o login sozinho.

## Debug
- Logs e screenshots são gravados em `/app/data/`.
- Se `status` retornar `error`, veja o `detail` com stacktrace/resumo.
