# --- api/main.py ---
from mangum import Mangum  # Adiciona compatibilidade com serverless
from adapters.web import app as fastapi_app  # Importa módulos

app = fastapi_app  # O app existente no projeto
handler = Mangum(app)  # Configuração necessária para o Vercel
