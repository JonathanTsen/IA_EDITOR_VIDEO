# Editor de Vídeo com IA

Este é um editor de vídeo automatizado que utiliza Inteligência Artificial para criar vídeos de forma inteligente. O sistema analisa clips de vídeo, gera uma narrativa coerente e cria um vídeo final editado automaticamente.

## Funcionalidades

- Processamento automático de múltiplos clips de vídeo
- Detecção e remoção de conteúdo duplicado usando IA
- Geração automática de narrativa usando GPT
- Ordenação inteligente dos clips
- Criação automática do vídeo final

## Pré-requisitos

- Python 3.6 ou superior
- FFmpeg instalado no sistema
- Chave de API da OpenAI

## Instalação

1. Clone o repositório:
```bash
git clone [seu-repositorio]
cd [seu-diretorio]
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione sua chave da API OpenAI:
   ```
   OPENAI_API_KEY=sua-chave-aqui
   ```

## Como Usar

1. Coloque seus clips de vídeo na pasta `clips/`

2. Execute o script principal:
```bash
python main.py
```

### Opções disponíveis:

- `--output`: Nome do arquivo de saída (padrão: video_final.mp4)
- `--clips-dir`: Diretório contendo os clips de entrada (padrão: clips)
- `--temp-dir`: Diretório para arquivos temporários (padrão: temp)

Exemplo com opções personalizadas:
```bash
python main.py --output meu_video.mp4 --clips-dir meus_clips
```

## Estrutura do Projeto

- `main.py`: Script principal do programa
- `src/`: Módulos do projeto
  - `audio_processor.py`: Processamento de áudio
  - `transcription.py`: Transcrição de áudio
- `clips/`: Diretório para os clips de entrada
- `temp/`: Diretório para arquivos temporários

## Dependências Principais

- moviepy: Processamento e edição de vídeo
- python-dotenv: Gerenciamento de variáveis de ambiente
- openai: Integração com a API da OpenAI
- ffmpeg-python: Interface com FFmpeg
- pydub: Processamento de áudio

## Notas

- Certifique-se de ter espaço suficiente em disco para os arquivos temporários
- A qualidade da edição depende da qualidade dos clips de entrada
- O tempo de processamento pode variar dependendo do tamanho e quantidade dos clips
