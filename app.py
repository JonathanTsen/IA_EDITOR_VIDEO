from flask import Flask, request, jsonify, send_file, render_template, after_this_request, make_response
from werkzeug.utils import secure_filename
import os
import gc
import secrets
from functools import wraps
from src import (
    setup_folders,
    get_clips_info,
    get_ai_script,
    parse_ai_response,
    create_final_video,
    remove_duplicate_content
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'clips')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB max file size

# Configurações de segurança
app.config['SECURE_HEADERS'] = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data:;"
}

def add_secure_headers(response):
    """Adiciona headers de segurança em todas as respostas"""
    for header, value in app.config['SECURE_HEADERS'].items():
        response.headers[header] = value
    return response

def secure_api_key():
    """Decorator para proteger e limpar a API key"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            @after_this_request
            def cleanup(response):
                # Limpa a API key da memória
                if 'OPENAI_API_KEY' in os.environ:
                    # Sobrescreve a variável com dados aleatórios antes de deletar
                    os.environ['OPENAI_API_KEY'] = secrets.token_hex(32)
                    del os.environ['OPENAI_API_KEY']
                
                # Força a coleta de lixo
                gc.collect()
                
                # Adiciona headers de segurança
                return add_secure_headers(response)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Rota principal com headers de segurança"""
    response = make_response(render_template('index.html'))
    return add_secure_headers(response)

@app.route('/upload', methods=['POST'])
@secure_api_key()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    # Obtém a API key do header em vez do form data
    api_key = request.headers.get('X-Api-Key')
    if not api_key:
        return jsonify({'error': 'OpenAI API Key não fornecida'}), 400
    
    # Valida o formato da API key
    if not api_key.startswith('sk-') or len(api_key) < 20:
        return jsonify({'error': 'OpenAI API Key inválida'}), 400
    
    try:
        # Define a API key no ambiente de forma segura
        os.environ['OPENAI_API_KEY'] = api_key
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Configuração inicial
                setup_folders()
                
                # Processar clips
                clips_info = get_clips_info()
                
                if not clips_info:
                    return jsonify({'error': 'Erro ao processar o vídeo'}), 500
                
                # Remover conteúdo duplicado
                clips_info = remove_duplicate_content(clips_info)
                
                # Gerar script com IA
                ai_response = get_ai_script(clips_info)
                
                # Extrair narrativa e ordem dos clips
                narrative, clips_order, clips_timing = parse_ai_response(ai_response)
                
                # Criar vídeo final
                output_path = 'video_final.mp4'
                create_final_video(clips_order, clips_info, clips_timing)
                
                return jsonify({
                    'message': 'Vídeo processado com sucesso',
                    'narrative': narrative,
                    'output_path': output_path
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            finally:
                # Limpa o arquivo temporário após o processamento
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
        
        return jsonify({'error': 'Erro ao processar o arquivo'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Rota de download com headers de segurança"""
    try:
        response = send_file(filename, as_attachment=True)
        return add_secure_headers(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
