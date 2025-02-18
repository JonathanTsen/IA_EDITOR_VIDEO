
# Instruções para Adicionar um Backend e Implantar no Render.com

## 1. Introdução

Este documento fornece um passo a passo para adicionar um backend (Flask ou Django) ao seu projeto de edição de vídeo e implantá-lo no Render.com. O objetivo é permitir que usuários enviem vídeos para processamento e obtenham o resultado final por meio de uma interface web.

## 2. Configuração do Backend

Escolha entre Flask ou Django para criar o backend.

### 2.1 Flask

1. Instale o Flask:
   ```bash
   pip install flask flask-cors werkzeug
   ```
2. Crie um arquivo `app.py`:
   ```python
   from flask import Flask, request, jsonify
   import os

   app = Flask(__name__)
   UPLOAD_FOLDER = 'uploads'
   os.makedirs(UPLOAD_FOLDER, exist_ok=True)

   @app.route('/upload', methods=['POST'])
   def upload_file():
       if 'file' not in request.files:
           return jsonify({'error': 'Nenhum arquivo enviado'}), 400

       file = request.files['file']
       filepath = os.path.join(UPLOAD_FOLDER, file.filename)
       file.save(filepath)
       return jsonify({'message': 'Arquivo enviado com sucesso', 'path': filepath})

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```
3. Teste localmente:
   ```bash
   python app.py
   ```

### 2.2 Django

1. Instale o Django:
   ```bash
   pip install django djangorestframework
   ```
2. Crie um novo projeto:
   ```bash
   django-admin startproject videoprocessor
   cd videoprocessor
   ```
3. Crie um aplicativo para upload:
   ```bash
   python manage.py startapp upload
   ```
4. Adicione `upload` e `rest_framework` ao `INSTALLED_APPS` em `settings.py`.
5. Crie um `views.py` para lidar com uploads:
   ```python
   from rest_framework.decorators import api_view
   from rest_framework.response import Response
   from django.core.files.storage import default_storage

   @api_view(['POST'])
   def upload_video(request):
       file = request.FILES.get('file')
       if not file:
           return Response({'error': 'Nenhum arquivo enviado'}, status=400)

       file_path = default_storage.save(file.name, file)
       return Response({'message': 'Arquivo enviado', 'path': file_path})
   ```
6. Adicione as rotas em `urls.py`:
   ```python
   from django.urls import path
   from .views import upload_video

   urlpatterns = [
       path('upload/', upload_video),
   ]
   ```
7. Rode o servidor:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## 3. Configuração do Frontend (Básico)

Crie um `index.html` para permitir o upload de arquivos:

```html
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload de Vídeo</title>
</head>
<body>
    <h1>Envie um Vídeo</h1>
    <input type="file" id="videoFile">
    <button onclick="uploadFile()">Enviar</button>
    <script>
        function uploadFile() {
            let fileInput = document.getElementById('videoFile');
            let file = fileInput.files[0];
            let formData = new FormData();
            formData.append('file', file);
          
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error(error));
        }
    </script>
</body>
</html>
```

## 4. Implantando no Render.com

### 4.1 Criando o Repositório no GitHub

1. Crie um repositório no GitHub e envie o código:
   ```bash
   git init
   git add .
   git commit -m "Primeiro commit"
   git branch -M main
   git remote add origin https://github.com/seu-usuario/seu-repositorio.git
   git push -u origin main
   ```

### 4.2 Criando o Serviço no Render

1. Acesse [Render.com](https://render.com/) e faça login.
2. Clique em **+ New** >  **Web Service** .
3. Conecte seu repositório do GitHub.
4. Escolha a branch `main` e defina:

   * **Runtime** : Python 3.x
   * **Build Command** :

   ```bash
   pip install -r requirements.txt
   ```

   * **Start Command** :
   * Flask: `gunicorn app:app`
   * Django: `gunicorn videoprocessor.wsgi`
5. Clique em  **Deploy** .
6. Acesse a URL gerada (`https://seu-app.onrender.com`).

## 5. Conclusão

Agora, você tem um backend que processa vídeos e está implantado no Render.com. O frontend básico permite uploads e integração com o backend.
