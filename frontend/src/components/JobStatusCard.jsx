import React from 'react';
import { Clock, CheckCircle2, AlertTriangle, XCircle, FileCheck } from 'lucide-react';

export default function JobStatusCard({ job }) {
  if (!job) return null;

  const statusConfig = {
    PENDING: { bg: 'bg-amber-50', text: 'text-amber-700', icon: Clock, label: 'Queued' },
    PROCESSING: { bg: 'bg-blue-50', text: 'text-blue-700', icon: Clock, label: 'Processing Geometry...' },
    NEEDS_REVIEW: { bg: 'bg-orange-50', text: 'text-orange-700', icon: AlertTriangle, label: 'Needs Engineer Review' },
    APPROVED: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: CheckCircle2, label: 'Approved & Released' },
    COMPLETED: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: FileCheck, label: 'Drawing Generated' },
    FAILED: { bg: 'bg-red-50', text: 'text-red-700', icon: XCircle, label: 'Processing Failed' },
  };

  const current = statusConfig[job.status] || statusConfig.PENDING;
  const Icon = current.icon;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-mono text-slate-400 uppercase">JOB ID: {job.job_id}</span>
          <h3 className="text-xl font-bold text-slate-800">{job.filename}</h3>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${current.bg} ${current.text} font-medium text-sm`}>
          <Icon className="w-4 h-4" />
          {current.label}
        </div>
      </div>
    </div>
  );
}