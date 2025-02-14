from pydub import AudioSegment
from pydub.silence import detect_nonsilent

def analyze_audio_levels(audio_segment, window_ms=100):
    """Analisa os níveis de áudio para identificar pontos ideais de corte"""
    chunks = [audio_segment[i:i+window_ms] for i in range(0, len(audio_segment), window_ms)]
    levels = [chunk.dBFS for chunk in chunks]
    
    # Calcula médias móveis para suavizar a detecção
    window_size = 5
    moving_avg = []
    for i in range(len(levels)):
        start = max(0, i - window_size)
        end = min(len(levels), i + window_size)
        moving_avg.append(sum(levels[start:end]) / (end - start))
    
    return moving_avg

def find_optimal_cut_points(audio_segment, ranges):
    """Encontra os pontos ideais de corte baseado em análise de áudio"""
    levels = analyze_audio_levels(audio_segment)
    optimal_ranges = []
    
    for start, end in ranges:
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        
        # Analisa uma janela antes e depois do ponto de corte
        window_size = 500  # 500ms
        
        # Ajusta o ponto de início
        start_idx = start_ms // 100  # Converte para índice (100ms janelas)
        if start_idx > 0:
            best_start = start_ms
            min_level = float('inf')
            for i in range(max(0, start_idx - window_size//100), start_idx + window_size//100):
                if i < len(levels) and abs(levels[i]) < min_level:
                    min_level = abs(levels[i])
                    best_start = i * 100
            start_ms = best_start
        
        # Ajusta o ponto final
        end_idx = end_ms // 100
        if end_idx < len(levels):
            best_end = end_ms
            min_level = float('inf')
            for i in range(end_idx - window_size//100, min(len(levels), end_idx + window_size//100)):
                if abs(levels[i]) < min_level:
                    min_level = abs(levels[i])
                    best_end = i * 100
            end_ms = best_end
        
        optimal_ranges.append((start_ms/1000, end_ms/1000))
    
    return optimal_ranges

def detect_silence(path):
    """Detecta e analisa silêncios no áudio para determinar pontos de corte ideais"""
    audio = AudioSegment.from_file(path)
    
    # Parâmetros refinados para detecção de silêncio
    non_silent_ranges = detect_nonsilent(
        audio,
        min_silence_len=300,     # Reduzido para 400ms para ser mais agressivo
        silence_thresh=-32,      # Threshold ainda mais sensível
        seek_step=1             # Máxima precisão na busca
    )
    
    if not non_silent_ranges:
        return [(0, len(audio) / 1000)]
    
    # Remove silêncios longos no início e fim
    first_non_silent = non_silent_ranges[0]
    last_non_silent = non_silent_ranges[-1]
    
    # Se tiver mais de 400ms de silêncio no início, remove
    if first_non_silent[0] > 400:
        print(f"Removendo {first_non_silent[0]}ms de silêncio inicial")
        non_silent_ranges[0] = (0, first_non_silent[1])
    
    # Se tiver mais de 600ms de silêncio no fim, remove
    if len(audio) - last_non_silent[1] > 600:
        print(f"Removendo {len(audio) - last_non_silent[1]}ms de silêncio final")
        non_silent_ranges[-1] = (last_non_silent[0], len(audio))
    
    # Adiciona margens dinâmicas baseadas no contexto
    ranges = []
    for i, (start, end) in enumerate(non_silent_ranges):
        # Margens adaptativas baseadas na duração do segmento
        segment_duration = end - start
        
        # Margens menores no início para evitar silêncios
        start_margin = min(200, segment_duration * 0.03)  # 3% da duração ou 200ms
        end_margin = min(300, segment_duration * 0.05)    # 5% da duração ou 300ms
        
        # Adiciona margem extra para silêncio natural
        if i > 0:  # Não adiciona margem extra no primeiro segmento
            start_margin += 50   # Reduzido para 50ms
        if i < len(non_silent_ranges) - 1:  # Não adiciona margem extra no último segmento
            end_margin += 100    # Reduzido para 100ms
        
        start = max(0, start - start_margin)
        end = min(len(audio), end + end_margin)
        ranges.append((start / 1000, end / 1000))
    
    # Combina segmentos próximos com threshold adaptativo
    merged_ranges = []
    for start, end in ranges:
        if merged_ranges:
            prev_start, prev_end = merged_ranges[-1]
            gap = start - prev_end
            # Threshold adaptativo baseado na duração dos segmentos
            threshold = min(0.8, (end - start + prev_end - prev_start) * 0.15)
            if gap < threshold:
                merged_ranges[-1] = (prev_start, end)
            else:
                merged_ranges.append((start, end))
        else:
            merged_ranges.append((start, end))
    
    # Encontra pontos ideais de corte baseado em análise de áudio
    optimal_ranges = find_optimal_cut_points(audio, merged_ranges)
    
    return optimal_ranges
