from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from src import (
    setup_folders,
    get_clips_info,
    get_ai_script,
    parse_ai_response,
    create_final_video,
    remove_duplicate_content
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'clips'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
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
    
    return jsonify({'error': 'Erro ao processar o arquivo'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):
        print("Erro: OPENAI_API_KEY não encontrada!")
        print("Por favor, crie um arquivo .env com sua chave da API OpenAI")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
