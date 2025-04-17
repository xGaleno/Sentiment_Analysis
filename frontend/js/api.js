// Configuración dinámica de la URL base de la API
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api'; 

class ApiService {
    static async login(credentials) {
        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });
            return await response.json();
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    static async sendMessage(message) {
        try {
            const response = await fetch(`${API_BASE_URL}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ message })
            });
            return await response.json();
        } catch (error) {
            console.error('Message sending error:', error);
            throw error;
        }
    }

    static async loginEmpresa(credentials) {
        // Simulación de login exitoso
        const validCredentials = {
            username: "admin",
            password: "admin123"
        };
    
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (
                    credentials.username === validCredentials.username &&
                    credentials.password === validCredentials.password
                ) {
                    resolve({
                        token: "simulated-token",
                        empresa_id: "EMP001",
                        empresa_name: "Empresa Demo"
                    });
                } else {
                    reject(new Error("Credenciales incorrectas"));
                }
            }, 800);
        });
    }

    static async getEmpresaStats() {
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error('No auth token found');

            const response = await fetch(`${API_BASE_URL}/empresa_stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al obtener estadísticas');
            return await response.json();
        } catch (error) {
            console.error('Stats error:', error);
            throw error;
        }
    }
}