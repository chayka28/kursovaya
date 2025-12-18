document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('application-form');
    const notification = document.getElementById('notification');
    if (!form) return;

    const USER_LOGGED_IN = form.dataset.loggedIn === "true";

    const roleButtons = document.querySelectorAll('.role-btn');
    const listenerFields = document.getElementById('listener-fields');
    const speakerFields = document.getElementById('speaker-fields');
    const roleInput = document.querySelector('input[name="role"]');

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

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!USER_LOGGED_IN) {
            showNotification("❌ Требуется авторизация");
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
                showNotification(result.message || "❌ Ошибка отправки");
                return;
            }

            showNotification("✅ Заявка успешно отправлена!");
            form.reset();
        } catch (err) {
            showNotification("❌ Ошибка отправки. Попробуйте позже.");
        }
    });

    function showNotification(msg) {
        notification.textContent = msg;
        notification.classList.add('show');
        setTimeout(() => notification.classList.remove('show'), 5000);
    }
});