document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

    const isValidEmail = email =>
        /^[^@\s]+@(gmail\.com|outlook\.com|hotmail\.com|upc\.edu\.pe)$/.test(email);

    const validarUsuario = async (email) => {
        if (!isValidEmail(email)) {
            alert("El formato del correo no es válido.");
            return false;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/check_user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            if (!res.ok) {
                const data = await res.json();
                alert(data.error || 'El correo no está registrado. Por favor, ingresa uno válido.');
                return false;
            }

            return true;
        } catch (error) {
            console.error("Error validando el usuario:", error);
            alert("Hubo un problema al validar el usuario.");
            return false;
        }
    };

    class ChatInterface {
        constructor() {
            this.questions = [
                "¿Cómo describirías la calidad de los productos que has adquirido en nuestra tienda? ¿Cumplen con tus expectativas en términos de durabilidad, diseño y funcionalidad?",
                "¿Cuán satisfecho estás con el nivel de atención y servicio al cliente que has recibido durante tu última visita o compra en nuestra tienda? ¿Hubo algo en particular que te llamó la atención (positiva o negativamente)?",
                "Si tuvieras que recomendar nuestros productos o servicios a alguien más, ¿qué aspectos destacarías y qué áreas sientes que podrían ser mejoradas para ofrecer una experiencia más completa y agradable?"
            ];
            this.currentQuestionIndex = 0;
            this.responses = [];
            this.chatWindow = document.querySelector('.chat-window');
            this.messageInput = document.querySelector('.message-input');
            this.sendButton = document.querySelector('.send-button');
            this.userEmail = localStorage.getItem('user_email');
            this.initialize();
        }

        async initialize() {
            const valid = this.userEmail && await validarUsuario(this.userEmail);
            if (!valid) {
                localStorage.removeItem('user_email');
                window.location.href = '/';  // ✅ Ruta Flask principal
                return;
            }
        
            this.sendButton.addEventListener('click', () => this.handleSendMessage());
            this.messageInput.addEventListener('keypress', e => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        
            this.askQuestion();
        }        

        handleSendMessage() {
            const msg = this.messageInput.value.trim();
            if (!msg) return;

            this.addMessage(msg, false);
            this.responses.push({
                pregunta: this.questions[this.currentQuestionIndex],
                respuesta: msg
            });

            this.messageInput.value = '';
            this.currentQuestionIndex++;

            if (this.currentQuestionIndex < this.questions.length) {
                setTimeout(() => this.askQuestion(), 1000);
            } else {
                this.finishChat();
                this.addMessage("Guardando tus respuestas...");
                setTimeout(() => this.analyzeSentiment(), 500);                
            }
        }

        addMessage(text, isAssistant = true) {
            const div = document.createElement('div');
            div.className = `chat-message ${isAssistant ? 'assistant' : 'user'}`;
            div.textContent = text;
            this.chatWindow.appendChild(div);
            this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
        }

        askQuestion() {
            this.addMessage(this.questions[this.currentQuestionIndex]);
        }

        async analyzeSentiment() {
            try {
                const res = await fetch(`${API_BASE_URL}/sentiment_analysis`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: this.userEmail,
                        respuestas: this.responses
                    })
                });
        
                if (!res.ok) throw new Error('Error en el análisis de sentimiento');
        
                console.log("Sentimiento registrado correctamente.");
                window.location.href = '/agradecimiento';  // ✅ Ruta Flask, no HTML directo
        
            } catch (error) {
                console.error('Error al analizar sentimiento:', error);
                alert('Ocurrió un error al procesar tus respuestas. Inténtalo más tarde.');
            }
        }        

        finishChat() {
            this.addMessage("¡Gracias por tus respuestas! Tu opinión es muy importante para nosotros.");
            this.messageInput.disabled = true;
            this.sendButton.disabled = true;
        }
    }

    new ChatInterface();
});
