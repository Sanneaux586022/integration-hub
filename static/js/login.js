document.addEventListener('DOMContentLoaded', () => {
    // Selezioniamo il form e gli input
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');

    // --- 1. Gestione Visibilità Password ---
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            togglePassword.textContent = isPassword ? '🙈' : '👁️';
        });
    }

    // --- 2. Logica di Accesso ---
    if (loginForm) {
        loginForm.onsubmit = (e) => {
            e.preventDefault(); // Evita il refresh della pagina

            const emailValue = emailInput.value;
            const passwordValue = passwordInput.value;

            // Recuperiamo l'eventuale utente registrato
            const savedUser = JSON.parse(localStorage.getItem('userCredentials'));

            // Credenziali admin di test
            const adminUser = "Sanneaux";
            const adminPass = "12345";

            // Controllo incrociato
            const isSavedUser = savedUser && usernameValue === savedUser.username && passwordValue === savedUser.password;
            const isAdmin = usernameValue === adminUser && passwordValue === adminPass;

            if (isSavedUser || isAdmin) {
                // Salviamo lo stato di login
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('currentUser', usernameValue);

                alert("Accesso autorizzato!");
                window.location.href = "/dashboard"; // Assicurati che il percorso sia corretto
            } else {
                alert("Username o Password non validi!");
            }
        };
    }
});