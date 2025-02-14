#!/usr/bin/env python3
import os
import argparse
from dotenv import load_dotenv
from src import (
    setup_folders,
    get_clips_info,
    get_ai_script,
    parse_ai_response,
    create_final_video,
    remove_duplicate_content
)

def parse_arguments():
    """Configura e processa argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Editor de Vídeo com IA - Cria vídeos automaticamente usando IA'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='video_final.mp4',
        help='Nome do arquivo de saída (padrão: video_final.mp4)'
    )
    
    parser.add_argument(
        '--clips-dir',
        type=str,
        default='clips',
        help='Diretório contendo os clips de entrada (padrão: clips)'
    )
    
    parser.add_argument(
        '--temp-dir',
        type=str,
        default='temp',
        help='Diretório para arquivos temporários (padrão: temp)'
    )
    
    return parser.parse_args()

def main():
    """Função principal do editor de vídeo"""
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica a chave da API
    if not os.getenv('OPENAI_API_KEY'):
        print("Erro: OPENAI_API_KEY não encontrada!")
        print("Por favor, crie um arquivo .env com sua chave da API OpenAI")
        return
    
    # Processa argumentos da linha de comando
    args = parse_arguments()
    
    try:
        # Configuração inicial
        print("\n=== Editor de Vídeo com IA ===")
        setup_folders()
        
        # Passo 1: Processar arquivos
        print("\n1. Processando clips de entrada...")
        clips_info = get_clips_info()
        
        if not clips_info:
            print(f"\nNenhum clip encontrado no diretório '{args.clips_dir}'")
            print("Coloque seus vídeos no diretório 'clips' e tente novamente")
            return
            
        print(f"✓ {len(clips_info)} clips processados com sucesso")
        
        # Passo 1.5: Remover conteúdo duplicado usando GPT
        print("\n1.5. Analisando e removendo conteúdo repetido...")
        original_count = len(clips_info)
        clips_info = remove_duplicate_content(clips_info)
        removed_count = original_count - len(clips_info)
        if removed_count > 0:
            print(f"✓ {removed_count} clips com conteúdo repetido removidos")
        else:
            print("✓ Nenhum conteúdo repetido encontrado")
        
        # Passo 2: Gerar script com IA
        print("\n2. Analisando conteúdo e gerando narrativa...")
        ai_response = get_ai_script(clips_info)
        
        # Passo 3: Extrair narrativa e ordem dos clips
        print("\n3. Interpretando resposta da IA...")
        narrative, clips_order, clips_timing = parse_ai_response(ai_response)
        
        print("\nNarrativa gerada:")
        print("-" * 50)
        print(narrative)
        print("-" * 50)
        
        print("\nSequência de edição:")
        print(f"Ordem dos clips: {clips_order}")
        print(f"Tempos dos clips: {clips_timing}")
        
        # Passo 4: Criar vídeo final
        print("\n4. Criando vídeo final...")
        create_final_video(clips_order, clips_info, clips_timing)
        
        print("\n✨ Processo concluído com sucesso! ✨")
        print(f"O vídeo final foi salvo como: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro durante o processamento: {str(e)}")
        raise

if __name__ == "__main__":
    main()
