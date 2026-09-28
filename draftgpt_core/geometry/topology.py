from typing import List, Tuple
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_Orientation
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pln, gp_Cylinder

from draftgpt_core.schemas.features import (
    PlanarFeature,
    CylindricalFeature,
    FeatureType,
    Vector3D,
)


class TopologyExplorer:
    """Extracts geometric primitives and mathematical properties from TopoDS_Shape safely."""

    def __init__(self, shape):
        self.shape = shape

    def extract_primitives(self) -> Tuple[List[PlanarFeature], List[CylindricalFeature], int]:
        explorer = TopExp_Explorer(self.shape, TopAbs_FACE)
        planes: List[PlanarFeature] = []
        cylinders: List[CylindricalFeature] = []
        face_id = 0

        while explorer.More():
            face = explorer.Current()
            try:
                surf_adaptor = BRepAdaptor_Surface(face)
                surf_type = surf_adaptor.GetType()

                if surf_type == GeomAbs_Plane:
                    planes.append(self._process_plane(face_id, surf_adaptor, face))
                elif surf_type == GeomAbs_Cylinder:
                    cylinders.append(self._process_cylinder(face_id, surf_adaptor, face))
            except Exception as e:
                # Safely ignore complex/freeform surfaces (BSplines, Toroids, Spheres)
                pass

            face_id += 1
            explorer.Next()

        return planes, cylinders, face_id

    def _get_face_area(self, face) -> float:
        try:
            props = GProp_GProps()
            BRepGProp.SurfaceProperties_s(face, props)
            return round(float(props.Mass()), 4)
        except Exception:
            return 0.0

    def _process_plane(self, face_id: int, adaptor: BRepAdaptor_Surface, face) -> PlanarFeature:
        plane: gp_Pln = adaptor.Plane()
        loc = plane.Location()
        norm = plane.Axis().Direction()
        
        orientation_factor = -1.0 if face.Orientation() == TopAbs_Orientation.TopAbs_REVERSED else 1.0

        return PlanarFeature(
            face_id=face_id,
            location=Vector3D(
                x=round(float(loc.X()), 4),
                y=round(float(loc.Y()), 4),
                z=round(float(loc.Z()), 4)
            ),
            normal=Vector3D(
                x=round(float(norm.X()) * orientation_factor, 4),
                y=round(float(norm.Y()) * orientation_factor, 4),
                z=round(float(norm.Z()) * orientation_factor, 4)
            ),
            area_mm2=self._get_face_area(face),
        )

    def _process_cylinder(self, face_id: int, adaptor: BRepAdaptor_Surface, face) -> CylindricalFeature:
        cylinder: gp_Cylinder = adaptor.Cylinder()
        radius = round(float(cylinder.Radius()), 4)
        loc = cylinder.Location()
        axis = cylinder.Axis().Direction()

        is_hole = face.Orientation() == TopAbs_Orientation.TopAbs_REVERSED
        feature_type = FeatureType.CYLINDER_HOLE if is_hole else FeatureType.CYLINDER_BOSS

        return CylindricalFeature(
            face_id=face_id,
            feature_type=feature_type,
            radius_mm=radius,
            diameter_mm=round(radius * 2.0, 4),
            location=Vector3D(
                x=round(float(loc.X()), 4),
                y=round(float(loc.Y()), 4),
                z=round(float(loc.Z()), 4)
            ),
            axis_direction=Vector3D(
                x=round(float(axis.X()), 4),
                y=round(float(axis.Y()), 4),
                z=round(float(axis.Z()), 4)
            ),
        )