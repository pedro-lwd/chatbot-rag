document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    
    // URL da API - ajuste conforme necessário
    const API_URL = 'http://localhost:5000/api/chat';
    
    // Função para criar um elemento de mensagem
    function createMessageElement(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = text;
        return messageDiv;
    }
    
    // Função para criar o indicador de digitação
    function createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.id = 'typingIndicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicator.appendChild(dot);
        }
        
        return indicator;
    }
    
    // Função para enviar mensagem
    async function sendMessage() {
        const message = userInput.value.trim();
        
        if (message === '') {
            return;
        }
        
        // Adiciona mensagem do usuário
        chatMessages.appendChild(createMessageElement(message, true));
        
        // Limpa o input
        userInput.value = '';
        
        // Adiciona indicador de digitação
        const typingIndicator = createTypingIndicator();
        chatMessages.appendChild(typingIndicator);
        
        // Rola para a mensagem mais recente
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            // Envia requisição para a API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove o indicador de digitação
            chatMessages.removeChild(typingIndicator);
            
            if (response.ok) {
                // Adiciona resposta do bot
                chatMessages.appendChild(createMessageElement(data.response, false));
            } else {
                // Adiciona mensagem de erro
                chatMessages.appendChild(
                    createMessageElement('Desculpe, ocorreu um erro: ' + (data.error || 'Erro desconhecido'), false)
                );
            }
        } catch (error) {
            // Remove o indicador de digitação
            if (typingIndicator.parentNode) {
                chatMessages.removeChild(typingIndicator);
            }
            
            // Adiciona mensagem de erro
            chatMessages.appendChild(
                createMessageElement('Não foi possível conectar ao servidor. Verifique sua conexão.', false)
            );
            
            console.error('Erro ao enviar mensagem:', error);
        }
        
        // Rola para a mensagem mais recente
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});