# Nexus Injector — README

## Objetivo
Prover um método seguro e confiável para o Nexus aprender os seletores do login da corretora (HomeBroker) executando um scanner **no navegador real do usuário** (bookmarklet). O backend recebe só metadados (seletor, placeholder, etc.) — **não coleta** valores de login/senha.

---

## Arquivos importantes
- `main.py` — FastAPI backend com endpoint `/capture`.
- `static/injector.html` — página pública com instruções e bookmarklet.
- `static/scanner.js` — script de scanner (executado no contexto da página da corretora).
- `Dockerfile`, `requirements.txt` — para deploy na Render.
- `.env.example` — modelo de variável de ambiente.

---

## Passo a passo rápido (deploy e uso)

### 1) Deploy no Render
1. Suba o repositório no GitHub (ou diretamente na Render).
2. Crie um serviço Web no Render (Docker) apontando para o repositório.
3. Em **Environment**, defina:
   - `NEXUS_TOKEN = <seu-token-secreto>`
4. Deploy. Quando o serviço for publicado, terá uma URL pública: `https://<seu-service>.onrender.com/`.

### 2) Configurar bookmarklet (recomendado)
Opções:
- **Sem token embutido (mais seguro):**
  1. Abra `https://<seu-service>.onrender.com/` (injector.html).
  2. Arraste o botão **NEXUS SCAN** para a barra de favoritos (desktop) ou copie o código do bookmarklet e crie manualmente um favorito (mobile).
  3. Abra `https://www.homebroker.com/pt/sign-in` no mesmo navegador.
  4. Clique no favorito **NEXUS SCAN**. O script `scanner.js` será carregado e enviará seletores para `https://<seu-service>.onrender.com/capture`. **Você continuará digitando o login/senha manualmente.**

- **Com token embutido (conveniente, menos seguro):**
  1. No injector.html há um código pronto com `YOUR_TOKEN`. Substitua `YOUR_TOKEN` pelo valor de `NEXUS_TOKEN` e crie o favorito com esse código.
  2. Ao clicar, o scanner enviará with header `X-NEXUS-TOKEN` automaticamente.

> Recomendação: use a opção sem token embutido se estiver inseguro. Defina `NEXUS_TOKEN` na Render e use o bookmarklet sem token — depois veja `/captures` no backend para confirmar.

### 3) Verificar captures
- Acesse `https://<seu-service>.onrender.com/captures` para ver os arquivos JSON gerados.
- Cada capture contém `fields` com seletores (email, password, submit, form), `url` e `timestamp`.

### 4) Consumir os seletores no agent/Selenium
- Baixe o JSON do capture (`/data/<file>`).
- Use os seletores enviados para o Selenium (ou para seu `selenium_core.py`) — **lembre-se de nunca enviar os valores de campo pelo scanner**. O Selenium fará o preenchimento localmente (se for rodar em um ambiente que tenha permissão/ acesso IP permitido pela corretora).

---

## Segurança e ética
- O scanner NÃO envia valores dos inputs.
- O uso é autorizado por você — nunca use isso para contas que não são suas.
- Proteja `NEXUS_TOKEN` no Render.

---

## Troubleshooting rápido
- Se nada aparece em `/captures`, verifique:
  - O bookmarklet foi executado na página correta (`homebroker`).
  - Seu serviço tem `NEXUS_TOKEN` e, se você usou a versão com token embutido, o token no favorito confere.
  - Console do navegador (F12) mostrará logs do scanner.
