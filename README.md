#PhonIA - Phono + IA = Aplicativo dedicado à Fonoaudiologia com aplicação de IA


# Estrutura do Projeto
O presente aplicativo está sendo desenvolvido utilizando a arquitetura hexagonal de forma a facilitar upgrades futuros e a própria manutenção do código, permitindo a substituição de módulos e tecnologias utilizadas de forma facilitada.

## Domain Layer (Core Logic):
Contém a lógica central para análise de jitter e shimmer.
Classe: AudioAnalyzer

## Application Layer:
Faz a ponte entre a lógica central e as interfaces de entrada/saída.
Classe: AudioAnalysisService

## Adapter Layer (Web Interface):
Interface web construída com FastAPI.
Permite o upload de arquivos .wav e retorna os resultados de jitter e shimmer.

## main.py: 
Ponto de entrada que conecta todas as camadas, seguindo o princípio da independência de domínio.



### Rodar o servidor
Execute o servidor FastAPI:

uvicorn main:app --reload

O servidor estará disponível em http://127.0.0.1:8000.


### Interagir com a interface web
Acesse o frontend: Abra http://127.0.0.1:8000 no navegador. A página exibirá um formulário para enviar arquivos .wav para análise.

Enviar arquivos: Escolha um arquivo .wav e clique em "Analyze".
O servidor processará o arquivo e retornará as métricas de Jitter, Shimmer e Frequência Fundamental (F0).

Resultados: Os resultados serão exibidos diretamente na página.
As análises também serão armazenadas no banco de dados SQLite (analysis_history.db) para rastreamento futuro.


### Personalização do Frontend
Os arquivos na pasta frontend/ podem ser personalizados:

index.html: Estrutura HTML.
app.js: Lógica para envio e recepção de dados.
styles.css: Estilização da página.

### Testar a API diretamente (opcional)
A API também aceita requisições via ferramentas como Postman ou curl:

curl -X POST "http://127.0.0.1:8000/analyze-audio" -F "file=@path/to/your/file.wav"
