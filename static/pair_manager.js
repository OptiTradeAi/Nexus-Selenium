(function(){

  console.log("NEXUS Pair Manager ON");

  const interval = 30000; // 30 segundos

  function clickRandomPair(){
      try {
          const pairs = document.querySelectorAll("div, button, a");

          const otc = [...pairs].filter(el =>
              /(OTC|otc|Cripto|crypto|Par|Moeda)/i.test(el.innerText)
          );

          if(otc.length === 0){
              console.log("Nenhum par encontrado no DOM.");
              return;
          }

          const pick = otc[Math.floor(Math.random() * otc.length)];
          pick.click();

          console.log("Trocado par para -> ", pick.innerText);
      } catch(e){
          console.log("Erro ao trocar par: ", e);
      }
  }

  setInterval(clickRandomPair, interval);

})();
