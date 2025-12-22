document.addEventListener('DOMContentLoaded', () => {
  // ===== Получение элементов =====
  const loginModal = document.getElementById('loginModal');
  const registerModal = document.getElementById('registerModal');
  const resetModal = document.getElementById('resetModal');
  const resetLinkModal = document.getElementById('resetLinkModal');

  const loginBtn = document.getElementById('loginBtn');
  const registerBtn = document.getElementById('registerBtn');
  const forgotLink = document.getElementById('forgotPasswordLink');

  const closeButtons = document.querySelectorAll('.close');
  const modals = [loginModal, registerModal, resetModal, resetLinkModal].filter(Boolean);

  const loginNotification = document.getElementById('loginNotification');
  const registerNotification = document.getElementById('registerNotification');
  const resetNotification = document.getElementById('resetNotification');
  const resetLinkEl = document.getElementById('resetLink');
  const resetLinkClose = document.getElementById('resetLinkClose');

  // ===== Функции открытия/закрытия =====
  function openModal(modal) {
    if (!modal) return;
    modal.style.display = 'flex';
  }

  function closeAll() {
    modals.forEach(m => m.style.display = 'none');
  }

  closeAll();

  if (loginBtn) loginBtn.onclick = () => openModal(loginModal);
  if (registerBtn) registerBtn.onclick = () => openModal(registerModal);
  if (forgotLink) forgotLink.onclick = () => { closeAll(); openModal(resetModal); };

  closeButtons.forEach(btn => btn.onclick = () => closeAll());
  window.onclick = e => { if (modals.includes(e.target)) closeAll(); };

  // ===== Форма Входа =====
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.onsubmit = async e => {
      e.preventDefault();
      const data = {
        email: loginForm.elements["email"].value,
        password: loginForm.elements["password"].value
      };
      const remember = loginForm.elements["rememberMe"]?.checked;

      const response = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        if (remember) localStorage.setItem("userEmail", data.email);
        else localStorage.removeItem("userEmail");
        location.reload();
      } else if (loginNotification) {
        loginNotification.textContent = result.message || "Ошибка входа";
        loginNotification.style.display = "block";
        loginNotification.style.color = "#ef4444";
        setTimeout(() => loginNotification.style.display = "none", 5000);
      }
    };
  }

  // ===== Форма Регистрации =====
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    const passwordInput = registerForm.elements["password"];
    const strengthBar = document.getElementById("strength-bar");
    const rules = {
      length: v => v.length >= 8,
      letter: v => /[a-zA-Z]/.test(v),
      digit: v => /\d/.test(v),
      special: v => /[!@#$%^&*]/.test(v)
    };

    passwordInput?.addEventListener("input", () => {
      const value = passwordInput.value;
      let passed = 0;
      Object.entries(rules).forEach(([key, check]) => {
        const el = document.querySelector(`[data-rule="${key}"]`);
        if (!el) return;
        if (check(value)) { el.classList.add("valid"); el.classList.remove("invalid"); passed++; }
        else { el.classList.add("invalid"); el.classList.remove("valid"); }
      });
      strengthBar.style.width = `${passed * 25}%`;
      strengthBar.className = "strength-bar";
      if (passed >= 3) strengthBar.classList.add("medium");
      if (passed === 4) strengthBar.classList.add("strong");
    });

    registerForm.onsubmit = async e => {
      e.preventDefault();
      if (!strengthBar.classList.contains("strong")) {
        registerNotification.textContent = "Пароль недостаточно надёжный!";
        registerNotification.style.display = "block";
        registerNotification.style.color = "#ef4444";
        setTimeout(() => registerNotification.style.display = "none", 5000);
        return;
      }

      const data = {
        fullname: registerForm.elements["fullname"].value,
        email: registerForm.elements["email"].value,
        password: passwordInput.value
      };

      const response = await fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      const result = await response.json();

      if (response.ok) closeAll();
      else {
        registerNotification.textContent = result.message || "Ошибка регистрации";
        registerNotification.style.display = "block";
        registerNotification.style.color = "#ef4444";
        setTimeout(() => registerNotification.style.display = "none", 5000);
      }
    };
  }

  // ===== Форма Сброса пароля =====
  const resetForm = document.getElementById('resetForm');
  if (resetForm) {
    resetForm.onsubmit = async e => {
      e.preventDefault();
      const data = { email: resetForm.elements["email"].value };
      const response = await fetch("/reset-password", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      const result = await response.json();

      if (response.ok && result.reset_link) {
          resetLinkEl.href = result.reset_link;
          resetLinkEl.textContent = result.reset_link;
          openModal(resetLinkModal);  
      } else if (resetNotification) {
        resetNotification.textContent = result.message || "Ошибка отправки ссылки";
        resetNotification.style.display = "block";
        resetNotification.style.color = "#ef4444";
        setTimeout(() => resetNotification.style.display = "none", 5000);
      }
    };
  }

  if (resetLinkClose) resetLinkClose.onclick = () => resetLinkModal.style.display = "none";

  // ===== Запомнить email =====
  const savedEmail = localStorage.getItem("userEmail");
  if (savedEmail && loginForm) {
    loginForm.elements["email"].value = savedEmail;
    if (loginForm.elements["rememberMe"]) loginForm.elements["rememberMe"].checked = true;
  }
});
