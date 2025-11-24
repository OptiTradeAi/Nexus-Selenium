# Nexus-Selenium (Atualizado)

Resumo:
- Serviço FastAPI que expõe /injector e /capture.
- Selenium (undetected-chromedriver) roda em background e salva /app/data/dom.html.
- Fluxo recomendado: usar bookmarklet (scanner.js) no browser real para capturar seletores e enviar ao /capture.

Configuração:
1. No Render -> Environment variables crie:
   - PORT=10000
   - NEXUS_TOKEN=Dcrt17*
   - NEXUS_CAPTURE_SECRET=Dcrt17*
   - HB_EMAIL (opcional)
   - HB_PASSWORD (opcional)

2. Faça deploy (Docker) com Dockerfile no root. Docker build context: `.`
3. Acesse: https://<seu-servico>.onrender.com/injector
4. No celular, abra a página da corretora (via injector ou direto), execute o bookmarklet (scanner.js) — o scanner enviará os seletores para /capture.
5. Depois de salvar a captura em /app/data, o selenium_core pode usar os seletores para login automático.

Problemas comuns:
- Access restricted por região: use VPN/região permitida.
- Iframe/CORS: a injeção cross-origin pode ser bloqueada — use bookmarklet direto na página real (recomendado).
- Token inválido: verifique NEXUS_CAPTURE_SECRET e header X-Nexus-Token no envio.
