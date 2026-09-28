import ezdxf
from ezdxf.enums import TextEntityAlignment
from pathlib import Path
from typing import Union

from draftgpt_core.schemas.views import DrawingSheetLayout, ViewType


class DXFDrawingGenerator:
    """Renders DrawingSheetLayout into a standardized CAD drawing DXF file."""

    def __init__(self, layout: DrawingSheetLayout):
        self.layout = layout
        self.doc = ezdxf.new(setup=True)
        self.msp = self.doc.modelspace()
        self._setup_layers()

    def _setup_layers(self):
        """Creates CAD standard layers with specific colors and line types."""
        layers = [
            ("BORDER", 7),          # White/Black thick line
            ("TITLE_BLOCK", 7),     # White/Black text/lines
            ("VISIBLE_GEOMETRY", 3),# Green outline
            ("CENTERLINES", 1),     # Red centerline
            ("DIMENSIONS", 5),      # Blue dimension lines
            ("ANNOTATIONS", 2),     # Yellow callout text
        ]
        for name, color in layers:
            if name not in self.doc.layers:
                layer = self.doc.layers.add(name)
                layer.color = color

    def build_dxf(self, output_path: Union[str, Path]) -> Path:
        """Generates title block, views, dimensions, and saves DXF."""
        output_path = Path(output_path)
        
        # 1. Draw Title Block & Border
        self._draw_border_and_title_block()

        # 2. Render Views
        for view in self.layout.views:
            self._render_view(view)

        # 3. Save Output File
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.saveas(str(output_path))
        return output_path

    def _draw_border_and_title_block(self):
        """Draws A3 border (420mm x 297mm) and Standard Title Block."""
        # Sheet Outer Border (A3: 420 x 297 mm)
        margin = 10.0
        x_max, y_max = 420.0 - margin, 297.0 - margin
        
        self.msp.add_lwpolyline(
            [(margin, margin), (x_max, margin), (x_max, y_max), (margin, y_max)],
            close=True,
            dxfattribs={"layer": "BORDER", "lineweight": 50}
        )

        # Title Block Box (Bottom Right Corner: 180mm x 50mm)
        tb_w, tb_h = 180.0, 50.0
        tb_x0, tb_y0 = x_max - tb_w, margin
        
        self.msp.add_lwpolyline(
            [(tb_x0, tb_y0), (x_max, tb_y0), (x_max, tb_y0 + tb_h), (tb_x0, tb_y0 + tb_h)],
            close=True,
            dxfattribs={"layer": "TITLE_BLOCK"}
        )

        # Title Block Field Lines
        self.msp.add_line((tb_x0, tb_y0 + 25), (x_max, tb_y0 + 25), dxfattribs={"layer": "TITLE_BLOCK"})
        
        # Metadata Text Entries
        self.msp.add_text(
            f"PART: {self.layout.part_name}",
            dxfattribs={"layer": "TITLE_BLOCK", "height": 4.0}
        ).set_placement((tb_x0 + 5, tb_y0 + 35), align=TextEntityAlignment.LEFT)

        self.msp.add_text(
            f"SHEET: {self.layout.sheet_size} | SCALE: 1:1",
            dxfattribs={"layer": "TITLE_BLOCK", "height": 3.0}
        ).set_placement((tb_x0 + 5, tb_y0 + 10), align=TextEntityAlignment.LEFT)

        self.msp.add_text(
            "DRAFTGPT AUTOMATED DRAWING",
            dxfattribs={"layer": "TITLE_BLOCK", "height": 3.0}
        ).set_placement((tb_x0 + 100, tb_y0 + 10), align=TextEntityAlignment.LEFT)

    def _render_view(self, view):
        """Renders 2D view geometry, dimensions, and callout annotations."""
        ox, oy = view.center_offset.x, view.center_offset.y
        w, h = view.bounding_box_2d

        # Render View Label
        self.msp.add_text(
            f"VIEW: {view.view_type.value}",
            dxfattribs={"layer": "ANNOTATIONS", "height": 3.5}
        ).set_placement((ox, oy + h + 8.0), align=TextEntityAlignment.LEFT)

        if view.view_type == ViewType.ISOMETRIC:
            # Isometric Box Representative Placeholder
            self.msp.add_lwpolyline(
                [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)],
                close=True,
                dxfattribs={"layer": "VISIBLE_GEOMETRY"}
            )
            return

        # Draw View Bounding Frame
        self.msp.add_lwpolyline(
            [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)],
            close=True,
            dxfattribs={"layer": "VISIBLE_GEOMETRY"}
        )

        # Add Dimensions
        for dim in view.dimensions:
            if dim.dimension_type in ("WIDTH", "DEPTH"):
                # Horizontal Dimension Line below view
                y_pos = oy - 12.0
                self.msp.add_line((ox, y_pos), (ox + w, y_pos), dxfattribs={"layer": "DIMENSIONS"})
                self.msp.add_line((ox, oy), (ox, y_pos - 3), dxfattribs={"layer": "DIMENSIONS"})
                self.msp.add_line((ox + w, oy), (ox + w, y_pos - 3), dxfattribs={"layer": "DIMENSIONS"})
                
                self.msp.add_text(
                    f"{dim.value_mm:.2f} mm",
                    dxfattribs={"layer": "DIMENSIONS", "height": 3.0}
                ).set_placement((ox + w / 2, y_pos + 2), align=TextEntityAlignment.MIDDLE_CENTER)

            elif dim.dimension_type == "HEIGHT":
                # Vertical Dimension Line left of view
                x_pos = ox - 12.0
                self.msp.add_line((x_pos, oy), (x_pos, oy + h), dxfattribs={"layer": "DIMENSIONS"})
                self.msp.add_line((ox, oy), (x_pos - 3, oy), dxfattribs={"layer": "DIMENSIONS"})
                self.msp.add_line((ox, oy + h), (x_pos - 3, oy + h), dxfattribs={"layer": "DIMENSIONS"})
                
                self.msp.add_text(
                    f"{dim.value_mm:.2f} mm",
                    dxfattribs={"layer": "DIMENSIONS", "height": 3.0}
                ).set_placement((x_pos - 4, oy + h / 2), align=TextEntityAlignment.MIDDLE_CENTER)

        # Add Hole Callout Annotations
        for callout in view.hole_annotations:
            cx, cy = ox + callout.center_location.x, oy + callout.center_location.y
            
            # Draw Hole Centerline Cross
            r = 5.0
            self.msp.add_line((cx - r, cy), (cx + r, cy), dxfattribs={"layer": "CENTERLINES"})
            self.msp.add_line((cx, cy - r), (cx, cy + r), dxfattribs={"layer": "CENTERLINES"})

            # Hole Callout Annotation Leader Line
            self.msp.add_line((cx, cy), (cx + 15, cy + 15), dxfattribs={"layer": "ANNOTATIONS"})
            self.msp.add_line((cx + 15, cy + 15), (cx + 35, cy + 15), dxfattribs={"layer": "ANNOTATIONS"})
            self.msp.add_text(
                callout.callout_text,
                dxfattribs={"layer": "ANNOTATIONS", "height": 3.0}
            ).set_placement((cx + 16, cy + 17), align=TextEntityAlignment.LEFT)