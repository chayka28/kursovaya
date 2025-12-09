document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("newPasswordForm");

    form.onsubmit = async e => {
        e.preventDefault();

        const password = document.getElementById("password").value;
        const confirm = document.getElementById("password_confirm").value;
        const token = document.getElementById("token").value;

        if (password !== confirm) {
            alert("Пароли не совпадают!");
            return;
        }

        const response = await fetch("/reset-confirm", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ token: token, new_password: password })
        });

        const result = await response.json();
        alert(result.message);

        if (response.ok) {
            window.location.href = "/";
        }
    };
});
