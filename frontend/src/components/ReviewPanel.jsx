import React, { useState } from 'react';
import { AlertTriangle, Check, X, Download } from 'lucide-react';
import axios from 'axios';

export default function ReviewPanel({ job, onReviewUpdated }) {
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!job) return null;

  const handleReview = async (approved) => {
    setSubmitting(true);
    try {
      await axios.post(`http://localhost:8000/api/v1/drawings/jobs/${job.job_id}/review`, {
        reviewer_notes: notes,
        approved: approved,
      });
      onReviewUpdated();
    } catch (err) {
      alert('Failed to submit review.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-orange-500" />
        Engineer Review & Signoff
      </h3>

      {/* Flagged Items Checklist */}
      {job.flagged_items && job.flagged_items.length > 0 ? (
        <div className="mb-6 space-y-2">
          {job.flagged_items.map((flag, idx) => (
            <div key={idx} className="p-3 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-800">
              <span className="font-semibold">{flag.code}:</span> {flag.message}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500 mb-4">No automated flags raised. Drawing passes automated checks.</p>
      )}

      {/* Reviewer Notes */}
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Add engineering review notes or corrections..."
        className="w-full p-3 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none mb-4"
        rows={3}
      />

      {/* Actions */}
      <div className="flex items-center justify-between">
        {job.dxf_path && (
          <a
            href={`http://localhost:8000/${job.dxf_path}`}
            download
            className="flex items-center gap-2 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            <Download className="w-4 h-4" /> Download DXF Drawing
          </a>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => handleReview(false)}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            <X className="w-4 h-4" /> Reject Drawing
          </button>
          <button
            onClick={() => handleReview(true)}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50"
          >
            <Check className="w-4 h-4" /> Approve & Release
          </button>
        </div>
      </div>
    </div>
  );
}