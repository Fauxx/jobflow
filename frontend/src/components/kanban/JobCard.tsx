import React from 'react';
import type { Job, JobStatus } from '../../types';
import { Building2, MapPin, Sparkles, ExternalLink, ArrowRight, X } from 'lucide-react';

interface JobCardProps {
  job: Job;
  onSelect: (job: Job) => void;
  onStatusChange: (jobId: number, status: JobStatus) => void;
  onTailor: (jobId: number) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onSelect,
  onStatusChange,
  onTailor,
}) => {
  const getScoreColor = (score?: number) => {
    if (!score) return 'bg-gray-800 text-gray-400 border-gray-700';
    if (score >= 80) return 'bg-emerald-950/80 text-emerald-400 border-emerald-700/50';
    if (score >= 60) return 'bg-blue-950/80 text-blue-400 border-blue-700/50';
    return 'bg-amber-950/80 text-amber-400 border-amber-700/50';
  };

  return (
    <div
      onClick={() => onSelect(job)}
      className="bg-gray-900 border border-gray-800 hover:border-gray-700 p-4 rounded-xl shadow-sm hover:shadow-md transition cursor-pointer group flex flex-col justify-between relative"
    >
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-gray-400 flex items-center">
              <Building2 className="w-3.5 h-3.5 mr-1 text-gray-500" />
              {job.company}
            </span>
          </div>

          {job.fit_score !== undefined && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-bold border flex items-center gap-1 ${getScoreColor(
                job.fit_score
              )}`}
            >
              <Sparkles className="w-3 h-3" />
              {job.fit_score}% Fit
            </span>
          )}
        </div>

        <h3 className="font-bold text-white text-base leading-snug group-hover:text-blue-400 transition mb-2">
          {job.title}
        </h3>

        {job.location && (
          <p className="text-xs text-gray-400 flex items-center mb-3">
            <MapPin className="w-3 h-3 mr-1 text-gray-500 shrink-0" />
            <span className="truncate">{job.location}</span>
          </p>
        )}

        {job.fit_reason && (
          <p className="text-xs text-gray-400 line-clamp-2 bg-gray-950/50 p-2 rounded-lg border border-gray-800/80 mb-3">
            {job.fit_reason}
          </p>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-800/80 mt-2">
        <div className="flex items-center space-x-1.5">
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition"
              title="Open Original Job Link"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {job.status !== 'SKIPPED' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onStatusChange(job.id, 'SKIPPED');
              }}
              className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition"
              title="Skip Job"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onTailor(job.id);
            }}
            className="text-xs font-bold px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition shadow-sm flex items-center gap-1"
          >
            Tailor AI
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};
