(function() {

    const RENDER_BASE = "https://nexus-selenium.onrender.com";
    const TOKEN = "032318";

    function loadScript(src){
        return new Promise((resolve)=>{
            const s = document.createElement("script");
            s.src = src + "?ts=" + Date.now();
            s.onload = resolve;
            document.head.appendChild(s);
        });
    }

    async function start(){
        console.log("🔥 NEXUS LOADER iniciado + conectado ao servidor Render");

        // Variáveis globais para scanner.js, activity_keeper.js e pair_manager.js
        window.NEXUS_TOKEN_INJECT = TOKEN;
        window.NEXUS_CAPTURE_ENDPOINT = RENDER_BASE + "/api/dom";
        window.NEXUS_BASE = RENDER_BASE;

        // Carregar módulos diretamente do servidor Render (sempre funciona)
        await loadScript(RENDER_BASE + "/static/scanner.js");
        await loadScript(RENDER_BASE + "/static/activity_keeper.js");
        await loadScript(RENDER_BASE + "/static/pair_manager.js");

        console.log("⚡ NEXUS: todos os módulos carregados e ativos.");
    }

    start();

})();
