document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('application-form');
    const notification = document.getElementById('notification');
    if (!form) return;

    const USER_LOGGED_IN = form.dataset.loggedIn === "true";

    const roleButtons = document.querySelectorAll('.role-btn');
    const listenerFields = document.getElementById('listener-fields');
    const speakerFields = document.getElementById('speaker-fields');
    const roleInput = document.querySelector('input[name="role"]');

    /* ================= ROLE SWITCH ================= */

    roleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            roleButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const role = btn.dataset.role;
            roleInput.value = role;

            if (role === 'listener') {
                listenerFields.classList.remove('hidden');
                speakerFields.classList.add('hidden');
            } else {
                speakerFields.classList.remove('hidden');
                listenerFields.classList.add('hidden');
            }
        });
    });

    /* ================= FORM SUBMIT ================= */

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!USER_LOGGED_IN) {
            showNotification("❌ Требуется авторизация", "error");
            return;
        }

        const formData = new FormData(form);
        const data = {};
        formData.forEach((v, k) => data[k] = v);

        try {
            const res = await fetch('/application/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (!res.ok) {
                showNotification(result.message || "❌ Ошибка отправки", "error");
                return;
            }

            /* ===== SUCCESS ===== */

            showNotification("✅ Заявка успешно отправлена!", "success");

            // На всякий случай блокируем повторную отправку
            form.querySelector('button[type="submit"]').disabled = true;

            // Перезагрузка страницы через 1.5 сек
            setTimeout(() => {
                window.location.reload();
            }, 1500);

        } catch (err) {
            console.error(err);
            showNotification("❌ Ошибка отправки. Попробуйте позже.", "error");
        }
    });

    /* ================= NOTIFICATION ================= */

    function showNotification(msg, type = "info") {
        notification.textContent = msg;
        notification.className = `notification ${type} show`;

        setTimeout(() => {
            notification.className = "notification";
        }, 5000);
    }
});
