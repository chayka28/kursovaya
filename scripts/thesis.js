document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('thesis-form');
    if (!form) return;

    const notification = document.getElementById('notification');
    const counter = document.getElementById('thesis-counter');
    const submitBtn = document.getElementById('submit-thesis');

    let currentCount = parseInt(form.dataset.thesisCount || 0, 10);
    const userRole = form.dataset.userRole;

    /* ===== SAFETY CHECK ===== */
    if (userRole !== 'speaker') {
        show("❌ Отправка тезисов доступна только докладчикам", "error");
        submitBtn.disabled = true;
        return;
    }

    if (currentCount >= 5) {
        submitBtn.disabled = true;
        counter.textContent = "❌ Достигнут лимит 5 тезисов";
        return;
    }

    /* ===== SUBMIT ===== */
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        submitBtn.disabled = true;

        const data = {
            title: form.title.value.trim(),
            abstract: form.abstract.value.trim()
        };

        try {
            const res = await fetch('/thesis/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (!res.ok) {
                show("❌ " + (result.message || "Ошибка отправки"), "error");
                submitBtn.disabled = false;
                return;
            }

            /* SUCCESS */
            currentCount++;
            form.reset();

            show("✅ Тезис успешно отправлен!", "success");

            if (currentCount >= 5) {
                counter.textContent = "❌ Достигнут лимит 5 тезисов";
                submitBtn.disabled = true;
            } else {
                counter.textContent = `Вы отправили ${currentCount} / 5 тезисов`;
                submitBtn.disabled = false;
            }

        } catch (err) {
            show("❌ Ошибка отправки. Попробуйте позже.", "error");
            submitBtn.disabled = false;
        }
    });

    function show(text, type) {
        notification.textContent = text;
        notification.className = `notification ${type}`;
        notification.style.display = "block";

        setTimeout(() => {
            notification.style.display = "none";
        }, 5000);
    }
});
