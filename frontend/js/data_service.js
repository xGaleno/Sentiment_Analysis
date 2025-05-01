// =======================================================
// 📦 data_service.js — Gestión de datos (API y procesamiento)
// =======================================================


// =======================================================
// 🌐 1. FETCH: Datos desde el backend
// =======================================================

/**
 * Obtiene los comentarios desde la API
 * @param {string} API_BASE_URL - Ruta base de la API
 * @returns {Promise<Array>} Lista de comentarios
 */
export async function fetchComments(API_BASE_URL) {
    try {
        const res = await fetch(`${API_BASE_URL}/comments`);
        if (!res.ok) throw new Error(`Error: ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.error("Error al obtener comentarios:", err);
        return [];
    }
}


/**
 * Obtiene los usuarios desde la API
 * @param {string} API_BASE_URL - Ruta base de la API
 * @returns {Promise<Array>} Lista de usuarios
 */
export async function fetchUsers(API_BASE_URL) {
    try {
        const res = await fetch(`${API_BASE_URL}/users`);
        if (!res.ok) throw new Error(`Error: ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.error("Error al obtener usuarios:", err);
        return [];
    }
}

  
// =======================================================
// 🧠 2. PROCESAMIENTO DE COMENTARIOS
// =======================================================

/**
 * Procesa los comentarios para generar:
 * - Conteo por tipo de sentimiento
 * - Promedio y varianza por mes
 *
 * @param {Array} comments - Lista de comentarios con timestamp y sentimiento
 * @returns {Object} { sentiments, averageSentimentByMonth }
 */
export function processCommentsData(comments) {
    const sentiments = { positive: 0, neutral: 0, negative: 0 };
    const averageSentimentData = {};

    comments.forEach(comment => {
        const raw = comment.sentiment || comment.sentimiento;
        const ts = comment.timestamp;
        if (!raw || !ts) return;

        const sentiment = raw.toLowerCase().trim() === 'positivo' ? 'positive'
                         : raw.toLowerCase().trim() === 'neutro' ? 'neutral'
                         : 'negative';
        const score = sentiment === "positive" ? 1 : sentiment === "neutral" ? 0 : -1;
        sentiments[sentiment]++;

        const date = new Date(ts);
        if (isNaN(date.getTime())) return;
        const monthKey = `${date.getFullYear()}-${date.toLocaleString('default', { month: 'long' })}`;

        if (!averageSentimentData[monthKey]) {
            averageSentimentData[monthKey] = { totalScore: 0, count: 0, scores: [] };
        }

        averageSentimentData[monthKey].totalScore += score;
        averageSentimentData[monthKey].count++;
        averageSentimentData[monthKey].scores.push(score);
    });

    const averageSentimentByMonth = Object.entries(averageSentimentData).map(([month, data]) => {
        const avg = data.totalScore / data.count;
        const variance = data.scores.reduce((acc, s) => acc + Math.pow(s - avg, 2), 0) / data.count;
        return { date: month, averageSentiment: avg, variance };
    });

    return { sentiments, averageSentimentByMonth };
}
