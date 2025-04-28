document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

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

        initialize() {
            if (!this.userEmail) {
                window.location.href = '/frontend/pages/main.html';
                return;
            }
            this.setupEventListeners();
            this.askQuestion();
        }

        setupEventListeners() {
            this.sendButton.addEventListener('click', () => this.handleSendMessage());
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        }

        handleSendMessage() {
            const message = this.messageInput.value.trim();
            if (!message) return;

            this.addMessage(message, false);

            const currentQuestion = this.questions[this.currentQuestionIndex];
            this.responses.push({
                pregunta: currentQuestion,
                respuesta: message
            });

            this.messageInput.value = '';
            this.currentQuestionIndex++;

            if (this.currentQuestionIndex < this.questions.length) {
                setTimeout(() => this.askQuestion(), 1000);
            } else {
                this.finishChat();
                this.analyzeSentiment();
            }
        }

        addMessage(message, isAssistant = true) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${isAssistant ? 'assistant' : 'user'}`;
            messageDiv.textContent = message;
            this.chatWindow.appendChild(messageDiv);
            this.scrollToBottom();
        }

        scrollToBottom() {
            this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
        }

        askQuestion() {
            const question = this.questions[this.currentQuestionIndex];
            this.addMessage(question, true);
        }

        async analyzeSentiment() {
            try {
                const response = await fetch(`${API_BASE_URL}/sentiment_analysis`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: this.userEmail,
                        respuestas: this.responses
                    })
                });

                if (!response.ok) {
                    throw new Error('Error en el análisis de sentimiento');
                }

                const result = await response.json();
                console.log("Sentimiento registrado:", result);

                // Enviar correo de confirmación al terminar
                this.sendConfirmationEmail();

            } catch (error) {
                console.error('Error al analizar sentimiento:', error);
                alert('Ocurrió un error al procesar tus respuestas. Inténtalo más tarde.');
            }
        }

        async sendConfirmationEmail() {
            try {
                const response = await fetch(`${API_BASE_URL}/send_confirmation_email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: this.userEmail
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error enviando correo');
                }

                console.log('Correo de confirmación enviado correctamente');

            } catch (error) {
                console.error('Error al enviar correo de confirmación:', error);
                alert('No pudimos enviarte el correo de confirmación, pero tu participación fue registrada.');
            } finally {
                setTimeout(() => {
                    window.location.href = '/frontend/pages/main.html';
                }, 3000);
            }
        }

        finishChat() {
            this.addMessage("¡Gracias por tus respuestas! Tu opinión es muy importante para nosotros.", true);
            this.messageInput.disabled = true;
            this.sendButton.disabled = true;
        }
    }

    new ChatInterface();
});
