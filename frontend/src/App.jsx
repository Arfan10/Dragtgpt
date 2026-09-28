import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import JobStatusCard from './components/JobStatusCard';
import MetadataViewer from './components/MetadataViewer';
import ReviewPanel from './components/ReviewPanel';

export default function App() {
  const [activeJobId, setActiveJobId] = useState(null);
  const [jobData, setJobData] = useState(null);

  const fetchJobStatus = async (jobId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/drawings/jobs/${jobId}`);
      setJobData(response.data);
    } catch (err) {
      console.error('Error fetching job status:', err);
    }
  };

  useEffect(() => {
    if (!activeJobId) return;

    fetchJobStatus(activeJobId);
    const interval = setInterval(() => {
      fetchJobStatus(activeJobId);
    }, 2000);

    return () => clearInterval(interval);
  }, [activeJobId]);

  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-900 pb-12">
      <header className="bg-slate-900 text-white border-b border-slate-800 py-4 px-8 shadow-md">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-indigo-400 font-bold text-2xl tracking-tight">DraftGPT</span>
            <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded font-mono">
              v1.0 MVP
            </span>
          </div>
          <span className="text-xs text-slate-400">AI-Powered Engineering Detailing Platform</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 mt-8 space-y-6">
        <FileUpload onUploadSuccess={(jobId) => setActiveJobId(jobId)} />

        {jobData && (
          <>
            <JobStatusCard job={jobData} />
            <MetadataViewer metadata={jobData.metadata} />
            <ReviewPanel job={jobData} onReviewUpdated={() => fetchJobStatus(activeJobId)} />
          </>
        )}
      </main>
    </div>
  );
}