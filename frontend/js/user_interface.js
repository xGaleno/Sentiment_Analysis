// ===================================================================
// 🧩 user_interface.js — Manipulación del DOM para usuarios y chats
// ===================================================================


/**
 * Renderiza la tabla de usuarios en el DOM
 * @param {Array} users - Lista de usuarios con campo `email`
 * @param {Function} onRowClick - Función callback cuando se hace click en una fila
 */
export function renderUsersTable(users, onRowClick) {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '';

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${user.email}</td>`;
        row.addEventListener('click', () => onRowClick(user.email));
        tbody.appendChild(row);
    });
}


/**
 * Renderiza el historial de preguntas y respuestas de un usuario
 * @param {Array} comments - Lista de comentarios (con pregunta/respuesta)
 * @param {string} userEmail - Email del usuario seleccionado
 */
export function renderChatHistory(comments, userEmail) {
    const section = document.querySelector('.chat-panel');
    const container = document.getElementById('chatHistoryContainer');
    container.innerHTML = '';

    const userComments = comments.filter(c => c.usuario === userEmail);

    if (userComments.length === 0) {
        container.innerHTML = '<p>No hay historial de chat disponible para este usuario.</p>';
    } else {
        userComments.forEach(c => {
            const pregunta = c.pregunta || '(Pregunta no disponible)';
            const respuesta = c.respuesta || '(Respuesta no disponible)';
            const block = document.createElement('div');
            block.innerHTML = `
                <p><strong>Pregunta:</strong> ${pregunta}</p>
                <p><strong>Respuesta:</strong> ${respuesta}</p>
                <hr>
            `;
            container.appendChild(block);
        });
    }

    section.style.display = 'block';
}
