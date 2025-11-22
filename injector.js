// injector.js
(function(){
  // Configuration: replace these values when you deploy
  var NEXUS_CAPTURE_URL = (window.__NEXUS_CAPTURE_URL__ || "REPLACE_WITH_YOUR_NEXUS_URL/capture"); 
  var TOKEN = (window.__NEXUS_TOKEN__ || "REPLACE_WITH_YOUR_TOKEN");

  function grabInputInfo(input){
    return {
      tag: input.tagName,
      type: input.type || null,
      name: input.name || null,
      id: input.id || null,
      placeholder: input.placeholder || null,
      xpath: xpathForElement(input)
    };
  }

  function xpathForElement(el){
    if (!el) return null;
    var segs = [];
    for (; el && el.nodeType == 1; el = el.parentNode) {
      var i = 1;
      for (var sib = el.previousSibling; sib; sib = sib.previousSibling) {
        if (sib.nodeType == 1 && sib.tagName == el.tagName) i++;
      }
      var tagName = el.tagName.toLowerCase();
      var seg = tagName + '[' + i + ']';
      segs.unshift(seg);
    }
    return '/' + segs.join('/');
  }

  function collect(){
    var inputs = Array.from(document.querySelectorAll("input, button, textarea, select"));
    var infos = inputs.map(grabInputInfo);
    // attempt heuristics for email/password/submit
    var email = inputs.find(i => i.type === 'email' || (i.placeholder && /email|e-mail/i.test(i.placeholder)) || (i.name && /email|user/i.test(i.name)));
    var password = inputs.find(i => i.type === 'password' || (i.placeholder && /senha|password/i.test(i.placeholder)) || (i.name && /pass|senha/i.test(i.name)));
    var submit = inputs.find(i => (i.type && (i.type==='submit' || i.type==='button')) || (i.tagName && i.tagName.toLowerCase()==='button'));
    var payload = {
      url: location.href,
      title: document.title,
      captured_at: new Date().toISOString(),
      inputs: infos,
      heuristics: {
        email: email ? grabInputInfo(email) : null,
        password: password ? grabInputInfo(password) : null,
        submit: submit ? grabInputInfo(submit) : null
      }
    };
    return payload;
  }

  function send(payload){
    var url = NEXUS_CAPTURE_URL + (NEXUS_CAPTURE_URL.indexOf('?') === -1 ? '?' : '&') + 'token=' + encodeURIComponent(TOKEN);
    fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    }).then(function(resp){ 
      if(resp.ok) alert("Nexus: captura enviada com sucesso.");
      else alert("Nexus: falha ao enviar (status "+resp.status+").");
    }).catch(function(err){
      alert("Nexus: erro ao enviar captura: " + err);
    });
  }

  try {
    var payload = collect();
    console.log("Nexus injector payload:", payload);
    send(payload);
  } catch(e) {
    console.error("injector error:", e);
    alert("Injector error: " + e);
  }
})();
