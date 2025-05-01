// ===========================================================
// 📊 charts.js — Funciones de renderizado de gráficos Chart.js
// ===========================================================


// ===========================================================
// 🔁 Función base para crear o actualizar un gráfico
// ===========================================================
export function renderChart(chart, element, type, labels, data, options) {
    if (chart) chart.destroy();
    return new Chart(element, {
        type,
        data: { labels, datasets: data },
        options
    });
}


// ===========================================================
// 🟢 1. Distribución de Sentimientos (Gráfico de Torta)
// ===========================================================
export function renderSentimentDistributionChart(data, ctx, currentChart) {
    const chartData = [{
        data: [data.positive, data.neutral, data.negative],
        backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
    }];

    return renderChart(currentChart, ctx, 'pie', ['Positivo', 'Neutral', 'Negativo'], chartData, {
        responsive: true,
        plugins: { legend: { position: 'top' } }
    });
}


// ===========================================================
// 🔵 2. Sentimiento Promedio por Mes (Gráfico de Línea)
// ===========================================================
export function renderAverageSentimentChart(dataArray, ctx, currentChart) {
    const chartData = [{
        label: 'Sentimiento Promedio',
        data: dataArray.map(d => d.averageSentiment),
        borderColor: '#1E90FF',
        fill: false
    }];

    return renderChart(currentChart, ctx, 'line', dataArray.map(d => d.date), chartData, {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                suggestedMin: -2,
                suggestedMax: 2
            }
        }
    });
}


// ===========================================================
// 🔴 3. Varianza del Sentimiento por Mes (Gráfico de Barras)
// ===========================================================
export function renderVarianceSentimentChart(dataArray, ctx, currentChart) {
    const chartData = [{
        label: 'Varianza del Sentimiento',
        data: dataArray.map(d => d.variance),
        backgroundColor: '#FF6347'
    }];

    return renderChart(currentChart, ctx, 'bar', dataArray.map(d => d.date), chartData, {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                suggestedMax: 2
            }
        }
    });
}


// ===========================================================
// 🟩 4. Tendencia de Comentarios Positivos (Gráfico de Línea)
// ===========================================================
export function renderPositiveTrendChart(dataArray, ctx, currentChart) {
    const chartData = [{
        label: 'Tendencia de Comentarios Positivos',
        data: dataArray.map(d => d.averageSentiment > 0 ? d.averageSentiment : 0),
        borderColor: '#4CAF50',
        fill: false
    }];

    return renderChart(currentChart, ctx, 'line', dataArray.map(d => d.date), chartData, {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    });
}


// ===========================================================
// 🟣 5. Usuarios por Rango de Edad (Gráfico de Barras)
// ===========================================================
export function renderUserStatsChart(usersData, ctx, currentChart) {
    const ageGroups = {
        "18-25": 0,
        "26-35": 0,
        "36-45": 0,
        "46-60": 0,
        "60+": 0
    };

    usersData.forEach(user => {
        const age = user.age;
        if (age >= 18 && age <= 25) ageGroups["18-25"]++;
        else if (age >= 26 && age <= 35) ageGroups["26-35"]++;
        else if (age >= 36 && age <= 45) ageGroups["36-45"]++;
        else if (age >= 46 && age <= 60) ageGroups["46-60"]++;
        else ageGroups["60+"]++;
    });

    const chartData = [{
        label: 'Cantidad de Usuarios',
        data: Object.values(ageGroups),
        backgroundColor: ['#4B0082', '#1E90FF', '#FF6347', '#FFC107', '#A9A9A9']
    }];

    return renderChart(currentChart, ctx, 'bar', Object.keys(ageGroups), chartData, {
        responsive: true,
        scales: { y: { beginAtZero: true } },
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: `Total Usuarios: ${usersData.length}` }
        }
    });
}
