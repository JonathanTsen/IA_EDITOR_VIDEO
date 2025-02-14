import os
import glob
import mimetypes
from .video_processor import convert_to_mp4
from .audio_processor import detect_silence

def setup_folders():
    """Cria as pastas necessárias para o projeto"""
    os.makedirs("temp", exist_ok=True)
    os.makedirs("clips", exist_ok=True)

def is_video_file(filepath):
    """Verifica se o arquivo é um vídeo"""
    mime, _ = mimetypes.guess_type(filepath)
    return mime and mime.startswith('video')

def is_audio_file(filepath):
    """Verifica se o arquivo é um áudio"""
    mime, _ = mimetypes.guess_type(filepath)
    return mime and mime.startswith('audio')

def get_clips_info():
    """Obtém informações sobre todos os clips disponíveis"""
    clips_info = []
    extensions = ['*.mp4', '*.mkv', '*.avi', '*.mov', '*.mp3', '*.wav']
    
    for ext in extensions:
        for filepath in glob.glob(os.path.join("clips", ext)):
            processed_path, ranges = process_file(filepath)
            if not processed_path:
                continue
            
            # Usa o primeiro range ou valores padrão se não houver ranges
            if ranges and len(ranges) > 0:
                start, end = ranges[0]
            else:
                # Se não houver ranges, usa o vídeo inteiro
                video = VideoFileClip(processed_path)
                start, end = 0, video.duration
                video.close()
            
            duration = end - start
            
            clips_info.append({
                'path': processed_path,
                'start': start,
                'end': end,
                'duration': duration,
                'original': filepath,
                'id': len(clips_info)
            })
    
    return clips_info

def process_file(filepath):
    """Processa um arquivo, convertendo para MP4 se necessário e detectando silêncios"""
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join("temp", f"{name}.mp4")
    
    # Converte para MP4 se necessário
    if ext.lower() != '.mp4':
        output_path = convert_to_mp4(filepath, output_path)
    else:
        output_path = filepath
    
    # Detecta e remove silêncios
    ranges = detect_silence(output_path)
    
    # Retorna o caminho do arquivo e os ranges detectados
    return output_path, ranges
