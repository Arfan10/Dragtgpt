from enum import Enum
from typing import List, Tuple, Optional
from pydantic import BaseModel
from draftgpt_core.schemas.features import Vector3D, HolePattern


class ViewType(str, Enum):
    FRONT = "FRONT"
    TOP = "TOP"
    RIGHT = "RIGHT"
    ISOMETRIC = "ISOMETRIC"


class Projection2D(BaseModel):
    x: float
    y: float


class BoundingDimension2D(BaseModel):
    dimension_type: str  # "WIDTH", "HEIGHT", "DEPTH"
    value_mm: float
    start_point: Projection2D
    end_point: Projection2D
    label: str


class HoleAnnotation2D(BaseModel):
    pattern_id: str
    callout_text: str  # e.g., "4x Ø10.00 THRU"
    center_location: Projection2D


class ViewLayout(BaseModel):
    view_type: ViewType
    scale: float
    center_offset: Projection2D
    bounding_box_2d: Tuple[float, float]  # (width_mm, height_mm)
    dimensions: List[BoundingDimension2D]
    hole_annotations: List[HoleAnnotation2D]


class DrawingSheetLayout(BaseModel):
    part_name: str
    sheet_size: str  # "A3", "A4"
    views: List[ViewLayout]