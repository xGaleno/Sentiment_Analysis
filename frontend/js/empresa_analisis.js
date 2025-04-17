document.addEventListener('DOMContentLoaded', async () => {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

    const sentimentDistributionChartElement = document.getElementById('sentimentDistributionChart').getContext('2d');
    const averageSentimentChartElement = document.getElementById('averageSentimentChart').getContext('2d');
    const varianceSentimentChartElement = document.getElementById('varianceSentimentChart').getContext('2d');
    const nuevoGraficoElement = document.getElementById('nuevoGrafico').getContext('2d');

    let comments = [];
    let sentimentDistributionChart, averageSentimentChart, varianceSentimentChart, nuevoGrafico;
    let selectedYears = new Set();

    async function fetchCommentsData() {
        try {
            const response = await fetch(`${API_BASE_URL}/comments`);
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            comments = await response.json();
            console.log("Comentarios obtenidos:", comments);
            return comments;
        } catch (error) {
            console.error("Failed to fetch comments data:", error);
            return [];
        }
    }

    async function fetchUsersData() {
        try {
            const response = await fetch(`${API_BASE_URL}/users`);
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            return await response.json();
        } catch (error) {
            console.error("Failed to fetch users data:", error);
            return [];
        }
    }

    function processCommentsData(comments) {
        const sentiments = { positive: 0, neutral: 0, negative: 0 };
        const averageSentimentData = {};

        comments.forEach(comment => {
            let sentiment = comment.sentiment.toLowerCase().trim();
            sentiment = sentiment === 'positivo' ? 'positive' :
                       sentiment === 'neutro' ? 'neutral' : 'negative';
            const sentimentScore = sentiment === "positive" ? 1 : sentiment === "neutral" ? 0 : -1;

            sentiments[sentiment] = (sentiments[sentiment] || 0) + 1;

            const date = new Date(comment.timestamp);
            const monthKey = `${date.getFullYear()}-${date.toLocaleString('default', { month: 'long' })}`;

            if (!averageSentimentData[monthKey]) {
                averageSentimentData[monthKey] = { totalScore: 0, count: 0, scores: [] };
            }
            averageSentimentData[monthKey].totalScore += sentimentScore;
            averageSentimentData[monthKey].count += 1;
            averageSentimentData[monthKey].scores.push(sentimentScore);
        });

        const averageSentimentByMonth = Object.keys(averageSentimentData).map(month => {
            const data = averageSentimentData[month];
            const average = data.totalScore / data.count;
            const variance = data.scores.reduce((acc, score) => acc + Math.pow(score - average, 2), 0) / data.count;
            return { date: month, averageSentiment: average, variance: variance };
        });

        return { sentiments, averageSentimentByMonth };
    }

    function renderChart(chart, element, type, labels, data, options) {
        if (chart) chart.destroy();
        return new Chart(element, { type, data: { labels, datasets: data }, options });
    }

    function renderSentimentDistributionChart(data) {
        const chartData = [{
            data: [data.positive, data.neutral, data.negative],
            backgroundColor: ['#4CAF50', '#FFC107', '#F44336']
        }];
        sentimentDistributionChart = renderChart(
            sentimentDistributionChart, sentimentDistributionChartElement, 'pie',
            ['Positivo', 'Neutral', 'Negativo'], chartData, { responsive: true, plugins: { legend: { position: 'top' } } }
        );
    }

    function renderAverageSentimentChart(averageSentimentByMonth) {
        const chartData = [{
            label: 'Sentimiento Promedio',
            data: averageSentimentByMonth.map(data => data.averageSentiment),
            borderColor: '#1E90FF',
            fill: false
        }];
        averageSentimentChart = renderChart(
            averageSentimentChart, averageSentimentChartElement, 'line',
            averageSentimentByMonth.map(data => data.date), chartData,
            { responsive: true, scales: { y: { beginAtZero: true, suggestedMin: -2, suggestedMax: 2 } } }
        );
    }

    function renderVarianceSentimentChart(averageSentimentByMonth) {
        const chartData = [{
            label: 'Varianza del Sentimiento',
            data: averageSentimentByMonth.map(data => data.variance),
            backgroundColor: '#FF6347'
        }];
        varianceSentimentChart = renderChart(
            varianceSentimentChart, varianceSentimentChartElement, 'bar',
            averageSentimentByMonth.map(data => data.date), chartData,
            { responsive: true, scales: { y: { beginAtZero: true, suggestedMax: 2 } } }
        );
    }

    function renderPositiveTrendChart(averageSentimentByMonth) {
        const positiveCommentsData = averageSentimentByMonth.map(data => data.averageSentiment > 0 ? data.averageSentiment : 0); 
        const chartData = [{
            label: 'Tendencia de Comentarios Positivos',
            data: positiveCommentsData,
            borderColor: '#4CAF50',
            fill: false
        }];
        const labels = averageSentimentByMonth.map(data => data.date);

        nuevoGrafico = renderChart(
            nuevoGrafico, nuevoGraficoElement, 'line',
            labels, chartData,
            { responsive: true, scales: { y: { beginAtZero: true } } }
        );
    }

    function filterByYears(years) {
        const filteredComments = comments.filter(comment =>
            years.includes(new Date(comment.timestamp).getFullYear())
        );
        const { sentiments, averageSentimentByMonth } = processCommentsData(filteredComments);
        renderSentimentDistributionChart(sentiments);
        renderAverageSentimentChart(averageSentimentByMonth);
        renderVarianceSentimentChart(averageSentimentByMonth);
        renderPositiveTrendChart(averageSentimentByMonth);
    }

    function toggleYearFilter(year, buttonId) {
        const button = document.getElementById(buttonId);
        if (selectedYears.has(year)) {
            selectedYears.delete(year);
            button.classList.remove('selected');
        } else {
            selectedYears.add(year);
            button.classList.add('selected');
        }
        filterByYears(Array.from(selectedYears));
    }

    document.getElementById('filter2023').addEventListener('click', () => toggleYearFilter(2023, 'filter2023'));
    document.getElementById('filter2024').addEventListener('click', () => toggleYearFilter(2024, 'filter2024'));

    const commentsData = await fetchCommentsData();
    if (commentsData.length > 0) {
        const { sentiments, averageSentimentByMonth } = processCommentsData(commentsData);
        renderSentimentDistributionChart(sentiments);
        renderAverageSentimentChart(averageSentimentByMonth);
        renderVarianceSentimentChart(averageSentimentByMonth);
        renderPositiveTrendChart(averageSentimentByMonth);
    } else {
        console.warn("No se obtuvieron comentarios para mostrar en los gráficos.");
    }

    async function fetchUsersData() {
        try {
            const response = await fetch(`${API_BASE_URL}/users`);    
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            const users = await response.json();
            return users;
        } catch (error) {
            console.error("Failed to fetch users data:", error);
            return [];
        }
    }

    function renderUserStatsChart(usersData) {
        const ageRanges = usersData.map(user => user.age);
        const totalUsers = usersData.length;
        const ageGroups = { "18-25": 0, "26-35": 0, "36-45": 0, "46-60": 0, "60+": 0 };

        ageRanges.forEach(age => {
            if (age >= 18 && age <= 25) ageGroups["18-25"] += 1;
            else if (age >= 26 && age <= 35) ageGroups["26-35"] += 1;
            else if (age >= 36 && age <= 45) ageGroups["36-45"] += 1;
            else if (age >= 46 && age <= 60) ageGroups["46-60"] += 1;
            else ageGroups["60+"] += 1;
        });

        const chartData = [
            {
                label: 'Cantidad de Usuarios',
                data: Object.values(ageGroups),
                backgroundColor: ['#4B0082', '#1E90FF', '#FF6347', '#FFC107', '#A9A9A9']
            }
        ];

        const labels = Object.keys(ageGroups);

        const tercerGraficoElement = document.getElementById('tercerGrafico').getContext('2d');
        renderChart(
            null,
            tercerGraficoElement,
            'bar',
            labels,
            chartData,
            {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: `Total Usuarios: ${totalUsers}` }
                }
            }
        );
    }


    
    const usersData = await fetchUsersData();
    renderUserStatsChart(usersData);

});
