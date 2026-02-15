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
        loginForm.onsubmit = async (e) => {
            e.preventDefault(); // Evita il refresh della pagina
            const payload = {
                email: emailInput.value,
                plain_password: passwordInput.value
            }

            try {
                const response = await fetch('api/v1/login', {
                    method: 'POST',
                    headers: {
                        'Content-type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const result = await response.json();

                    // Il server ha restituito il token nel JSON,
                    // ma noi vogliamo che sia salvato nei Cookies per la dashboard.
                    // Lo facciamo vis JS se il server non lo ha già impostato:
                    document.cookie = `access_token=${result.access_token}; path=/; SameSite=Lax`;
                    alert('Accesso autorizzato!');
                    window.location.href = '/dashboard';
                } else {
                    const errorData = await response.json();
                    console.log("Errore 422o simile : ", errorData);
                    alert('Credenziali non valide o errore formato dati');
                }

            } catch(error) {
                console.error('Errore di rete');
            }

        };
    }
});