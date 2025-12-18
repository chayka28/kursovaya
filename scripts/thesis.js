document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('thesis-form');
    const notification = document.getElementById('notification');
    const counter = document.getElementById('thesis-counter');
    const submitBtn = document.getElementById('submit-thesis');

    if(!form) return;

    // Инициализация счетчика
    let currentCount = parseInt(counter.textContent.match(/\d+/)?.[0] || 0);
    if(currentCount >= 5) submitBtn.disabled = true;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            title: form.title.value,
            abstract: form.abstract.value
        };

        try {
            const response = await fetch('/thesis/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if(response.ok){
                // Зеленое уведомление
                notification.textContent = "✅ Тезис успешно отправлен!";
                notification.style.color = "green";
                form.reset();

                currentCount++;
                counter.textContent = `Вы отправили ${currentCount} / 5 тезисов`;

                if(currentCount >= 5){
                    submitBtn.disabled = true;
                    counter.textContent = "❌ Достигнут лимит 5 тезисов";
                }

            } else {
                // Красное уведомление
                notification.textContent = "❌ " + (result.message || result.error);
                notification.style.color = "red";

                if(result.message && result.message.includes("не более 5")){
                    submitBtn.disabled = true;
                    counter.textContent = "❌ Достигнут лимит 5 тезисов";
                }
            }

            notification.classList.add('show');
            setTimeout(() => notification.classList.remove('show'), 5000);

        } catch (err) {
            notification.textContent = "❌ Ошибка отправки. Попробуйте позже.";
            notification.style.color = "red";
            notification.classList.add('show');
            setTimeout(() => notification.classList.remove('show'), 5000);
        }
    });
});
