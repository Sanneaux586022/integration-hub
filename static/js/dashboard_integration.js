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

document.addEventListener("DOMContentLoaded", loadChart, );