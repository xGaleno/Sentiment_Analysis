document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    const loginButton = document.querySelector('.login-button');
    
    // Crear div para mensajes de error/éxito
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    loginForm.appendChild(messageDiv);

    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        
        // Mostrar estado de carga
        loginButton.disabled = true;
        loginButton.innerHTML = 'Iniciando sesión...';
        messageDiv.textContent = '';
        
        const username = document.querySelector('input[type="text"]').value;
        const password = document.querySelector('input[type="password"]').value;
        
        try {
            const response = await ApiService.loginEmpresa({ username, password });
            
            if (response.token) {
                // Guardar datos de la sesión
                localStorage.setItem('token', response.token);
                localStorage.setItem('empresa_id', response.empresa_id);
                localStorage.setItem('empresa_name', response.empresa_name);
                
                // Mostrar mensaje de éxito
                messageDiv.textContent = 'Login exitoso, redirigiendo...';
                messageDiv.style.color = 'green';
                
                // Redireccionar después de un breve delay
                setTimeout(() => {
                    window.location.href = "/frontend/pages/empresa_analisis.html";
                }, 1000);
            } else {
                showError("Error en la autenticación");
            }
        } catch (error) {
            showError(error.message || "Login failed. Please try again.");
        }
    });

    function showError(message) {
        loginButton.disabled = false;
        loginButton.innerHTML = 'Login';
        messageDiv.textContent = message;
        messageDiv.style.color = 'red';
    }
});