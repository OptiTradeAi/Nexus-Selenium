(function(){

  const BASE = window.location.origin;
  const TOKEN = "032318"; // token temporário - você pode alterar via env e rebuild

  function loadScript(src){
      return new Promise((resolve)=>{
          const s = document.createElement("script");
          s.src = src + "?ts=" + Date.now();
          s.onload = resolve;
          document.head.appendChild(s);
      });
  }

  async function start(){
      console.log("NEXUS LOADER iniciado");

      // Exportar variáveis globais para outros scripts
      window.NEXUS_TOKEN_INJECT = TOKEN;
      window.NEXUS_CAPTURE_ENDPOINT = BASE + "/capture";
      window.NEXUS_BASE = BASE;

      // Se quiser que o scanner envie cookies/localStorage, defina:
      // window.NEXUS_ALLOW_COOKIES = true; // ATIVE SOMENTE SE AUTORIZAR
      window.NEXUS_ALLOW_COOKIES = false;

      await loadScript(BASE + "/static/scanner.js");
      // await loadScript(BASE + "/static/activity_keeper.js");
      // await loadScript(BASE + "/static/pair_manager.js");

      console.log("NEXUS: todos os módulos carregados com sucesso.");
  }

  start();

})();
