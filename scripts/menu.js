document.addEventListener('DOMContentLoaded', () => {
  const loginModal = document.getElementById('loginModal');
  const registerModal = document.getElementById('registerModal');
  const resetModal = document.getElementById('resetModal');
  const loginBtn = document.getElementById('loginBtn');
  const registerBtn = document.getElementById('registerBtn');
  const forgotLink = document.getElementById('forgotPasswordLink');

  const closeButtons = document.querySelectorAll('.close');
  const modals = [loginModal, registerModal, resetModal];

  // Открытие модалок
  loginBtn.onclick = () => openModal(loginModal);
  registerBtn.onclick = () => openModal(registerModal);
  forgotLink.onclick = () => {
    closeAll();
    openModal(resetModal);
  };

  // Закрытие
  closeButtons.forEach(btn => btn.onclick = () => closeAll());
  window.onclick = e => { if (modals.includes(e.target)) closeAll(); };

  function openModal(modal) {
    modal.style.display = 'flex';
  }
  function closeAll() {
    modals.forEach(m => m.style.display = 'none');
  }
//##################
//#обработчики форм#
//##################
  
  // Вход
  document.getElementById('loginForm').onsubmit = async e => {
    e.preventDefault();
    
    const form = e.target;
    const data = {
      email: form.elements["email"].value,
      password: form.elements["password"].value
    };

    const remember = form.elements["rememberMe"]?.checked;

    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    const result = await response.json();
    alert(result.message || "Авторизация успешна!");
    closeAll();

    if (response.ok && remember) {
      localStorage.setItem("userEmail", data.email);
    } else {
      localStorage.removeItem("userEmail");
    }
  };

  // Регистрация
  document.getElementById('registerForm').onsubmit = async e => {
    e.preventDefault();
    
    const form = e.target;
    const data = {
      fullname: form.elements["fullname"].value,
      email: form.elements["email"].value,
      password: form.elements["password"].value
    };

    const response = await fetch("http://127.0.0.1:8000/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    const result = await response.json();
    alert(result.message || "Регистрация прошла успешно!")
    closeAll();
  };


  // Восстановление
  document.getElementById('resetForm').onsubmit = async e => {
    e.preventDefault();
    
    const form = e.target;
    const data = {
      email: form.elements["email"].value
    };

    const response = await fetch("http://127.0.0.1:8000/reset-password", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });


    const result = await response.json();
    alert(result.message || "Письмо для восстановление пароля отправлено!");
    closeAll();
  };
});

// Запомнить меня

  window.addEventListener("DOMContentLoaded", () => {
    const savedEmail = localStorage.getItem("userEmail");
    if (savedEmail) {
      const form = document.getElementById('loginForm');
      form.elements["email"].value = savedEmail;
      if (form.elements["rememverMe"]){
        form.elements["rememberMe"].checked = true;
      }
    }
  })
