document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileUpload = document.getElementById('fileUpload');
    const fileNames = document.getElementById('fileNames');
    const uploadStatus = document.getElementById('uploadStatus');
    
    // URL da API para upload
    const UPLOAD_URL = 'http://localhost:5000/api/upload';
    
    // Atualiza o nome dos arquivos selecionados
    fileUpload.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileList = Array.from(this.files).map(file => file.name);
            fileNames.textContent = fileList.join(', ');
        } else {
            fileNames.textContent = 'Nenhum arquivo selecionado';
        }
    });
    
    // Manipula o envio do formulário
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (fileUpload.files.length === 0) {
            showStatus('Por favor, selecione pelo menos um arquivo.', 'error');
            return;
        }
        
        showStatus('Enviando arquivos...', 'progress');
        
        const formData = new FormData();
        
        // Adiciona todos os arquivos ao FormData
        for (let i = 0; i < fileUpload.files.length; i++) {
            formData.append('files', fileUpload.files[i]);
        }
        
        try {
            const response = await fetch(UPLOAD_URL, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showStatus(`Upload concluído com sucesso! ${data.processed_files || ''} documentos processados.`, 'success');
                
                // Limpa o formulário após o upload bem-sucedido
                uploadForm.reset();
                fileNames.textContent = 'Nenhum arquivo selecionado';
                
                // Adiciona uma mensagem no chat sobre os documentos carregados
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                messageDiv.textContent = `Documentos carregados com sucesso! Agora você pode fazer perguntas sobre eles.`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                showStatus(`Erro no upload: ${data.error || 'Erro desconhecido'}`, 'error');
            }
        } catch (error) {
            console.error('Erro ao enviar arquivos:', error);
            showStatus('Não foi possível conectar ao servidor. Verifique sua conexão.', 'error');
        }
    });
    
    // Função para mostrar mensagens de status
    function showStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'upload-status';
        
        // Adiciona classe específica para o tipo de status
        switch(type) {
            case 'success':
                uploadStatus.classList.add('status-success');
                break;
            case 'error':
                uploadStatus.classList.add('status-error');
                break;
            case 'progress':
                uploadStatus.classList.add('status-progress');
                break;
        }
    }
});