from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from rag import gerar_resposta
from gerar_embedded import processar_arquivos
from dotenv import load_dotenv
import uuid

load_dotenv()


app = Flask(__name__, static_folder='./static', template_folder='./templates')
CORS(app)

pasta_upload = os.getenv('PASTA_UPLOAD')
EXTENSOES_LIBERADAS = {'pdf', 'ppt', 'pptx'}
app.config['UPLOAD_FOLDER'] = pasta_upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16mb

def arquivo_liberado(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_LIBERADAS

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('message', '')
    
    if not query:
        return jsonify({'error': 'Mensagem vazia'}), 400
    
    try:
        
        resposta = gerar_resposta(query)
        return jsonify({'response': resposta})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/upload', methods=['POST'])
def upload_arquivo():
    if 'arquivos' not in request.arquivos:
        return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
    
    arquivos = request.arquivos.getlist('arquivos')
    
    if not arquivos or arquivos[0].filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    arquivos_processados = 0
    erros = []
    
    for arquivo in arquivos:
        if arquivo and arquivo_liberado(arquivo.filename):
            # gerar um arquivo com um uuid seguro pra n da merda
            original_filename = secure_filename(arquivo.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                arquivo.save(filepath)
                
                processar_arquivos(filepath, original_filename)
                
                arquivos_processados += 1
            except Exception as e:
                erros.append(f"Erro ao processar {original_filename}: {str(e)}")
            else:
                erros.append(f"Tipo de arquivo não permitido: {arquivo.filename}")
                
        if arquivos_processados > 0:
            return jsonify({''
                'mensagem': 'Upload concluído com sucesso',
                'arquivos_processados': arquivos_processados,
                'erros': erros if erros else None
                
            })
        else:
            return jsonify({'erro': 'Nenhum arquivo foi processado', 'details': erros }), 400
        

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path == "":
        return send_from_directory(app.template_folder, 'index.html')
    return send_from_directory(app.template_folder, path)

if __name__ == '__main__':
    print("Iniciando flask")
    app.run(debug=True, host='0.0.0.0', port=5000)