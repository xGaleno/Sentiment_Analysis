// ============================================
// 🔧 CONFIGURACIÓN GLOBAL DE API
// ============================================

const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';


// ============================================
// 📦 CLASE ApiService
// ============================================

class ApiService {

    // ============================================
    // 🔐 AUTENTICACIÓN: Login de usuario general
    // ============================================
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


    // ============================================
    // 🔐 AUTENTICACIÓN: Login de empresa (Simulado)
    // ============================================
    static async loginEmpresa(credentials) {
        const validCredentials = {
            username: "Diha",
            password: "Alicia_Modas_Diha"
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


    // ============================================
    // ✉️ ENVÍO DE MENSAJES
    // ============================================
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


    // ============================================
    // 📊 CONSULTA DE ESTADÍSTICAS DE EMPRESA
    // ============================================
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
