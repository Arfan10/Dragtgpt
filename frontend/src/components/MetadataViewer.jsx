import React from 'react';
import { Box } from 'lucide-react';

export default function MetadataViewer({ metadata }) {
  if (!metadata) return null;

  const dims = metadata.dimensions_mm || {};
  const counts = metadata.topology_counts || {};

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <Box className="w-5 h-5 text-indigo-600" />
        Extracted CAD Geometry
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Dimensions */}
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
          <span className="text-xs font-medium text-slate-500 uppercase">Bounding Box (mm)</span>
          <p className="text-lg font-bold text-slate-800 mt-1">
            {dims.dx} × {dims.dy} × {dims.dz}
          </p>
        </div>

        {/* Mass Properties */}
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
          <span className="text-xs font-medium text-slate-500 uppercase">Volume & Surface Area</span>
          <p className="text-sm font-semibold text-slate-800 mt-1">
            Vol: {metadata.volume_mm3?.toLocaleString()} mm³
          </p>
          <p className="text-xs text-slate-500">
            Area: {metadata.surface_area_mm2?.toLocaleString()} mm²
          </p>
        </div>

        {/* Topology Counts */}
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
          <span className="text-xs font-medium text-slate-500 uppercase">Topology Entities</span>
          <p className="text-sm font-semibold text-slate-800 mt-1">
            Solids: {counts.solids} | Shells: {counts.shells}
          </p>
          <p className="text-xs text-slate-500">Total Faces: {counts.faces}</p>
        </div>
      </div>
    </div>
  );
}