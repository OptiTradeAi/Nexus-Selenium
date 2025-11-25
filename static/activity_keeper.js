(function(){

  console.log("NEXUS activity keeper ON");

  const BASE = window.location.origin;
  const token = window.NEXUS_TOKEN_INJECT;
  const interval = 20000; // 20s

  function humanMove(){
      try {
          window.scrollTo({
              top: Math.random() * 200,
              behavior: "smooth"
          });
      } catch(e){}
  }

  setInterval(humanMove, interval);

})();
