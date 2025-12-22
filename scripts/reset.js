document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("newPasswordForm");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("password_confirm");
    const strengthBar = document.getElementById("strength-bar");

    // контейнер для уведомлений
    const resultContainer = document.getElementById("result");
    if (resultContainer) {
        resultContainer.style.marginBottom = "10px";
        resultContainer.style.fontWeight = "500";
    }

    const rules = {
        length: v => v.length >= 8,
        letter: v => /[a-zA-Z]/.test(v),
        digit: v => /\d/.test(v),
        special: v => /[!@#$%^&*]/.test(v)
    };

    passwordInput.addEventListener("input", () => {
        const value = passwordInput.value;
        let passed = 0;

        // проверяем правила только внутри формы
        Object.entries(rules).forEach(([key, check]) => {
            const el = form.querySelector(`[data-rule="${key}"]`);
            if (!el) return;
            if (check(value)) {
                el.classList.add("valid");
                el.classList.remove("invalid");
                passed++;
            } else {
                el.classList.add("invalid");
                el.classList.remove("valid");
            }
        });

        // обновляем прогресс-бар
        strengthBar.style.width = `${passed * 25}%`;
        strengthBar.classList.remove("medium", "strong");
        if (passed >= 3) strengthBar.classList.add("medium");
        if (passed === 4) strengthBar.classList.add("strong");
    });

    form.onsubmit = async e => {
        e.preventDefault();

        const password = passwordInput.value;
        const confirm = confirmInput.value;
        const token = document.getElementById("token").value;

        // проверка совпадения паролей
        if (password !== confirm) {
            if (resultContainer) {
                resultContainer.textContent = "Пароли не совпадают!";
                resultContainer.style.color = "#ef4444";
                setTimeout(() => resultContainer.textContent = "", 5000);
            }
            return;
        }

        // проверка силы пароля
        if (!strengthBar.classList.contains("strong")) {
            if (resultContainer) {
                resultContainer.textContent = "Пароль недостаточно надёжный!";
                resultContainer.style.color = "#ef4444";
                setTimeout(() => resultContainer.textContent = "", 5000);
            }
            return;
        }

        const response = await fetch("/reset-confirm", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ token: token, new_password: password })
        });

        const result = await response.json();

        if (resultContainer) {
            resultContainer.textContent = result.message || "Пароль успешно изменён";
            resultContainer.style.color = response.ok ? "#10b981" : "#ef4444";
            if (response.ok) {
                setTimeout(() => { window.location.href = "/"; }, 2000);
            } else {
                setTimeout(() => resultContainer.textContent = "", 5000);
            }
        }
    };
});
