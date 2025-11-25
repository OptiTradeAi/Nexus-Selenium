// static/scanner.js
(function(){
  if (window.__nexus_scanner_installed) return;
  window.__nexus_scanner_installed = true;

  // CONFIG
  const BACKEND = (new URL(window.location.href)).origin; // not used; bookmarklet will set target
  const SEND_ENDPOINT = (typeof NEXUS_CAPTURE_ENDPOINT !== "undefined") ? NEXUS_CAPTURE_ENDPOINT : null;
  const TOKEN = (typeof NEXUS_TOKEN_INJECT !== "undefined") ? NEXUS_TOKEN_INJECT : null;

  // Utils
  function cssPath(el){
    if(!el) return null;
    // Build a reasonably robust CSS selector (id preferred, otherwise tag+classes+nth)
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
        const siblings = Array.from(parent.children).filter(c => c.tagName === el.tagName);
        if (siblings.length > 1) {
          const index = Array.prototype.indexOf.call(parent.children, el) + 1;
          part += `:nth-child(${index})`;
        }
      }
      parts.unshift(part);
      el = el.parentNode;
    }
    return parts.join(' > ');
  }

  function safeSend(data){
    if (!SEND_ENDPOINT) {
      console.warn("No SEND_ENDPOINT defined for scanner.");
      return;
    }
    try {
      fetch(SEND_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-NEXUS-TOKEN": TOKEN || ""
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

  // Main logic: find typical login-related elements without reading values
  function findLoginElements(){
    const res = {timestamp: new Date().toISOString(), url: location.href, fields: {}, notes: ""};

    // Candidate inputs by type or placeholder or name
    const email = document.querySelector("input[type='email'], input[placeholder*='email'], input[placeholder*='Email'], input[name*='user'], input[name*='email']");
    const password = document.querySelector("input[type='password'], input[placeholder*='senha'], input[placeholder*='Senha'], input[name*='password'], input[name*='pass']");
    // Common submit buttons
    const submit = document.querySelector("button[type='submit'], input[type='submit'], button:contains('Entrar'), button:contains('Iniciar')");

    // fallback approaches: broader search
    if(!email){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => /email|user|login/i.test(i.name || i.placeholder || i.id || ""));
      if(candidates.length) email = candidates[0];
    }
    if(!password){
      const candidates = Array.from(document.querySelectorAll("input")).filter(i => i.type === 'password' || /senha|pass/i.test(i.name || i.placeholder || i.id || ""));
      if(candidates.length) password = candidates[0];
    }

    // Build result with selectors (no values)
    try {
      if(email) res.fields.email = {
        tag: email.tagName,
        selector: cssPath(email),
        placeholder: email.placeholder || null,
        name: email.name || null,
        id: email.id || null,
        dataset: {...email.dataset}
      };
      if(password) res.fields.password = {
        tag: password.tagName,
        selector: cssPath(password),
        placeholder: password.placeholder || null,
        name: password.name || null,
        id: password.id || null,
        dataset: {...password.dataset}
      };
      // try to find the form parent and submit button inside form
      let form = email && email.form ? email.form : (password && password.form ? password.form : document.querySelector("form"));
      if(form){
        const btn = form.querySelector("button[type='submit'], input[type='submit'], button");
        if(btn) {
          res.fields.submit = { selector: cssPath(btn), text: btn.innerText ? btn.innerText.trim() : null };
          res.fields.form = { selector: cssPath(form) };
        }
      } else {
        // fallback global search
        const btn = document.querySelector("button[type='submit'], input[type='submit'], button");
        if(btn) res.fields.submit = { selector: cssPath(btn), text: btn.innerText ? btn.innerText.trim() : null };
      }
    } catch(e){
      res.notes = "error building selectors: " + (e && e.message);
    }
    return res;
  }

  // Mutation observer to detect changes (and update selectors)
  let lastCapture = null;
  const obs = new MutationObserver((muts)=>{
    // on each mutation, attempt to (re)discover login elements
    const info = findLoginElements();
    const infoStr = JSON.stringify(info);
    if(infoStr !== lastCapture){
      lastCapture = infoStr;
      console.log("Nexus scanner detected DOM change, sending capture:", info);
      safeSend(info);
    }
  });

  // Start observing the whole document for changes
  try {
    obs.observe(document, {childList:true, subtree:true, attributes:true});
  } catch(e){
    console.warn("Observer failed", e);
  }

  // Also send an immediate capture
  const initial = findLoginElements();
  lastCapture = JSON.stringify(initial);
  safeSend(initial);

  // Safety timeout: stop observer after 10 minutes to avoid runaway
  setTimeout(()=>{ try{ obs.disconnect(); console.log("Nexus scanner stopped after timeout"); }catch(e){} }, 10 * 60 * 1000);

  console.log("Nexus scanner installed (no credential values collected).");
})();
