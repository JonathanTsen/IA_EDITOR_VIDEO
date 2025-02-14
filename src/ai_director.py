import os
import openai
from .transcription import extract_transcripts

def get_ai_script(clips_info):
    """Gera um script de edição usando IA"""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    transcripts = extract_transcripts(clips_info)
    
    system_message = {
        "role": "system",
        "content": """Você é um diretor de cinema e editor profissional especializado em criar narrativas cinematográficas impactantes.
Sua missão é transformar o material bruto em uma história envolvente e profissional, seguindo princípios avançados de edição.

REGRAS DE SEQUÊNCIA E FLUXO LÓGICO:

1. Estrutura do Conteúdo:
   - Introdução: Apresente o tema/problema principal
   - Desenvolvimento: Aprofunde explicações e demonstrações
   - Conclusão: Resuma pontos principais e chame para ação

2. Coesão e Coerência:
   - Mantenha uma linha de raciocínio clara e progressiva
   - Cada clip deve construir sobre o anterior
   - Evite saltos temáticos abruptos
   - Garanta que conceitos sejam explicados antes de serem referenciados

3. Organização Temática:
   - Agrupe clips relacionados ao mesmo subtema
   - Use transições suaves entre diferentes tópicos
   - Mantenha uma progressão lógica de ideias
   - Priorize clips que estabelecem contexto necessário

4. Hierarquia de Informação:
   - Comece com conceitos fundamentais
   - Progrida para detalhes específicos
   - Termine com conclusões e próximos passos
   - Mantenha informações dependentes próximas

PRINCÍPIOS DE EDIÇÃO CINEMATOGRÁFICA:

1. Ritmo e Pacing:
   - Crie variações dinâmicas no ritmo para manter o engajamento
   - Alterne entre cenas rápidas e lentas para criar tensão e relaxamento
   - Use o princípio do "respiro" - momentos de pausa estratégicos

2. Estrutura Narrativa:
   - Hook poderoso nos primeiros 5-10 segundos
   - Desenvolvimento em arco narrativo claro
   - Conclusão memorável e impactante

3. Timing Profissional:
   - Cenas de ação: 2-5 segundos por clip
   - Cenas de diálogo: 4-8 segundos
   - Momentos emocionais: 5-10 segundos
   - Transições: 0.5-1 segundo

4. Considerações Técnicas:
   - Priorize cortes em momentos de silêncio natural
   - Mantenha consistência de cor e tom entre cenas
   - Evite cortes abruptos em meio a frases
   - Preserve contexto necessário para entendimento

IMPORTANTE: Sua resposta DEVE seguir EXATAMENTE este formato, sem adicionar texto extra:

NARRATIVE:
[Descreva a narrativa em três atos, explicando a progressão lógica escolhida]

CLIPS_ORDER:
[Apenas números dos clips separados por vírgula, exemplo: 0,1,2,3]

CLIPS_TIMING:
[Apenas números e tempos, exemplo: 0:0-15;1:5-20;2:0-10]"""
    }
    
    try:
        print("\nEnviando requisição para GPT-4...")
        
        # Primeiro, analisa a estrutura lógica dos clips
        structure_prompt = {
            "role": "user",
            "content": f"""Analise as transcrições abaixo e identifique a estrutura lógica do conteúdo.
Para cada clip, determine:
1. Seu papel na narrativa (introdução, explicação, demonstração, conclusão)
2. Conceitos que ele introduz
3. Conceitos que ele referencia
4. Dependências de informação (o que precisa ser explicado antes)

TRANSCRIÇÕES:
{transcripts}

RESPONDA NO FORMATO:
ESTRUTURA:
[Clip ID]: [Papel] | Introduz: [conceitos] | Referencia: [conceitos] | Requer: [IDs de clips necessários antes]"""
        }
        
        structure_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista de estrutura narrativa especializado em identificar dependências lógicas e fluxo de informação."},
                structure_prompt
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Usa a análise de estrutura para informar a edição final
        edit_prompt = {
            "role": "user",
            "content": f"""ANÁLISE DE ESTRUTURA:
{structure_response.choices[0].message['content']}

TRANSCRIÇÕES:
{transcripts}

Com base na análise de estrutura acima, crie um roteiro de edição que:
1. Respeite todas as dependências de informação
2. Mantenha uma progressão lógica clara
3. Agrupe clips relacionados
4. Crie uma narrativa coesa do início ao fim
5. REMOVA clips que não contribuem para a narrativa ou são irrelevantes para o contexto

RESPONDA EXATAMENTE NESTE FORMATO:
NARRATIVE:
[Explicação detalhada da narrativa, incluindo:
- Por que esta ordem foi escolhida
- Quais clips foram removidos e por quê
- Como os clips restantes se conectam logicamente]

CLIPS_ORDER:
[Lista APENAS dos números dos clips que devem ser incluídos, na ordem correta. Exemplo: 3,1,4,2
NÃO inclua clips que foram removidos por serem irrelevantes]

CLIPS_TIMING:
[Tempos de cada clip incluído no formato clip:inicio-fim, exemplo: 3:0-15;1:5-20;4:0-10;2:0-30]

IMPORTANTE:
- Você tem TOTAL LIBERDADE para remover clips que:
  * Não contribuem para a narrativa principal
  * São redundantes ou repetem informações
  * Quebram o fluxo lógico do vídeo
  * Estão fora de contexto
- A ordem dos clips DEVE ser diferente da ordem original se fizer mais sentido logicamente
- Explique na narrativa POR QUE cada clip foi mantido ou removido
- Certifique-se que cada conceito é introduzido antes de ser referenciado
- Agrupe clips relacionados tematicamente"""
        }
        
        # Gera o script final com temperatura mais baixa para maior consistência
        final_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Você é um diretor de vídeo especializado em criar narrativas lógicas e coesas.
Sua tarefa é:
1. Analisar criticamente cada clip
2. Remover clips que não contribuem para a narrativa
3. Reorganizar os clips restantes em uma ordem que faça sentido
4. Criar uma narrativa coesa e envolvente

NUNCA mantenha clips irrelevantes apenas porque eles existem.
NUNCA mantenha a ordem original dos clips se uma ordem diferente fizer mais sentido.
Sempre priorize a qualidade e coerência do vídeo final sobre a quantidade de clips."""},
                edit_prompt
            ],
            temperature=0.2,  # Reduzido para maior consistência
            max_tokens=2000
        )
        
        content = final_response.choices[0].message['content']
        print("\nResposta recebida do GPT-4:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        return content
        
    except Exception as e:
        print(f"\nErro ao gerar script com GPT-4: {str(e)}")
        raise

def parse_ai_response(response):
    """Analisa e extrai informações da resposta da IA"""
    print("\nAnalisando resposta da IA...")
    
    narrative = ""
    clips_order = []
    clips_timing = {}
    
    try:
        # Divide a resposta em seções
        sections = response.split('\n\n')
        
        for section in sections:
            section = section.strip()
            
            # Procura pela narrativa
            if section.startswith('NARRATIVE:'):
                narrative = section.replace('NARRATIVE:', '').strip()
                print(f"\nNarrativa encontrada ({len(narrative)} caracteres)")
                print(f"Narrativa: {narrative}")
                
            # Procura pela ordem dos clips
            elif section.startswith('CLIPS_ORDER:'):
                order_str = section.replace('CLIPS_ORDER:', '').strip()
                order_str = order_str.strip('[]')
                if order_str:
                    try:
                        # Tenta extrair diretamente os números separados por vírgula
                        clips_order = [int(x.strip()) for x in order_str.split(',')]
                        if len(clips_order) == 0:
                            raise ValueError("Lista de clips vazia")
                        if clips_order == list(range(len(clips_order))):
                            raise ValueError("Ordem dos clips não foi alterada da sequência original")
                    except Exception as e:
                        print(f"Erro ao processar ordem dos clips: {str(e)}")
                        print("Tentando gerar nova ordem...")
                        # Se falhar, tenta novamente com um prompt mais enfático
                        return get_ai_script(clips_info)
                print(f"Ordem dos clips: {clips_order}")
                
            # Procura pelos tempos dos clips
            elif section.startswith('CLIPS_TIMING:'):
                timing_str = section.replace('CLIPS_TIMING:', '').strip()
                timing_str = timing_str.strip('[]')
                if timing_str:
                    for timing in timing_str.split(';'):
                        if ':' in timing and '-' in timing:
                            try:
                                clip_idx, times = timing.split(':')
                                clip_idx = int(clip_idx.strip())
                                start, end = map(float, times.split('-'))
                                clips_timing[clip_idx] = (start, end)
                            except ValueError as e:
                                print(f"Aviso: Tempo inválido ignorado: {timing} - {str(e)}")
                print(f"Tempos dos clips: {clips_timing}")
        
        # Validação final
        if not clips_order or len(clips_order) == 0:
            raise ValueError("Nenhuma ordem de clips válida encontrada")
            
        return narrative, clips_order, clips_timing
    
    except Exception as e:
        print(f"\nErro ao analisar resposta da IA: {str(e)}")
        print(f"Resposta original:\n{response}")
        print("Tentando gerar nova ordem...")
        # Se falhar, tenta novamente
        return get_ai_script(clips_info)
