// ======================================================================
// 🔐 empresa_login.js — Lógica de autenticación para login de empresa
// ======================================================================

document.addEventListener('DOMContentLoaded', () => {
    // 🔍 Elementos del DOM
    const loginForm = document.querySelector('.login-form');
    const loginButton = document.querySelector('.login-button');

    // 📢 Mensaje dinámico de estado (éxito o error)
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    loginForm.appendChild(messageDiv);

    // ======================================================================
    // 🚀 SUBMIT DEL FORMULARIO DE LOGIN
    // ======================================================================
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // ⏳ Mostrar estado de carga
        setButtonState(true, 'Iniciando sesión...');
        messageDiv.textContent = '';

        const username = document.querySelector('input[type="text"]').value;
        const password = document.querySelector('input[type="password"]').value;

        try {
            // 🧠 Llamada al servicio de login simulado
            const res = await ApiService.loginEmpresa({ username, password });

            // ✅ Login exitoso
            if (res.token) {
                localStorage.setItem('token', res.token);
                localStorage.setItem('empresa_id', res.empresa_id);
                localStorage.setItem('empresa_name', res.empresa_name);

                messageDiv.textContent = 'Login exitoso, redirigiendo...';
                messageDiv.style.color = 'green';

                setTimeout(() => {
                    window.location.href = "/frontend/pages/empresa_analisis.html";
                }, 1000);
            } else {
                handleError("Error en la autenticación");
            }
        } catch (err) {
            // ❌ Fallo en login
            handleError(err.message || "Login failed. Please try again.");
        }
    });

    // ======================================================================
    // ⚠️ FUNCIONES AUXILIARES
    // ======================================================================

    /**
     * Muestra mensaje de error y reinicia botón
     * @param {string} message
     */
    function handleError(message) {
        setButtonState(false, 'Login');
        messageDiv.textContent = message;
        messageDiv.style.color = 'red';
    }

    /**
     * Cambia el estado del botón de login
     * @param {boolean} disabled
     * @param {string} text
     */
    function setButtonState(disabled, text) {
        loginButton.disabled = disabled;
        loginButton.innerHTML = text;
    }
});
