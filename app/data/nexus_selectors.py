{
  "email": [
    "#email",
    "#user",
    "input[type='email']",
    "input[name*='email']",
    "input[name*='user']",
    "//input[contains(@placeholder,'Email') or contains(@placeholder,'email') or contains(@placeholder,'Usuário') or contains(@placeholder,'usuario')]",
    "//form//input[1]"
  ],
  "password": [
    "#password",
    "#senha",
    "input[type='password']",
    "input[name*='password']",
    "input[name*='pass']",
    "//input[contains(@placeholder,'Senha') or contains(@placeholder,'senha') or contains(@name,'pass')]",
    "//form//input[contains(@type,'password') or contains(@class,'password')]"
  ],
  "submit": [
    "button[type='submit']",
    "input[type='submit']",
    "button:contains('Entrar')",
    "//button[contains(translate(normalize-space(.),'ENTRAR','entrar'),'entrar')]",
    "//button[contains(., 'Login') or contains(., 'Entrar') or contains(., 'Acessar')]",
    "//form//button"
  ],
  "post_login_markers": [
    "//*[contains(text(),'Saldo')]",
    "//*[contains(text(),'Minhas Operações')]",
    "//*[contains(text(),'OTC')]",
    "//*[contains(text(),'Minha Carteira')]",
    "//*[contains(text(),'Mercado')]",
    "//header"
  ]
}
