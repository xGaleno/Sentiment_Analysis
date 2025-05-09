// ===================================================================
// 🧩 user_interface.js — Manipulación del DOM para usuarios y chats
// ===================================================================

let allUsersGlobal = [];  // Almacena todos los usuarios cargados
let selectedAgeRanges = new Set(['18-25', '26-35', '36-45', '46-60', '60+']);

/**
 * Renderiza la tabla de usuarios en el DOM, aplicando el filtro de edad activo
 * @param {Array} users - Lista de usuarios con campos `email` y `age`
 * @param {Function} onRowClick - Función callback cuando se hace click en una fila
 */
export function renderUsersTable(users, onRowClick) {
    allUsersGlobal = users;
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '';

    const filtered = users.filter(user => {
        const age = user.age;
        if (typeof age !== 'number') return false;

        if (age >= 18 && age <= 25 && selectedAgeRanges.has('18-25')) return true;
        if (age >= 26 && age <= 35 && selectedAgeRanges.has('26-35')) return true;
        if (age >= 36 && age <= 45 && selectedAgeRanges.has('36-45')) return true;
        if (age >= 46 && age <= 60 && selectedAgeRanges.has('46-60')) return true;
        if (age > 60 && selectedAgeRanges.has('60+')) return true;

        return false;
    });

    filtered.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.email}</td>
            <td><button class="delete-user-button" data-email="${user.email}">✖</button></td>
        `;
    
        // Historial al hacer clic en fila
        row.addEventListener('click', () => onRowClick(user.email));
    
        // Lógica de eliminación
        const deleteButton = row.querySelector('.delete-user-button');
        deleteButton.addEventListener('click', async (e) => {
            e.stopPropagation(); // Evita activar historial
            const email = e.target.dataset.email;
    
            const confirmDelete = confirm(`¿Eliminar todos los comentarios del usuario ${email}?`);
            if (!confirmDelete) return;
    
            try {
                const res = await fetch(`/api/delete_user/${encodeURIComponent(email)}`, {
                    method: 'DELETE'
                });
    
                if (!res.ok) throw new Error("Error al eliminar usuario");
    
                alert("Usuario eliminado correctamente");
                location.reload(); // o recargar tabla si prefieres
            } catch (err) {
                console.error("Error al eliminar usuario:", err);
                alert("No se pudo eliminar el usuario");
            }
        });
    
        tbody.appendChild(row);
    });
    
}

/**
 * Renderiza el historial de preguntas y respuestas de un usuario
 * @param {Array} comments - Lista de comentarios
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
            const sentimiento = c.sentimiento || c.sentiment || '(Sin dato)';
            const block = document.createElement('div');
            block.innerHTML = `
                <p><strong>Pregunta:</strong> ${pregunta}</p>
                <p><strong>Respuesta:</strong> ${respuesta}</p>
                <p><strong>Sentimiento:</strong> ${sentimiento}</p>
                <hr>
            `;
            container.appendChild(block);
        });
    }

    section.style.display = 'block';
}

/**
 * Inicializa el filtro de edad, conectando los botones al comportamiento
 * @param {Function} onFilterChange
 */
export function initAgeFilter(onFilterChange) {
    document.querySelectorAll('.age-filter-button').forEach(btn => {
        btn.addEventListener('click', () => {
            const range = btn.dataset.range;
            if (selectedAgeRanges.has(range)) {
                selectedAgeRanges.delete(range);
                btn.classList.remove('selected');
            } else {
                selectedAgeRanges.add(range);
                btn.classList.add('selected');
            }
            onFilterChange(allUsersGlobal);
        });
    });
}
