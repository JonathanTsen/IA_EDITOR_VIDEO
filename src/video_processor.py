import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import ffmpeg

def convert_to_mp4(input_path, output_path):
    """Converte vídeo para formato MP4"""
    # Se o arquivo já existe, retorna o caminho
    if os.path.exists(output_path):
        print(f"Usando arquivo convertido existente: {output_path}")
        return output_path
        
    print(f"Convertendo {input_path} para MP4...")
    (
        ffmpeg
        .input(input_path)
        .output(output_path, vcodec='libx264', acodec='aac')
        .run(overwrite_output=True, quiet=True)
    )
    return output_path

def create_video_from_audio(audio_path, output_path):
    """Cria um vídeo a partir de um arquivo de áudio"""
    (
        ffmpeg
        .input('default_image.jpg', loop=1, framerate=1)
        .input(audio_path)
        .output(output_path, vcodec='libx264', t=ffmpeg.probe(audio_path)['format']['duration'])
        .run(overwrite_output=True, quiet=True)
    )
    return output_path

def convert_to_audio(video_path, temp_dir):
    """Extrai o áudio de um vídeo"""
    audio_path = os.path.join(temp_dir, os.path.basename(video_path) + ".mp3")
    
    # Se o arquivo de áudio já existe, retorna o caminho
    if os.path.exists(audio_path):
        print(f"Usando arquivo de áudio existente: {audio_path}")
        return audio_path
        
    print(f"Extraindo áudio de {video_path}...")
    if not os.path.exists(audio_path):
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='libmp3lame')
            .run(overwrite_output=True, quiet=True)
        )
    return audio_path

def create_final_video(clips_order, clips_info, clips_timing):
    """Cria o vídeo final apenas com cortes simples"""
    print("\nAplicando cortes...")
    final_clips = []
    
    try:
        for idx, clip_number in enumerate(clips_order):
            if clip_number not in clips_timing:
                continue
                
            clip_info = clips_info[clip_number]
            start_time, end_time = clips_timing[clip_number]
            
            if not os.path.exists(clip_info['path']):
                continue
            
            try:
                clip = VideoFileClip(clip_info['path'])
                
                # Aplica apenas o corte de tempo
                if start_time > 0 or end_time < clip.duration:
                    end_time = min(end_time, clip.duration)
                    clip = clip.subclip(start_time, end_time)
                
                final_clips.append(clip)
                print(f"Clip {clip_number} cortado com sucesso")
                
            except Exception as e:
                print(f"Erro ao processar clip {clip_number}: {str(e)}")
                continue
        
        if not final_clips:
            raise ValueError("Nenhum clip válido para montar o vídeo")
        
        print("\nMontando vídeo final...")
        final_video = concatenate_videoclips(final_clips)
        
        output_file = "video_final.mp4"
        
        print(f"\nRenderizando vídeo final...")
        final_video.write_videofile(
            output_file,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=30
        )
        
        for clip in final_clips:
            clip.close()
        final_video.close()
        
        print(f"\nVídeo final criado com sucesso: {output_file}")
        print(f"Duração total: {final_video.duration:.2f} segundos")
        
    except Exception as e:
        for clip in final_clips:
            try:
                clip.close()
            except:
                pass
        raise e
