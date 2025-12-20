
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date();
    const confDate = new Date('2025-05-10');

    if (
        today.getFullYear() === confDate.getFullYear() &&
        today.getMonth() === confDate.getMonth() &&
        today.getDate() === confDate.getDate()
    ) {
        document.querySelectorAll('.hall-btn').forEach(btn => {
            btn.classList.remove('disabled');
            btn.onclick = () => {
                window.open('https://zoom.us', '_blank');
            };
        });
    }
});

document.getElementById("download-btn").addEventListener("click", function () {
    window.location.href = "/download/program-pdf";  // This triggers the PDF download
});