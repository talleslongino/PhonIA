# --- adapters/web.py ---
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from application.services import AudioAnalysisService
from domain.audio_analysis import AudioAnalyzer

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

analyzer = AudioAnalyzer()
service = AudioAnalysisService(analyzer)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile):
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Save file locally
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Analyze the audio file
        result = service.analyze_audio_file(file_path)
        return JSONResponse(content=result.dict())

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up
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
