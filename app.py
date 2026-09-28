import uuid
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel

from draftgpt_core.ingestion.step_loader import STEPFileLoader
from draftgpt_core.geometry.feature_detector import FeatureDetector
from draftgpt_core.engine.view_planner import ViewPlanner
from draftgpt_core.exporter.dxf_generator import DXFDrawingGenerator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DraftGPT API",
    description="AI-Powered Engineering Detailing Platform API",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job tracker for MVP (substitute with PostgreSQL + Celery in production)
JOBS_DB: Dict[str, Dict[str, Any]] = {}
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class ReviewApprovalRequest(BaseModel):
    reviewer_notes: str
    approved: bool


def process_cad_file_task(job_id: str, file_path: Path):
    """Background task executing the CAD processing pipeline."""
    try:
        JOBS_DB[job_id]["status"] = "PROCESSING"

        # Phase 1: Ingestion & Feature Extraction
        loader = STEPFileLoader(file_path)
        shape = loader.load()
        metadata = loader.get_metadata()

        detector = FeatureDetector(shape, filename=file_path.name)
        features = detector.analyze()

        # Phase 2: View Planning
        planner = ViewPlanner(feature_summary=features, metadata=metadata)
        sheet_layout = planner.plan_drawing_sheet(sheet_size="A3")

        # Phase 3: DXF Generation
        dxf_path = OUTPUT_DIR / f"{job_id}_drawing.dxf"
        exporter = DXFDrawingGenerator(sheet_layout)
        exporter.build_dxf(dxf_path)

        # Flag items requiring review (e.g. multiple hole patterns or high face count)
        flagged = []
        if len(features.hole_patterns) > 2:
            flagged.append({
                "code": "MULTIPLE_HOLE_PATTERNS",
                "message": f"Detected {len(features.hole_patterns)} hole patterns. Please verify dimensions."
            })

        # Update Job Record
        JOBS_DB[job_id].update({
            "status": "NEEDS_REVIEW" if flagged else "COMPLETED",
            "metadata": metadata,
            "layout": sheet_layout.model_dump(),
            "dxf_path": str(dxf_path.resolve()),
            "flagged_items": flagged
        })

    except Exception as e:
        JOBS_DB[job_id]["status"] = "FAILED"
        JOBS_DB[job_id]["error"] = str(e)


@app.post("/api/v1/drawings/upload", status_code=202)
async def upload_cad_model(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...)
):
    """Uploads a STEP file and initiates drawing generation."""
    if not file.filename.lower().endswith((".step", ".stp")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .step and .stp supported.")

    job_id = str(uuid.uuid4())
    saved_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    with open(saved_path, "wb") as f:
        f.write(await file.read())

    JOBS_DB[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "status": "PENDING",
        "file_path": str(saved_path),
        "flagged_items": []
    }

    # Queue background task
    background_tasks.add_task(process_cad_file_task, job_id, saved_path)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "status": "PENDING",
        "message": "CAD file uploaded successfully. Processing started."
    }


@app.get("/api/v1/drawings/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Retrieves status, metadata, and generated layout for a specific job."""
    if job_id not in JOBS_DB:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    return JOBS_DB[job_id]


@app.post("/api/v1/drawings/jobs/{job_id}/review")
async def approve_or_reject_drawing(job_id: str, review: ReviewApprovalRequest):
    """Allows an engineer to sign off or request changes on a generated drawing."""
    if job_id not in JOBS_DB:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    job = JOBS_DB[job_id]
    job["reviewer_notes"] = review.reviewer_notes
    job["status"] = "APPROVED" if review.approved else "REJECTED"

    return {
        "job_id": job_id,
        "status": job["status"],
        "message": f"Drawing review updated to {job['status']}."
    }