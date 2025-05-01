// ====================================================================
// 🧠 empresa_analisis.js — Inicialización de la vista de análisis
// ====================================================================

import {
    renderSentimentDistributionChart,
    renderAverageSentimentChart,
    renderVarianceSentimentChart,
    renderPositiveTrendChart,
    renderUserStatsChart
} from './charts.js';

import {
    fetchComments,
    fetchUsers,
    processCommentsData
} from './data_service.js';

import {
    renderUsersTable,
    renderChatHistory,
    initAgeFilter
} from './user_interface.js';

// ====================================================================
// 🚀 MAIN — Espera a que el DOM esté listo
// ====================================================================

document.addEventListener('DOMContentLoaded', async () => {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

    // 🎯 Contextos de los gráficos (canvas)
    const ctx = {
        sentiment: document.getElementById('sentimentDistributionChart').getContext('2d'),
        avg: document.getElementById('averageSentimentChart').getContext('2d'),
        var: document.getElementById('varianceSentimentChart').getContext('2d'),
        trend: document.getElementById('nuevoGrafico').getContext('2d'),
        users: document.getElementById('tercerGrafico').getContext('2d')
    };

    let allCommentsData = [];
    let selectedYears = new Set(['2023', '2024', '2025']);
    let charts = {};

    // ====================================================================
    // 📊 RENDERIZAR GRÁFICOS CON DATOS PROCESADOS
    // ====================================================================
    function updateCharts(data) {
        charts.sentiment = renderSentimentDistributionChart(data.sentiments, ctx.sentiment, charts.sentiment);
        charts.avg = renderAverageSentimentChart(data.averageSentimentByMonth, ctx.avg, charts.avg);
        charts.var = renderVarianceSentimentChart(data.averageSentimentByMonth, ctx.var, charts.var);
        charts.trend = renderPositiveTrendChart(data.averageSentimentByMonth, ctx.trend, charts.trend);
    }

    // ====================================================================
    // 📥 CARGA INICIAL DE DATOS
    // ====================================================================
    const comments = await fetchComments(API_BASE_URL);
    const users = await fetchUsers(API_BASE_URL);
    allCommentsData = comments;

    if (comments.length) {
        const processed = processCommentsData(comments);
        updateCharts(processed);
    }

    charts.users = renderUserStatsChart(users, ctx.users, charts.users);

    renderUsersTable(users, email => renderChatHistory(allCommentsData, email));

    initAgeFilter(filteredUsers => {
        renderUsersTable(filteredUsers, email => renderChatHistory(allCommentsData, email));
    });

    // ====================================================================
    // 🔐 CERRAR SESIÓN
    // ====================================================================
    document.getElementById('logoutButton')?.addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/frontend/pages/empresa_login.html';
    });

    // ====================================================================
    // 📆 FILTROS DE AÑO PARA LOS GRÁFICOS
    // ====================================================================
    ['2023', '2024', '2025'].forEach(year => {
        const btn = document.getElementById(year);
        btn?.addEventListener('click', () => {
            btn.classList.toggle('selected');
            selectedYears.has(year)
                ? selectedYears.delete(year)
                : selectedYears.add(year);

            const filtered = allCommentsData.filter(c =>
                selectedYears.has(new Date(c.timestamp).getFullYear().toString())
            );

            const processed = processCommentsData(filtered);
            updateCharts(processed);
        });
    });

    // ====================================================================
    // 🔁 BOTÓN: ACTUALIZAR PÁGINA COMPLETA
    // ====================================================================
    document.getElementById('refreshButton')?.addEventListener('click', () => location.reload());

    // ====================================================================
    // 📤 BOTÓN: EXPORTAR COMENTARIOS A CSV
    // ====================================================================
    document.getElementById('exportCSVButton')?.addEventListener('click', async () => {
        const res = await fetch(`${API_BASE_URL}/comments`);
        const comentarios = await res.json();

        const csvRows = [["Comentario", "Fecha", "Correo", "Edad"]];
        comentarios.forEach(row => {
            csvRows.push([
                (row.respuesta || '').replace(/"/g, '""'),
                row.timestamp || '',
                row.usuario || '',
                row.edad || 'Desconocida'
            ]);
        });

        const csvContent = csvRows.map(r => r.map(v => `"${v}"`).join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "comentarios_ordenados.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    });

    // ====================================================================
    // 📄 BOTÓN: GENERAR REPORTE PDF
    // ====================================================================
    document.getElementById('generatePDFButton')?.addEventListener('click', async () => {
        const res = await fetch(`${API_BASE_URL}/generate_report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comentarios: allCommentsData })
        });

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'reporte_comentarios.pdf';
        link.click();
        URL.revokeObjectURL(url);
    });

    // ====================================================================
    // ⏱️ AUTO-REFRESH CADA 10 SEGUNDOS
    // ====================================================================
    setInterval(async () => {
        console.log("⏱️ Auto-refresh ejecutado");
    
        const comments = await fetchComments(API_BASE_URL);
        allCommentsData = comments;
    
        const processed = processCommentsData(allCommentsData);
        updateCharts(processed);
    }, 10000);    

});
