import os
from pathlib import Path
from celery import Celery

from draftgpt_core.ingestion.step_loader import STEPFileLoader
from draftgpt_core.geometry.feature_detector import FeatureDetector
from draftgpt_core.engine.view_planner import ViewPlanner
from draftgpt_core.exporter.dxf_generator import DXFDrawingGenerator

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("draftgpt_tasks", broker=redis_url, backend=redis_url)


@celery_app.task(name="process_cad_task")
def process_cad_task(job_id: str, file_path_str: str, output_dir_str: str):
    file_path = Path(file_path_str)
    output_dir = Path(output_dir_str)

    # Phase 1: Feature Extraction
    loader = STEPFileLoader(file_path)
    shape = loader.load()
    metadata = loader.get_metadata()

    detector = FeatureDetector(shape, filename=file_path.name)
    features = detector.analyze()

    # Phase 2: View Planning
    planner = ViewPlanner(feature_summary=features, metadata=metadata)
    sheet_layout = planner.plan_drawing_sheet(sheet_size="A3")

    # Phase 3: DXF Generation
    dxf_path = output_dir / f"{job_id}_drawing.dxf"
    exporter = DXFDrawingGenerator(sheet_layout)
    exporter.build_dxf(dxf_path)

    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "dxf_path": str(dxf_path.resolve()),
        "metadata": metadata,
        "layout": sheet_layout.model_dump()
    }