document.addEventListener('DOMContentLoaded', function () {
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
});
