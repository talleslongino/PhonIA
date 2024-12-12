# --- adapters/web.py ---
from concurrent.futures import ThreadPoolExecutor
import threading
import uuid
import time
import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from application.services import AudioAnalysisService
from domain.audio_analysis import AudioAnalyzer

executor = ThreadPoolExecutor(max_workers=4)
tasks = {}  # Estrutura: {task_id: {"future": Future, "timestamp": timestamp}}


def clean_old_tasks(timeout: int = 300):
    """
    Remove tarefas antigas do dicionário `tasks`.
    """
    current_time = time.time()
    to_remove = []

    for task_id, task_data in tasks.items():
        if current_time - task_data["timestamp"] > timeout:
            to_remove.append(task_id)

    for task_id in to_remove:
        del tasks[task_id]


def periodic_task_cleanup(interval: int = 60, timeout: int = 300):
    """
    Executa a limpeza de tarefas periodicamente.
    """
    while True:
        clean_old_tasks(timeout)
        time.sleep(interval)


# Inicia a thread de limpeza ao iniciar a aplicação
cleanup_thread = threading.Thread(target=periodic_task_cleanup, daemon=True)
cleanup_thread.start()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

analyzer = AudioAnalyzer()
service = AudioAnalysisService(analyzer)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.post("/start-analysis")
async def start_analysis(file: UploadFile):
    clean_old_tasks()  # Limpa tarefas antigas ao adicionar uma nova
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        task_id = str(uuid.uuid4())
        future = executor.submit(service.analyze_audio_file, file_path)
        tasks[task_id] = {"future": future, "timestamp": time.time()}
        return {"task_id": task_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    future = tasks[task_id]
    if future.done():
        try:
            result = future.result()
            del tasks[task_id]  # Remove a tarefa concluída
            return {"status": "completed", "result": result.dict()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    else:
        return {"status": "in_progress"}


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
