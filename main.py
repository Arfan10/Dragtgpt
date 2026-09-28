import sys
import json
from pathlib import Path

from draftgpt_core.ingestion.step_loader import STEPFileLoader
from draftgpt_core.geometry.feature_detector import FeatureDetector
from draftgpt_core.engine.view_planner import ViewPlanner
from draftgpt_core.exporter.dxf_generator import DXFDrawingGenerator


def run_pipeline(step_file_path: str, output_dxf_path: str = "output/drawing.dxf"):
    """Executes Phase 1, Phase 2, and Phase 3 of the DraftGPT pipeline."""
    # Phase 1: STEP Loading & Feature Extraction
    loader = STEPFileLoader(step_file_path)
    shape = loader.load()
    metadata = loader.get_metadata()

    detector = FeatureDetector(shape, filename=loader.file_path.name)
    features = detector.analyze()

    # Phase 2: View Planning & Rules Engine
    planner = ViewPlanner(feature_summary=features, metadata=metadata)
    sheet_layout = planner.plan_drawing_sheet(sheet_size="A3")

    # Phase 3: DXF Drawing Generation
    exporter = DXFDrawingGenerator(sheet_layout)
    saved_path = exporter.build_dxf(output_dxf_path)

    print(f"Successfully generated shop-floor ready drawing: {saved_path.resolve()}")
    return sheet_layout, saved_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "samples/sample_part.step"

    if Path(file_path).exists():
        print(f"Running DraftGPT pipeline on: {file_path}...\n")
        run_pipeline(file_path, "output/sample_drawing.dxf")
    else:
        print(f"File not found: {file_path}")
        print("Usage: python main.py <path_to_step_file.step>")