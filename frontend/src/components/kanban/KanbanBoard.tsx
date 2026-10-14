import React from 'react';
import type { Job, JobStatus } from '../../types';
import { JobCard } from './JobCard';
import { Sparkles, CheckCircle, Send, ArchiveX } from 'lucide-react';

interface KanbanBoardProps {
  jobs: Job[];
  onSelectJob: (job: Job) => void;
  onStatusChange: (jobId: number, status: JobStatus) => void;
  onTailor: (jobId: number) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  jobs,
  onSelectJob,
  onStatusChange,
  onTailor,
}) => {
  const columns: Array<{ id: JobStatus; title: string; icon: any; color: string; bgBadge: string }> = [
    { id: 'NEW', title: 'New Opportunities', icon: Sparkles, color: 'text-blue-400', bgBadge: 'bg-blue-950 text-blue-400 border-blue-800' },
    { id: 'APPROVED', title: 'Approved to Apply', icon: CheckCircle, color: 'text-emerald-400', bgBadge: 'bg-emerald-950 text-emerald-400 border-emerald-800' },
    { id: 'APPLIED', title: 'Applied', icon: Send, color: 'text-purple-400', bgBadge: 'bg-purple-950 text-purple-400 border-purple-800' },
    { id: 'SKIPPED', title: 'Skipped', icon: ArchiveX, color: 'text-gray-400', bgBadge: 'bg-gray-800 text-gray-400 border-gray-700' },
  ];

  return (
    <div className="flex-1 overflow-x-auto p-6 flex gap-6 min-h-0 bg-[#0B0F19]">
      {columns.map((col) => {
        const colJobs = jobs.filter((j) => j.status === col.id);
        const Icon = col.icon;

        return (
          <div
            key={col.id}
            className="w-80 md:w-96 shrink-0 flex flex-col bg-gray-950/40 border border-gray-800/80 rounded-2xl overflow-hidden shadow-sm"
          >
            {/* Column Header */}
            <div className="p-4 border-b border-gray-800/80 flex items-center justify-between bg-gray-900/50">
              <div className="flex items-center space-x-2">
                <Icon className={`w-4 h-4 ${col.color}`} />
                <h3 className="font-bold text-sm text-white">{col.title}</h3>
              </div>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${col.bgBadge}`}>
                {colJobs.length}
              </span>
            </div>

            {/* Cards List */}
            <div className="p-3 overflow-y-auto flex-1 space-y-3">
              {colJobs.length === 0 ? (
                <div className="h-40 border border-dashed border-gray-800 rounded-xl flex items-center justify-center text-xs text-gray-500">
                  No jobs in {col.title.toLowerCase()}
                </div>
              ) : (
                colJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onSelect={onSelectJob}
                    onStatusChange={onStatusChange}
                    onTailor={onTailor}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
