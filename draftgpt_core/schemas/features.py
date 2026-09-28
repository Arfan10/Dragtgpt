from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class FeatureType(str, Enum):
    PLANE = "plane"
    CYLINDER_HOLE = "cylinder_hole"
    CYLINDER_BOSS = "cylinder_boss"
    PARALLEL_PAIR = "parallel_pair"


class Vector3D(BaseModel):
    x: float
    y: float
    z: float

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


class PlanarFeature(BaseModel):
    face_id: int
    location: Vector3D
    normal: Vector3D
    area_mm2: float


class CylindricalFeature(BaseModel):
    face_id: int
    feature_type: FeatureType  # CYLINDER_HOLE or CYLINDER_BOSS
    radius_mm: float
    diameter_mm: float
    location: Vector3D
    axis_direction: Vector3D
    is_through_hole: Optional[bool] = None
    depth_mm: Optional[float] = None


class ParallelPlanePair(BaseModel):
    face_id_1: int
    face_id_2: int
    distance_mm: float
    normal: Vector3D


class HolePattern(BaseModel):
    pattern_id: str
    diameter_mm: float
    hole_count: int
    axis_direction: Vector3D
    face_ids: List[int]
    locations: List[Vector3D]


class ExtractedFeaturesSummary(BaseModel):
    filename: str
    total_faces_processed: int
    planes: List[PlanarFeature]
    cylinders: List[CylindricalFeature]
    parallel_pairs: List[ParallelPlanePair]
    hole_patterns: List[HolePattern]