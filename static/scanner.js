(function(){
  if (window.__nexus_scanner_installed) return;
  window.__nexus_scanner_installed = true;

  console.log("NEXUS SCANNER iniciado ✔");

  const TOKEN = window.NEXUS_TOKEN_INJECT || "032318";
  const CAPTURE_URL = window.NEXUS_CAPTURE_ENDPOINT || (window.location.origin + "/capture");

  function safeFetch(url, payload){
    try {
      return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Nexus-Token": TOKEN
        },
        body: JSON.stringify(payload),
        keepalive: true
      }).then(r => r.json()).catch(e => { console.warn("fetch err:", e); });
    } catch(e){
      console.warn("safeFetch exception", e);
    }
  }

  function cssPath(el){
    if(!el) return null;
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    while (el && el.nodeType === 1 && el.tagName.toLowerCase() !== 'html') {
      let part = el.tagName.toLowerCase();
      if (el.className && typeof el.className === 'string') {
        const cls = el.className.trim().split(/\s+/).filter(Boolean);
        if (cls.length) part += '.' + cls.join('.');
      }
      const parent = el.parentNode;
      if (parent) {
        const index = Array.prototype.indexOf.call(parent.children, el) + 1;
        part += `:nth-child(${index})`;
      }
      parts.unshift(part);
      el = el.parentNode;
    }
    return parts.join(' > ');
  }

  function findLoginElements(){
    const res = {timestamp: new Date().toISOString(), url: location.href, fields: {}, notes: ""};
    let email = document.querySelector("input[type='email'], input[placeholder*='email'], input[name*='user'], input[name*='email']");
    let password = document.querySelector("input[type='password'], input[placeholder*='senha'], input[name*='password']");
    // broad fallback
    if(!email){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => /email|user|login|cpf/i.test(i.name + i.placeholder + i.id));
      if(candidates.length) email = candidates[0];
    }
    if(!password){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => i.type === 'password' || /senha|pass|pwd/i.test(i.name + i.placeholder + i.id));
      if(candidates.length) password = candidates[0];
    }
    try {
      if(email) res.fields.email = { tag: email.tagName, selector: cssPath(email), placeholder: email.placeholder || "", name: email.name || "", id: email.id || "" };
      if(password) res.fields.password = { tag: password.tagName, selector: cssPath(password), placeholder: password.placeholder || "", name: password.name || "", id: password.id || "" };
      let form = (email && email.form) || (password && password.form) || document.querySelector("form");
      if(form){
        const btn = form.querySelector("button[type='submit'], input[type='submit'], button");
        if(btn) res.fields.submit = { selector: cssPath(btn), text: (btn.innerText||"").trim() };
        res.fields.form = { selector: cssPath(form) };
      } else {
        const btn = document.querySelector("button[type='submit'], input[type='submit'], button");
        if(btn) res.fields.submit = { selector: cssPath(btn), text: (btn.innerText||"").trim() };
      }
    } catch(e){
      res.notes = "error building selectors: " + (e && e.message);
    }
    return res;
  }

  // send initial capture immediately
  try {
    const initial = findLoginElements();
    safeFetch(CAPTURE_URL, Object.assign({event:"initial_scan"}, initial));
    console.log("NEXUS scanner initial capture sent", initial);
  } catch(e){
    console.warn("scanner initial error", e);
  }

  // observe mutations and send diffs
  let last = null;
  const obs = new MutationObserver(() => {
    try {
      const info = findLoginElements();
      const s = JSON.stringify(info);
      if(s !== last){
        last = s;
        safeFetch(CAPTURE_URL, Object.assign({event:"mutation_scan"}, info));
        console.log("NEXUS scanner mutation capture sent");
      }
    } catch(e){
      console.warn("mutation handler error", e);
    }
  });

  try {
    obs.observe(document, {childList:true, subtree:true, attributes:true});
  } catch(e){
    console.warn("Observer failed", e);
  }

  // stop after 10 minutes automatically
  setTimeout(()=>{ try{ obs.disconnect(); console.log("NEXUS scanner stopped after timeout"); }catch(e){} }, 10 * 60 * 1000);

  console.log("NEXUS scanner installed (no credential values collected).");
})();
