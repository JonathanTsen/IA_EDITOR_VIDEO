import multiprocessing

# Configuração do Gunicorn para o Render
bind = "0.0.0.0:10000"  # Porta que o Render usa
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 300  # Aumentado para processar vídeos maiores
worker_class = 'sync'
accesslog = '-'
errorlog = '-'
