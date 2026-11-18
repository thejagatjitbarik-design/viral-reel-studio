import os
import shutil
import uuid
import gc
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pipeline.composer import compose_from_raw_video, compose_from_prompt

app = FastAPI(title="Viral Reel Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"
SCRATCH_DIR = BASE_DIR / "scratch"

for d in [UPLOADS_DIR, EXPORTS_DIR, SCRATCH_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Mount exports so rendered videos stream directly in browser
app.mount("/exports", StaticFiles(directory=str(EXPORTS_DIR)), name="exports")

# In-memory dictionary tracking async jobs
TASKS: dict = {}

def update_task_status(task_id: str, status: str, progress: int = 0, message: str = "", video_url: str = None, error: str = None):
    TASKS[task_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "video_url": video_url,
        "error": error
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Viral Reel Studio"}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = BASE_DIR / "static" / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>Viral Reel Studio is Running!</h1>"

def process_video_worker(task_id: str, raw_path: Path, output_path: Path, temp_dir: Path, output_filename: str):
    try:
        compose_from_raw_video(raw_path, output_video=output_path, temp_dir=temp_dir, task_id=task_id, status_fn=update_task_status)
        update_task_status(
            task_id=task_id,
            status="completed",
            progress=100,
            message="Your viral reel is ready!",
            video_url=f"/exports/{output_filename}"
        )
    except Exception as e:
        update_task_status(task_id=task_id, status="failed", progress=0, message="Processing failed", error=str(e))
    finally:
        gc.collect()
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

def process_prompt_worker(task_id: str, prompt: str, voice: str, output_path: Path, temp_dir: Path, output_filename: str):
    try:
        compose_from_prompt(prompt, output_video=output_path, temp_dir=temp_dir, voice=voice, task_id=task_id, status_fn=update_task_status)
        update_task_status(
            task_id=task_id,
            status="completed",
            progress=100,
            message="Your viral reel is ready!",
            video_url=f"/exports/{output_filename}"
        )
    except Exception as e:
        update_task_status(task_id=task_id, status="failed", progress=0, message="Processing failed", error=str(e))
    finally:
        gc.collect()
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/process-video")
async def api_process_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())[:8]
    temp_dir = SCRATCH_DIR / task_id
    raw_path = UPLOADS_DIR / f"{task_id}_{file.filename}"
    output_filename = f"Reel_{task_id}.mp4"
    output_path = EXPORTS_DIR / output_filename

    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    update_task_status(task_id, "processing", 10, "Video uploaded. Starting AI pipeline...")
    background_tasks.add_task(process_video_worker, task_id, raw_path, output_path, temp_dir, output_filename)
    return {"success": True, "task_id": task_id}

@app.post("/api/generate-from-prompt")
async def api_generate_from_prompt(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    voice: str = Form("en-US-ChristopherNeural")
):
    task_id = str(uuid.uuid4())[:8]
    temp_dir = SCRATCH_DIR / task_id
    output_filename = f"AI_Reel_{task_id}.mp4"
    output_path = EXPORTS_DIR / output_filename

    update_task_status(task_id, "processing", 10, "Starting script & voiceover synthesis...")
    background_tasks.add_task(process_prompt_worker, task_id, prompt, voice, output_path, temp_dir, output_filename)
    return {"success": True, "task_id": task_id}

@app.get("/api/task-status/{task_id}")
def api_task_status(task_id: str):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
