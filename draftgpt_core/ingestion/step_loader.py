import os
from pathlib import Path
from typing import Dict, Any, Union, Optional

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCP.TopoDS import TopoDS_Shape, TopoDS_Compound
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_SHELL


class STEPLoadError(Exception):
    """Custom exception raised when STEP file loading or parsing fails."""
    pass


class STEPFileLoader:
    """Handles STEP file ingestion, topology validation, and basic geometric metadata extraction."""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.shape: Optional[TopoDS_Shape] = None
        self._validate_file_path()

    def _validate_file_path(self) -> None:
        """Validates that the provided path exists and has a supported STEP extension."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"STEP file not found at: {self.file_path}")
        
        valid_extensions = {".step", ".stp", ".STEP", ".STP"}
        if self.file_path.suffix not in valid_extensions:
            raise ValueError(
                f"Invalid file extension '{self.file_path.suffix}'. Expected one of {valid_extensions}"
            )

    def load(self) -> TopoDS_Shape:
        """Parses the STEP file and transfers geometry into an OpenCascade TopoDS_Shape."""
        reader = STEPControl_Reader()
        status = reader.ReadFile(str(self.file_path.resolve()))

        if status != IFSelect_RetDone:
            raise STEPLoadError(
                f"Failed to parse STEP file: '{self.file_path.name}'. OpenCascade status code: {status}"
            )

        # Transfer root entities from STEP file into OpenCascade CAD shape
        reader.TransferRoots()
        self.shape = reader.Shape()

        if self.shape.IsNull():
            raise STEPLoadError(
                f"Failed to import geometry from '{self.file_path.name}'. Resulting shape is Null."
            )

        return self.shape

    def get_metadata(self) -> Dict[str, Any]:
        """Extracts high-level topological and geometric metadata from the loaded shape."""
        if self.shape is None:
            self.load()

        bounding_box = self._calculate_bounding_box()
        volume, surface_area = self._calculate_mass_properties()

        return {
            "filename": self.file_path.name,
            "filepath": str(self.file_path.resolve()),
            "file_size_bytes": self.file_path.stat().st_size,
            "topology_counts": {
                "solids": self._count_topology(TopAbs_SOLID),
                "shells": self._count_topology(TopAbs_SHELL),
                "faces": self._count_topology(TopAbs_FACE),
            },
            "bounding_box_mm": bounding_box,
            "dimensions_mm": {
                "dx": round(bounding_box["x_max"] - bounding_box["x_min"], 4),
                "dy": round(bounding_box["y_max"] - bounding_box["y_min"], 4),
                "dz": round(bounding_box["z_max"] - bounding_box["z_min"], 4),
            },
            "volume_mm3": round(volume, 4),
            "surface_area_mm2": round(surface_area, 4),
        }

    def _count_topology(self, shape_type) -> int:
        """Counts occurrence of a specific topological entity (e.g., FACE, SOLID)."""
        explorer = TopExp_Explorer(self.shape, shape_type)
        count = 0
        while explorer.More():
            count += 1
            explorer.Next()
        return count

    def _calculate_bounding_box(self) -> Dict[str, float]:
        """Calculates the axis-aligned bounding box (AABB) of the CAD model."""
        bbox = Bnd_Box()
        BRepBndLib.Add_s(self.shape, bbox)
        
        if bbox.IsVoid():
            raise STEPLoadError("Failed to calculate bounding box; geometry appears void.")

        x_min, y_min, z_min, x_max, y_max, z_max = bbox.Get()
        return {
            "x_min": round(x_min, 4),
            "y_min": round(y_min, 4),
            "z_min": round(z_min, 4),
            "x_max": round(x_max, 4),
            "y_max": round(y_max, 4),
            "z_max": round(z_max, 4),
        }

    def _calculate_mass_properties(self) -> tuple[float, float]:
        """Calculates exact volume (mm³) and surface area (mm²) using BRepGProp."""
        vol_props = GProp_GProps()
        surf_props = GProp_GProps()

        BRepGProp.VolumeProperties_s(self.shape, vol_props)
        BRepGProp.SurfaceProperties_s(self.shape, surf_props)

        return vol_props.Mass(), surf_props.Mass()


# Example Usage / Verification
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        try:
            loader = STEPFileLoader(test_file)
            shape = loader.load()
            metadata = loader.get_metadata()
            print("\nSuccessfully Loaded STEP File Metadata:")
            import json
            print(json.dumps(metadata, indent=2))
        except Exception as e:
            print(f"Error loading STEP file: {e}")
    else:
        print("Usage: python step_loader.py <path_to_step_file.step>")