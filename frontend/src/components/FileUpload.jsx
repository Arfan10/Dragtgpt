import React, { useState } from 'react';
import { Upload, FileCode, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    if (!file.name.toLowerCase().endsWith('.step') && !file.name.toLowerCase().endsWith('.stp')) {
      setError('Please upload a valid .step or .stp CAD file.');
      return;
    }

    setError(null);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/drawings/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onUploadSuccess(response.data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload CAD model.');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <FileCode className="w-5 h-5 text-indigo-600" />
        Upload 3D STEP Model
      </h2>

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer ${
          isDragging ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-300 hover:border-indigo-400'
        }`}
      >
        <input
          type="file"
          accept=".step,.stp"
          onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
          className="hidden"
          id="cad-file-input"
        />
        <label htmlFor="cad-file-input" className="cursor-pointer flex flex-col items-center">
          <Upload className="w-10 h-10 text-slate-400 mb-2" />
          <p className="text-sm font-medium text-slate-700">
            {loading ? 'Processing STEP model...' : 'Drag & Drop your STEP file here, or browse'}
          </p>
          <span className="text-xs text-slate-400 mt-1">Supports .step and .stp files</span>
        </label>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}