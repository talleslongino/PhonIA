# --- adapters/web.py ---
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from application.services import AudioAnalysisService
from domain.audio_analysis import AudioAnalyzer
import os


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
async def start_analysis(file: UploadFile):
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        result = service.analyze_audio_file(file_path)
        return JSONResponse(content=result.dict())

    except Exception as e:
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

@app.get("/")
def serve_frontend():
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)
