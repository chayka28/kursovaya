document.addEventListener('DOMContentLoaded', () => {
  // Получаем элементы модальных окон
  const loginModal = document.getElementById('loginModal');
  const registerModal = document.getElementById('registerModal');
  const resetModal = document.getElementById('resetModal');

  // Получаем кнопки для открытия модальных окон
  const loginBtn = document.getElementById('loginBtn');
  const registerBtn = document.getElementById('registerBtn');
  const forgotLink = document.getElementById('forgotPasswordLink');

  // Получаем кнопки для закрытия окон
  const closeButtons = document.querySelectorAll('.close');
  const modals = [loginModal, registerModal, resetModal].filter(Boolean);

  // Функция для открытия модального окна
  function openModal(modal) {
    if (!modal) return;
    modal.style.display = 'flex';
  }

  // Функция для закрытия всех модальных окон
  function closeAll() {
    modals.forEach(m => m.style.display = 'none');
  }

  // Закрываем все модальные окна при загрузке страницы
  closeAll();

  // Открытие модальных окон по клику
  if (loginBtn && loginModal) {
    loginBtn.onclick = () => openModal(loginModal);
  }

  if (registerBtn && registerModal) {
    registerBtn.onclick = () => openModal(registerModal);
  }

  if (forgotLink && resetModal) {
    forgotLink.onclick = () => {
      closeAll();
      openModal(resetModal);
    };
  }

  // Закрытие всех окон по клику на кнопку закрытия
  closeButtons.forEach(btn => {
    btn.onclick = () => closeAll();
  });

  // Закрытие окон при клике вне области модального окна
  window.onclick = e => {
    if (modals.includes(e.target)) closeAll();
  };

  // Обработка форм входа, регистрации и сброса пароля
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
      alert(result.message || "Авторизация успешна");
      closeAll();

      if (response.ok && remember) {
        localStorage.setItem("userEmail", data.email);
      } else {
        localStorage.removeItem("userEmail");
      }

      if (response.ok) location.reload();
    };
  }

  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.onsubmit = async e => {
      e.preventDefault();

      const data = {
        fullname: registerForm.elements["fullname"].value,
        email: registerForm.elements["email"].value,
        password: registerForm.elements["password"].value
      };

      const response = await fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });

      const result = await response.json();
      alert(result.message || "Регистрация успешна");
      closeAll();
    };
  }

  const resetForm = document.getElementById('resetForm');
  if (resetForm) {
    resetForm.onsubmit = async e => {
      e.preventDefault();

      const data = {
        email: resetForm.elements["email"].value
      };

      const response = await fetch("/reset-password", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });

      const result = await response.json();
      alert(result.message || "Письмо отправлено");
      closeAll();
    };
  }

});

// -------------------------
// ЗАПОМНИТЬ МЕНЯ
// -------------------------
window.addEventListener("DOMContentLoaded", () => {
  const savedEmail = localStorage.getItem("userEmail");
  const form = document.getElementById('loginForm');

  if (savedEmail && form) {
    form.elements["email"].value = savedEmail;
    if (form.elements["rememberMe"]) {
      form.elements["rememberMe"].checked = true;
    }
  }
});
