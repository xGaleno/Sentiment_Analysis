document.addEventListener('DOMContentLoaded', async () => {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

    const sentimentDistributionChartElement = document.getElementById('sentimentDistributionChart').getContext('2d');
    const averageSentimentChartElement = document.getElementById('averageSentimentChart').getContext('2d');
    const varianceSentimentChartElement = document.getElementById('varianceSentimentChart').getContext('2d');
    const nuevoGraficoElement = document.getElementById('nuevoGrafico').getContext('2d');
    const tercerGraficoElement = document.getElementById('tercerGrafico').getContext('2d');

    let comments = [];
    let usersData = [];
    let allCommentsData = [];
    let sentimentDistributionChart, averageSentimentChart, varianceSentimentChart, nuevoGrafico, tercerGrafico;
    let selectedYears = new Set();

    document.querySelectorAll('.year-filter button.selected').forEach(btn => {
        selectedYears.add(btn.id);
    });

    async function fetchCommentsData() {
        try {
            const response = await fetch(`${API_BASE_URL}/comments`);
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            comments = await response.json();
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
            const sentimientoRaw = comment.sentiment || comment.sentimiento;
            const timestampRaw = comment.timestamp;

            if (!sentimientoRaw || !timestampRaw) return;

            const sentiment = sentimientoRaw.toLowerCase().trim() === 'positivo' ? 'positive' :
                              sentimientoRaw.toLowerCase().trim() === 'neutro'   ? 'neutral'  :
                              'negative';

            const sentimentScore = sentiment === "positive" ? 1 : sentiment === "neutral" ? 0 : -1;
            sentiments[sentiment] = (sentiments[sentiment] || 0) + 1;

            const date = new Date(timestampRaw);
            if (isNaN(date.getTime())) return;

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
        nuevoGrafico = renderChart(
            nuevoGrafico, nuevoGraficoElement, 'line',
            averageSentimentByMonth.map(data => data.date), chartData,
            { responsive: true, scales: { y: { beginAtZero: true } } }
        );
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

        const chartData = [{
            label: 'Cantidad de Usuarios',
            data: Object.values(ageGroups),
            backgroundColor: ['#4B0082', '#1E90FF', '#FF6347', '#FFC107', '#A9A9A9']
        }];

        const labels = Object.keys(ageGroups);

        tercerGrafico = renderChart(
            tercerGrafico, tercerGraficoElement, 'bar',
            labels, chartData,
            {
                responsive: true,
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { position: 'top' }, title: { display: true, text: `Total Usuarios: ${totalUsers}` } }
            }
        );
    }

    function renderUsersTable(users) {
        const usersTableBody = document.querySelector('#usersTable tbody');
        usersTableBody.innerHTML = '';

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${user.email}</td>`;
            row.addEventListener('click', () => showChatHistory(user.email));
            usersTableBody.appendChild(row);
        });
    }

    function showChatHistory(userEmail) {
        const chatHistorySection = document.querySelector('.chat-history-section');
        const chatHistoryContainer = document.getElementById('chatHistoryContainer');
        chatHistoryContainer.innerHTML = '';

        const userComments = allCommentsData.filter(comment => comment.usuario === userEmail);

        if (userComments.length === 0) {
            chatHistoryContainer.innerHTML = '<p>No hay historial de chat disponible para este usuario.</p>';
        } else {
            userComments.forEach(comment => {
                const pregunta = comment.pregunta || '(Pregunta no disponible)';
                const respuesta = comment.respuesta || '(Respuesta no disponible)';
                const block = document.createElement('div');
                block.innerHTML = `<p><strong>Pregunta:</strong> ${pregunta}</p><p><strong>Respuesta:</strong> ${respuesta}</p><hr>`;
                chatHistoryContainer.appendChild(block);
            });
        }

        chatHistorySection.style.display = 'block';
    }

    // === FLUJO PRINCIPAL de carga ===

    comments = await fetchCommentsData();
    if (comments.length > 0) {
        const { sentiments, averageSentimentByMonth } = processCommentsData(comments);
        renderSentimentDistributionChart(sentiments);
        renderAverageSentimentChart(averageSentimentByMonth);
        renderVarianceSentimentChart(averageSentimentByMonth);
        renderPositiveTrendChart(averageSentimentByMonth);
    }

    usersData = await fetchUsersData();
    allCommentsData = comments;
    renderUsersTable(usersData);
    renderUserStatsChart(usersData);

    // === Botón Cerrar Sesión ===
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('empresa_id');
            localStorage.removeItem('empresa_name');
            window.location.href = '/frontend/pages/empresa_login.html';
        });
    }

    
    // === GESTIÓN DE BOTONES DE AÑO ===
    const yearButtons = ['2023', '2024', '2025'].map(y => document.getElementById(y));
    yearButtons.forEach(button => {
        button.addEventListener('click', () => {
            const year = button.id;
            if (selectedYears.has(year)) {
                selectedYears.delete(year);
                button.classList.remove('selected');
            } else {
                selectedYears.add(year);
                button.classList.add('selected');
            }
            actualizarGraficosPorAño();
        });
    });

    function actualizarGraficosPorAño() {
        const filtrados = allCommentsData.filter(c => {
            const fecha = new Date(c.timestamp);
            return !isNaN(fecha.getTime()) && selectedYears.has(fecha.getFullYear().toString());
        });

        const procesado = processCommentsData(filtrados);
        renderSentimentDistributionChart(procesado.sentiments);
        renderAverageSentimentChart(procesado.averageSentimentByMonth);
        renderVarianceSentimentChart(procesado.averageSentimentByMonth);
        renderPositiveTrendChart(procesado.averageSentimentByMonth);
    }


    // === Botón Actualizar Datos ===
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            location.reload();  // Recarga toda la página
        });
    }

    const exportCSVButton = document.getElementById('exportCSVButton');
    if (exportCSVButton) {
        exportCSVButton.addEventListener('click', async () => {
            try {
                const response = await fetch('http://localhost:5000/api/comments');
                if (!response.ok) throw new Error('Error al obtener comentarios');
                
                const comentarios = await response.json();
                
                // Encabezado del CSV
                let csvRows = [
                    ["Comentario", "Fecha", "Correo", "Edad"]
                ];
    
                comentarios.forEach(row => {
                    csvRows.push([
                        (row.respuesta || '').replace(/"/g, '""'),  // Escapa comillas internas
                        row.timestamp || '',
                        row.usuario || '',
                        row.edad || 'Desconocida'
                    ]);
                });


    const generatePDFButton = document.getElementById('generatePDFButton');
    if (generatePDFButton) {
        generatePDFButton.addEventListener('click', async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/generate_report`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ comentarios: allCommentsData })
                });
                if (!response.ok) throw new Error('No se pudo generar el reporte PDF');
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'reporte_comentarios.pdf';
                link.click();
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error al generar el PDF:', error);
                alert('Hubo un problema al generar el PDF.');
            }
        });
    }

    
                // Formato CSV listo
                const csvContent = csvRows.map(e => e.map(item => `"${item}"`).join(",")).join("\n");
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
    
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", "comentarios_ordenados.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exportando comentarios:', error);
                alert('No se pudo exportar los comentarios.');
            }
        });
    }

    

});
