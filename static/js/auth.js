// Questo script gira su OGNI pagina protetta (come la Dashboard)
document.addEventListener('DOMContentLoaded', () => {
    console.log("Auth.js caricato!");
    // 1. Controlla se l'utente è loggato
    const isLoggedIn = localStorage.getItem('isLoggedIn');

    // 2. Se non è loggato e NON si trova già nella pagina di login, lo cacciamo
    // Usiamo .includes per capire se l'URL attuale contiene 'login.html' o 'register.html'
    const isAuthPage = window.location.pathname.includes('login.html') || 
                       window.location.pathname.includes('register.html');

    if (isLoggedIn !== 'true' && !isAuthPage) {
        alert("Accesso negato! Devi prima effettuare il login.");
        window.location.href = "/login";
        return; // Interrompe l'esecuzione del resto dello script
    }

    // 3. Gestione automatica del Logout (se il tasto esiste nella pagina)
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.onclick = (e) => {
            e.preventDefault();
            localStorage.removeItem('isLoggedIn'); // Rimuoviamo il "permesso"
            localStorage.removeItem('currentUser'); // Puliamo i dati utente
            window.location.href = "/login";
        };
    }
});