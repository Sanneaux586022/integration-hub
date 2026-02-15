document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById("registerForm");
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('new-password');
    const errorMsg = document.getElementById('password-error');

    // --- 1. Toggle Visibilità Password (per entrambi i campi) ---
    const setupToggle = (toggleId, inputId) => {
        const toggle = document.getElementById(toggleId);
        const input = document.getElementById(inputId);
        if (toggle && input) {
            toggle.addEventListener('click', () => {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                toggle.textContent = isPassword ? '🙈' : '👁️';
            });
        }
    };

    setupToggle('togglePassword', 'password');
    setupToggle('toggleConfirmPassword', 'new-password');

    // --- 2. Controllo Password in tempo reale ---
    function checkPasswords() {
        if (confirmPassword.value === "") {
            errorMsg.style.display = "none";
            confirmPassword.style.borderColor = "#ccc";
            return;
        }

        if (password.value === confirmPassword.value) {
            errorMsg.style.display = "none";
            confirmPassword.style.borderColor = "rgb(2, 116, 11)"; // Verde S'anneaux
        } else {
            errorMsg.style.display = "block";
            confirmPassword.style.borderColor = "red";
        }
    }

    password.addEventListener('input', checkPasswords);
    confirmPassword.addEventListener('input', checkPasswords);

    // --- 3. Salvataggio Dati al Submit ---
    if (registerForm) {
        registerForm.onsubmit = (e) => {
            e.preventDefault();

            // Blocco se le password non corrispondono
            if (password.value !== confirmPassword.value) {
                alert("Le password non corrispondono!");
                return;
            }

            // Creiamo l'oggetto utente
            const newUser = {
                email: document.getElementById('email').value,
                username: document.getElementById('username').value,
                password: password.value
            };

            // Salviamo nel localStorage
            // Trasformiamo l'oggetto in stringa perché localStorage accetta solo stringhe
            localStorage.setItem('userCredentials', JSON.stringify(newUser));
            

            alert("Account creato con successo! Verrai reindirizzato al login.");
            window.location.href = "/login"; 
        };
    }
});