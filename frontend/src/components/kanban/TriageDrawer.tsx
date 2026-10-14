import React from 'react';
import type { Job, JobStatus } from '../../types';
import { X, Building2, MapPin, Sparkles, ExternalLink, ArrowRight } from 'lucide-react';

interface TriageDrawerProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChange: (jobId: number, status: JobStatus) => void;
  onTailor: (jobId: number) => void;
}

export const TriageDrawer: React.FC<TriageDrawerProps> = ({
  job,
  isOpen,
  onClose,
  onStatusChange,
  onTailor,
}) => {
  if (!isOpen || !job) return null;

  return (
    <aside className="w-full md:w-[480px] bg-gray-900 border-l border-gray-800 flex flex-col h-full shadow-2xl z-30 transition-all duration-300 ease-in-out shrink-0">
      {/* Header */}
      <div className="p-6 border-b border-gray-800 flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold text-gray-400 flex items-center mb-1">
            <Building2 className="w-3.5 h-3.5 mr-1 text-gray-500" />
            {job.company}
          </span>
          <h2 className="text-xl font-bold text-white leading-tight">{job.title}</h2>
          {job.location && (
            <p className="text-xs text-gray-400 flex items-center mt-2">
              <MapPin className="w-3 h-3 mr-1 text-gray-500" />
              {job.location}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Action Bar */}
      <div className="px-6 py-4 bg-gray-950/60 border-b border-gray-800 flex items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          {(['NEW', 'APPROVED', 'APPLIED', 'SKIPPED'] as JobStatus[]).map((st) => (
            <button
              key={st}
              onClick={() => onStatusChange(job.id, st)}
              className={`text-xs px-2.5 py-1 rounded-md font-bold transition ${
                job.status === st
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
        <button
          onClick={() => onTailor(job.id)}
          className="text-xs font-bold px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-1 shadow-sm"
        >
          Open Builder
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Body / Description */}
      <div className="p-6 overflow-y-auto flex-1 space-y-6">
        {job.fit_score !== undefined && (
          <div className="bg-blue-950/30 border border-blue-900/50 p-4 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold text-blue-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                AI Fit Score
              </span>
              <span className="text-lg font-black text-white">{job.fit_score}%</span>
            </div>
            {job.fit_reason && <p className="text-xs text-gray-300">{job.fit_reason}</p>}
          </div>
        )}

        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Job Description
          </h4>
          <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap font-sans bg-gray-950/40 p-4 rounded-xl border border-gray-800/80">
            {job.cleaned_description || job.raw_description || 'No description available.'}
          </div>
        </div>

        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center gap-2 w-full py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl text-xs font-bold transition"
          >
            <ExternalLink className="w-4 h-4" />
            View Original Posting
          </a>
        )}
      </div>
    </aside>
  );
};
