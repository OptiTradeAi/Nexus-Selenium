# Nexus-Selenium — Deploy quick instructions (Render / Docker)

## Arquivos necessários (na raiz)
- Dockerfile
- requirements.txt
- main.py
- selenium_core.py
- static/ (opcional; loader.js, scanner.js etc)
- data/ (será criado pelo container)

## Environment Variables (set in Render > Environment)
Set these at least:

- TOKEN = 032318                # token to validate scanner posts
- NEXUS_LOGIN_URL = https://www.homebroker.com/pt/invest
- BACKEND_PUBLIC_URL = https://nexus-selenium.onrender.com  # optional but helpful
- NEXUS_EMAIL = your_email@example.com   # optional: auto-login
- NEXUS_PASSWORD = YourPasswordHere      # optional: auto-login
- CHROME_BIN = /usr/bin/google-chrome    # usually not needed
- CHROMEDRIVER_PATH = /usr/bin/chromedriver

> **Important**: don't put real credentials in public repos. Use Render env secure fields.

## Notes about Chrome in Docker
- The Dockerfile tries apt-install of `chromium` and `chromium-driver`. If your environment blocks apt packages,
  the build may need manual chromedriver upload or a custom base image with Chrome preinstalled.
- If you see `SessionNotCreatedException` or `Chrome instance exited`, check Chrome <-> Chromedriver version compatibility.

## Logs / Debugging
- Visit your Render service logs to see `[selenium_core]` prints.
- Captured DOM snippets are saved under `/app/data/dom/` inside the container.
- Captures (events) appended to `/app/data/captures.log`.

## How the system behaves
- At startup main.py will start uvicorn and then call `start_selenium_thread()` which starts Selenium in background.
- Selenium tries to restore cookies, otherwise attempts env login if `NEXUS_EMAIL` / `NEXUS_PASSWORD` are provided.
- Selenium posts periodic heartbeat and DOM snippets to the `/capture` and `/api/dom` endpoints.
