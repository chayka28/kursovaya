document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contact-form");
  const notification = document.getElementById("notification");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      name: form.name.value,
      email: form.email.value,
      message: form.message.value,
    };

    try {
      const res = await fetch("/contact/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (res.ok) {
        notification.textContent = result.message;
        notification.className = "notification success";
        notification.style.display = "block";
        form.reset();
      } else {
        notification.textContent = result.message || "Ошибка отправки";
        notification.className = "notification error";
        notification.style.display = "block";
      }
    } catch (err) {
      notification.textContent = "Ошибка сети";
      notification.className = "notification error";
      notification.style.display = "block";
    }

    // Скрыть уведомление через 5 секунд
    setTimeout(() => {
      notification.style.display = "none";
    }, 5000);
  });

  // === Яндекс.Карта ===
  ymaps.ready(() => {
    const map = new ymaps.Map("map", {
      center: [51.6625, 39.2000], // Воронеж
      zoom: 10
    });

    const placemark = new ymaps.Placemark([51.6625, 39.2000], {
      balloonContent: "г. Воронеж"
    });

    map.geoObjects.add(placemark);
  });
});
