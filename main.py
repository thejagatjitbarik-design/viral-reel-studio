import os
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
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

# Mount exports so videos can be streamed directly in browser
app.mount("/exports", StaticFiles(directory=str(EXPORTS_DIR)), name="exports")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Viral Reel Studio"}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = BASE_DIR / "static" / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>Viral Reel Studio is Running!</h1>"

@app.post("/api/process-video")
async def api_process_video(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())[:8]
    temp_dir = SCRATCH_DIR / task_id
    raw_path = UPLOADS_DIR / f"{task_id}_{file.filename}"
    output_filename = f"Reel_{task_id}.mp4"
    output_path = EXPORTS_DIR / output_filename

    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        compose_from_raw_video(raw_path, output_path, temp_dir)
        return {
            "success": True,
            "filename": output_filename,
            "video_url": f"/exports/{output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp scratch frames
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/generate-from-prompt")
async def api_generate_from_prompt(
    prompt: str = Form(...),
    voice: str = Form("en-US-ChristopherNeural")
):
    task_id = str(uuid.uuid4())[:8]
    temp_dir = SCRATCH_DIR / task_id
    output_filename = f"AI_Reel_{task_id}.mp4"
    output_path = EXPORTS_DIR / output_filename

    try:
        compose_from_prompt(prompt, output_path, temp_dir, voice=voice)
        return {
            "success": True,
            "filename": output_filename,
            "video_url": f"/exports/{output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
