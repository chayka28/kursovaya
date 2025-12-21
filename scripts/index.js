// Countdown Timer
var countDownDate = new Date("May 10, 2026 00:00:00").getTime();

var x = setInterval(function() {
  var now = new Date().getTime();
  var distance = countDownDate - now;

  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  document.getElementById("countdown-timer").innerHTML = days + "d " + hours + "h "
    + minutes + "m " + seconds + "s ";

  if (distance < 0) {
    clearInterval(x);
    document.getElementById("countdown-timer").innerHTML = "EXPIRED";
  }
}, 1000);

// Handle Topic Card Click
const topicCards = document.querySelectorAll('.topic-card');

topicCards.forEach(card => {
  card.addEventListener('click', function() {
    // Hide all cards
    document.querySelectorAll('.topic-card').forEach(card => card.classList.remove('active'));
    
    // Show description of the selected card
    card.classList.add('active');
  });
});

// ===== Random thesis background =====
(async function loadBackgroundTheses() {
  try {
    const res = await fetch('/api/theses/random');
    if (!res.ok) return;

    const theses = await res.json();
    const container = document.getElementById('thesis-background');

    theses.forEach(t => {
      const el = document.createElement('div');
      el.className = 'thesis-bg-item';
      el.style.left = Math.random() * 80 + '%';
      el.style.animationDuration = (30 + Math.random() * 30) + 's';
      el.style.animationDelay = (-Math.random() * 20) + 's';

      el.innerHTML = `
        <strong>${t.title}</strong>
        ${t.abstract.slice(0, 160)}…
      `;

      container.appendChild(el);
    });

  } catch (e) {
    console.error('Ошибка загрузки тезисов', e);
  }
})();
