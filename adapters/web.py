# --- adapters/web.py ---
from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from application.services import AudioAnalysisService
from domain.audio_analysis import AudioAnalyzer
from fastapi.templating import Jinja2Templates
import os
import json
from utils.logger import logger


# Configurando os templates
templates = Jinja2Templates(directory="frontend/templates")

favicon_path = 'favicon.ico'

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

analyzer = AudioAnalyzer()
service = AudioAnalysisService(analyzer)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Adicione este middleware ao seu app FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/service-worker.js", response_class=FileResponse)
async def get_service_worker():
    return FileResponse("frontend/service-worker.js", media_type="application/javascript")


@app.post("/start-analysis")
async def start_analysis(file: UploadFile, request: Request):
    logger.info(f"Recebido arquivo: {file.filename}")
    user_info = request.headers.get("x-user-info")
    user_id = None
    if user_info:
        try:
            user_data = json.loads(user_info)
            user_id = service.save_user_info(user_data)
            logger.info(f"Dados do usuário salvos. ID: {user_id}")
        except Exception as e:
             logger.warning(f"Falha ao salvar usuário: {e}")

    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        result = service.analyze_audio_file(file_path)
        service._save_to_database(result, user_id=user_id)
        logger.info("Resultado da análise retornado.")
        return JSONResponse(content=result.dict())

    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/fft-plot")
def get_fft_plot():
    plot_path = "fft_plot.png"
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="FFT plot not found")
    return FileResponse(plot_path)


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile):
    with open(f"uploaded_audio/{file.filename}", "wb") as audio_file:
        audio_file.write(await file.read())
    return {"filename": file.filename}


# @app.post("/user-info")
# async def save_user_info(user_data: dict = Body(...)):
#     try:
#         user_id = service.save_user_info(user_data)
#         return {"user_id": user_id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Página 1 - Carregar Áudio
@app.get("/page1", response_class=HTMLResponse)
async def page1(request: Request):
    return templates.TemplateResponse("page1.html", {"request": request})


# Página 2 - Gravar Áudio
@app.get("/page2", response_class=HTMLResponse)
async def page2(request: Request):
    return templates.TemplateResponse("page2.html", {"request": request})


# Página 3 - Carregar Resultados DB
@app.get("/page3", response_class=HTMLResponse)
async def page3(request: Request):
    return templates.TemplateResponse("page3.html", {"request": request})


# Página 4 - Tutorial
@app.get("/page4", response_class=HTMLResponse)
async def page4(request: Request):
    return templates.TemplateResponse("page4.html", {"request": request})


# Página Termo de Consentimento
@app.get("/consent", response_class=HTMLResponse)
async def serve_consent(request: Request):
    return templates.TemplateResponse("consent.html", {"request": request})


@app.get("/instructions", response_class=HTMLResponse)
def instructions(request: Request):
    return templates.TemplateResponse("instructions.html", {"request": request})


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
