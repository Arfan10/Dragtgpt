from typing import Dict, Any, List
from draftgpt_core.schemas.features import ExtractedFeaturesSummary
from draftgpt_core.schemas.views import (
    ViewType,
    ViewLayout,
    Projection2D,
    BoundingDimension2D,
    HoleAnnotation2D,
    DrawingSheetLayout,
)


class ViewPlanner:
    """Calculates primary orientation, views, scaling, and dimension placement rules."""

    def __init__(self, feature_summary: ExtractedFeaturesSummary, metadata: Dict[str, Any]):
        self.summary = feature_summary
        self.metadata = metadata
        self.dims = metadata["dimensions_mm"]

    def plan_drawing_sheet(self, sheet_size: str = "A3") -> DrawingSheetLayout:
        dx, dy, dz = self.dims["dx"], self.dims["dy"], self.dims["dz"]

        # View 1: Front (DX x DY)
        front_view = self._build_view(
            view_type=ViewType.FRONT,
            width=dx,
            height=dy,
            dim_labels=("WIDTH", "HEIGHT"),
            dim_values=(dx, dy),
        )

        # View 2: Top (DX x DZ)
        top_view = self._build_view(
            view_type=ViewType.TOP,
            width=dx,
            height=dz,
            dim_labels=("WIDTH", "DEPTH"),
            dim_values=(dx, dz),
        )

        # View 3: Right (DZ x DY)
        right_view = self._build_view(
            view_type=ViewType.RIGHT,
            width=dz,
            height=dy,
            dim_labels=("DEPTH", "HEIGHT"),
            dim_values=(dz, dy),
        )

        # View 4: Isometric
        iso_view = ViewLayout(
            view_type=ViewType.ISOMETRIC,
            scale=1.0,
            center_offset=Projection2D(x=300.0, y=200.0),
            bounding_box_2d=(dx, dy),
            dimensions=[],
            hole_annotations=[],
        )

        # Add Hole Callouts to Front View
        front_view.hole_annotations = self._generate_hole_callouts()

        return DrawingSheetLayout(
            part_name=self.summary.filename,
            sheet_size=sheet_size,
            views=[front_view, top_view, right_view, iso_view],
        )

    def _build_view(
        self,
        view_type: ViewType,
        width: float,
        height: float,
        dim_labels: tuple[str, str],
        dim_values: tuple[float, float],
    ) -> ViewLayout:
        d1_label, d2_label = dim_labels
        v1_val, v2_val = dim_values

        dimensions = [
            BoundingDimension2D(
                dimension_type=d1_label,
                value_mm=round(v1_val, 2),
                start_point=Projection2D(x=0.0, y=0.0),
                end_point=Projection2D(x=width, y=0.0),
                label=f"{d1_label}: {v1_val:.2f} mm",
            ),
            BoundingDimension2D(
                dimension_type=d2_label,
                value_mm=round(v2_val, 2),
                start_point=Projection2D(x=0.0, y=0.0),
                end_point=Projection2D(x=0.0, y=height),
                label=f"{d2_label}: {v2_val:.2f} mm",
            ),
        ]

        return ViewLayout(
            view_type=view_type,
            scale=1.0,
            center_offset=Projection2D(x=100.0, y=100.0),
            bounding_box_2d=(round(width, 2), round(height, 2)),
            dimensions=dimensions,
            hole_annotations=[],
        )

    def _generate_hole_callouts(self) -> List[HoleAnnotation2D]:
            callouts = []
            for pattern in self.summary.hole_patterns:
                prefix = f"{pattern.hole_count}x " if pattern.hole_count > 1 else ""
                callout_str = f"{prefix}Ø{pattern.diameter_mm:.2f} THRU"
                
                if pattern.locations and len(pattern.locations) > 0:
                    loc = pattern.locations[0]
                    proj_loc = Projection2D(x=float(loc.x), y=float(loc.y))
                else:
                    proj_loc = Projection2D(x=0.0, y=0.0)

                callouts.append(
                    HoleAnnotation2D(
                        pattern_id=pattern.pattern_id,
                        callout_text=callout_str,
                        center_location=proj_loc,
                    )
                )
            return callouts


# Verification / Test Run
if __name__ == "__main__":
    import json
    # Dummy verification stub
    pass