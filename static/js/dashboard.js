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
                    borderWith: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRation: false,
                scales: {
                    y: {beginAtZero: false}
                }
            }
        })
    } catch (error){
        console.error("Error nel caricamento del grafico: ", error);
    }
}

document.addEventListener("DOMContentLoaded", loadChart);