async function loadChart() {
    try {

        const response = await fetch("/api/v1/weather/history");
        const data = await response.json()

        const labels = data.map(d => d.time);
        const temps = data.map(d => d.temp);
        const ctx = document.getElementById("weatherChart").getContext("2d");
        new Chart (ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Temperatura °C",
                    data: temps,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {beginAtZero: false}
                }
            }
        });
    } catch (error){
        console.error("Error nel caricamento del grafico: ", error);
    }
}
async function refreshData(endpoint, buttonId){
    const btn = document.getElementById(buttonId);

    if(!btn) {
        console.error("Errore: Bottone non trovato con ID: ", buttonId);
        return;
    }

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>...';

    try {
        const response = await fetch(`/api/v1/${endpoint}`);
        if (response.ok) {
            alert("Dati aggiornati con successo!");
            location.reload();
        } else {
            alert("Errore durante l'aggiornamento.");
        }
    } catch(error){
        console.error("Errore : ", error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }

}

document.addEventListener('DOMContentLoaded', () => {
    loadChart();
    // --- 1. SELEZIONE ELEMENTI ---
    const modal = document.getElementById('projectModal');
    const openBtn = document.getElementById('openModal'); // Il tasto accanto alla ricerca
    const closeBtn = document.getElementById('closeBtn');
    const closeIcon = document.querySelector('.close-modal');
    const projectForm = document.getElementById('projectForm');
    
    const searchInput = document.getElementById('search');
    const projectCards = document.querySelectorAll('.card');

    // --- 2. GESTIONE MODALE (Apertura/Chiusura) ---
    if (openBtn && modal) {
        openBtn.onclick = () => {
            modal.style.display = 'flex';
        };

        const closeModal = () => {
            modal.style.display = 'none';
        };

        if (closeBtn) closeBtn.onclick = closeModal;
        if (closeIcon) closeIcon.onclick = closeModal;

        // Chiudi se clicchi fuori dal rettangolo bianco
        window.onclick = (event) => {
            if (event.target == modal) closeModal();
        };
    }

    // --- 3. LOGICA DI RICERCA (Filtro Card) ---
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const searchText = searchInput.value.toLowerCase();

            projectCards.forEach(card => {
                // Cerchiamo il testo dentro l'H3 della card
                const title = card.querySelector('h3').innerText.toLowerCase();
                
                if (title.includes(searchText)) {
                    card.style.display = "block"; // Mostra
                } else {
                    card.style.display = "none";  // Nascondi
                }
            });
        });
    }

    // --- 4. INVIO FORM (Verso il Raspberry) ---
    if (projectForm) {
        projectForm.onsubmit = (e) => {
            e.preventDefault();

            // Recupero valori dal form
            const payload = {
                projectName: document.getElementById('projectName').value,
                technology: document.getElementById('techStack').value,
                extraParams: document.getElementById('extraParams').value,
                timestamp: new Date().toISOString(),
                owner: localStorage.getItem('currentUser') || 'S\'anneaux'
            };

            console.log("🚀 Payload pronto per il Raspberry:", payload);
            
            // FEEDBACK UTENTE
            alert(`Avvio automazione per il progetto: ${payload.projectName}\nTecnologia: ${payload.technology}`);

            // TODO: Qui inseriremo la chiamata fetch() reale domani
            // fetch('http://IP_RASPBERRY:5000/api/create-project', { method: 'POST', body: JSON.stringify(payload) })

            projectForm.reset(); // Svuota il form
            modal.style.display = 'none'; // Chiudi il modale
        };
    }
});