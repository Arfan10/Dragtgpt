import math
from typing import List, Dict
from collections import defaultdict

from draftgpt_core.geometry.topology import TopologyExplorer
from draftgpt_core.schemas.features import (
    PlanarFeature,
    CylindricalFeature,
    ParallelPlanePair,
    HolePattern,
    ExtractedFeaturesSummary,
    FeatureType,
)


class FeatureDetector:
    """Analyzes topology primitives to group holes into patterns and find parallel thickness pairs."""

    def __init__(self, shape, filename: str = "model.step"):
        self.shape = shape
        self.filename = filename
        self.explorer = TopologyExplorer(shape)

    def analyze(self) -> ExtractedFeaturesSummary:
        planes, cylinders, total_faces = self.explorer.extract_primitives()
        
        parallel_pairs = self._detect_parallel_planes(planes)
        hole_patterns = self._detect_hole_patterns(cylinders)

        return ExtractedFeaturesSummary(
            filename=self.filename,
            total_faces_processed=total_faces,
            planes=planes,
            cylinders=cylinders,
            parallel_pairs=parallel_pairs,
            hole_patterns=hole_patterns,
        )

    def _detect_parallel_planes(self, planes: List[PlanarFeature], tol: float = 1e-3) -> List[ParallelPlanePair]:
        """Identifies pairs of opposing parallel faces to determine material thicknesses."""
        pairs: List[ParallelPlanePair] = []
        n = len(planes)

        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = planes[i], planes[j]

                # Dot product of normal vectors checking for opposite alignment (~ -1.0)
                dot_prod = (
                    p1.normal.x * p2.normal.x +
                    p1.normal.y * p2.normal.y +
                    p1.normal.z * p2.normal.z
                )

                if abs(dot_prod + 1.0) < tol:
                    # Calculate perpendicular distance along the normal vector
                    dx = p2.location.x - p1.location.x
                    dy = p2.location.y - p1.location.y
                    dz = p2.location.z - p1.location.z
                    dist = abs(dx * p1.normal.x + dy * p1.normal.y + dz * p1.normal.z)

                    pairs.append(
                        ParallelPlanePair(
                            face_id_1=p1.face_id,
                            face_id_2=p2.face_id,
                            distance_mm=round(dist, 4),
                            normal=p1.normal,
                        )
                    )

        return pairs

    def _detect_hole_patterns(self, cylinders: List[CylindricalFeature], tol: float = 1e-3) -> List[HolePattern]:
        """Groups cylindrical holes with identical diameters and parallel axis vectors into patterns."""
        holes = [c for c in cylinders if c.feature_type == FeatureType.CYLINDER_HOLE]
        
        # Key: (diameter_mm, abs(axis_x), abs(axis_y), abs(axis_z))
        grouped: Dict[tuple, List[CylindricalFeature]] = defaultdict(list)

        for hole in holes:
            key = (
                hole.diameter_mm,
                round(abs(hole.axis_direction.x), 3),
                round(abs(hole.axis_direction.y), 3),
                round(abs(hole.axis_direction.z), 3),
            )
            grouped[key].append(hole)

        patterns: List[HolePattern] = []
        pattern_idx = 1

        for group in grouped.values():
            if len(group) >= 1:
                first = group[0]
                patterns.append(
                    HolePattern(
                        pattern_id=f"PAT_{pattern_idx:02d}",
                        diameter_mm=first.diameter_mm,
                        hole_count=len(group),
                        axis_direction=first.axis_direction,
                        face_ids=[h.face_id for h in group],
                        locations=[h.location for h in group],
                    )
                )
                pattern_idx += 1

        return patterns


# Example Verification
if __name__ == "__main__":
    import json
    from draftgpt_core.ingestion.step_loader import STEPFileLoader

    # Replace with test STEP file path
    # loader = STEPFileLoader("sample.step")
    # shape = loader.load()
    # detector = FeatureDetector(shape, filename="sample.step")
    # summary = detector.analyze()
    # print(summary.model_dump_json(indent=2))
    pass