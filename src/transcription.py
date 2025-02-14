import os
import openai
from .video_processor import convert_to_audio
from typing import List, Dict

def extract_transcripts(clips_info):
    """Extrai transcrições dos clips usando OpenAI Whisper"""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    transcripts = []
    
    for clip in clips_info:
        # Verifica se já existe transcrição salva
        transcript_path = os.path.join('temp', f"{os.path.basename(clip['path'])}.transcript.txt")
        
        if os.path.exists(transcript_path):
            print(f"Usando transcrição existente para clip {clip['id']}")
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
                clip['transcript'] = transcript_text
                transcripts.append(f"Clip {clip['id']}:\n{transcript_text}\n")
            continue
            
        try:
            # Extrair áudio do vídeo
            audio_path = convert_to_audio(clip['path'], 'temp')
            
            # Transcrever áudio usando Whisper
            print(f"Transcrevendo clip {clip['id']}...")
            with open(audio_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    language="pt"
                )
                transcript_text = transcript['text']
                
                # Salva a transcrição para uso futuro
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript_text)
                
                clip['transcript'] = transcript_text
                transcripts.append(f"Clip {clip['id']}:\n{transcript_text}\n")
        except Exception as e:
            print(f"Erro ao transcrever clip {clip['id']}: {str(e)}")
            clip['transcript'] = ""
            transcripts.append(f"Clip {clip['id']}: [Sem transcrição]\n")
    
    return "\n".join(transcripts)

def find_similar_content_with_gpt(clips_info: List[Dict]) -> List[int]:
    """
    Usa GPT para identificar clips com conteúdo similar/repetido
    Retorna lista de IDs dos clips que devem ser removidos
    """
    # Prepara o texto para análise
    clips_text = []
    for clip in clips_info:
        if clip.get('transcript'):
            clips_text.append(f"Clip {clip['id']}: {clip['transcript']}")
    
    if not clips_text:
        return []
        
    system_message = {
        "role": "system",
        "content": """Você é um especialista em análise de texto e sua tarefa é identificar conteúdo similar ou repetido entre diferentes clips de vídeo.

Regras para identificação:
1. Identifique clips que transmitem a mesma informação, mesmo que com palavras diferentes
2. Considere o contexto e significado, não apenas palavras exatas
3. Se houver repetição, escolha manter o clip que:
   - É mais conciso e direto
   - Tem melhor clareza na explicação
   - Aparece primeiro na sequência (se tudo mais for igual)

Formato da resposta deve ser EXATAMENTE:
CLIPS_TO_REMOVE: [lista de números dos clips a remover]
REASON: [breve explicação do motivo]"""
    }
    
    user_message = {
        "role": "user",
        "content": "Analise os seguintes clips e identifique quais contêm conteúdo repetido:\n\n" + "\n".join(clips_text)
    }
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_message, user_message],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message['content']
        
        # Extrai os clips a serem removidos da resposta
        clips_line = next(line for line in content.split('\n') if line.startswith('CLIPS_TO_REMOVE:'))
        clips_to_remove = eval(clips_line.split(':', 1)[1].strip())
        
        # Extrai a razão para logging
        reason_line = next(line for line in content.split('\n') if line.startswith('REASON:'))
        reason = reason_line.split(':', 1)[1].strip()
        
        print(f"\nConteúdo repetido encontrado:")
        print(f"Clips a remover: {clips_to_remove}")
        print(f"Motivo: {reason}")
        
        return clips_to_remove
        
    except Exception as e:
        print(f"Erro ao analisar similaridade com GPT: {str(e)}")
        return []

def remove_duplicate_content(clips_info: List[Dict]) -> List[Dict]:
    """
    Remove clips com conteúdo similar/repetido usando GPT para análise
    """
    clips_to_remove = find_similar_content_with_gpt(clips_info)
    return [clip for clip in clips_info if clip['id'] not in clips_to_remove]
