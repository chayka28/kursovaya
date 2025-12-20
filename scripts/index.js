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
