import React, { useState, useMemo } from 'react';
import type { Job, JobStatus } from '../../types';
import {
  Star,
  Search,
  ExternalLink,
  ChevronRight,
  Building,
  MapPin,
  Calendar,
  Inbox,
  CheckCircle2,
  Layers,
} from 'lucide-react';

interface JobListViewProps {
  jobs: Job[];
  activeTab: 'all' | 'priority' | 'saved' | 'applied';
  onTabSelect: (tab: 'all' | 'priority' | 'saved' | 'applied') => void;
  onSelectJob: (job: Job) => void;
  onTogglePriority: (jobId: number) => Promise<void>;
  onStatusChange: (jobId: number, status: JobStatus) => Promise<void>;
  onOpenResumeStudio?: (jobId: number) => void;
}

export const JobListView: React.FC<JobListViewProps> = ({
  jobs,
  activeTab,
  onTabSelect,
  onSelectJob,
  onTogglePriority,
  onStatusChange,
  onOpenResumeStudio,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Tab counts
  const counts = useMemo(() => {
    return {
      all: jobs.length,
      priority: jobs.filter((j) => j.is_priority).length,
      saved: jobs.filter((j) => j.status === 'SAVED' || j.status === 'NEW' || j.status === 'APPROVED').length,
      applied: jobs.filter((j) => j.status === 'APPLIED').length,
    };
  }, [jobs]);

  // Filtered jobs based on tab and search
  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      if (activeTab === 'priority' && !job.is_priority) return false;
      if (activeTab === 'saved') {
        const isSaved = job.status === 'SAVED' || job.status === 'NEW' || job.status === 'APPROVED';
        if (!isSaved) return false;
      }
      if (activeTab === 'applied' && job.status !== 'APPLIED') return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const titleMatch = job.title?.toLowerCase().includes(q);
        const compMatch = job.company?.toLowerCase().includes(q);
        const locMatch = job.location?.toLowerCase().includes(q);
        const descMatch = job.cleaned_description?.toLowerCase().includes(q);
        return titleMatch || compMatch || locMatch || descMatch;
      }

      return true;
    });
  }, [jobs, activeTab, searchQuery]);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-[#080c14] overflow-hidden">
      {/* Top Filter and Search Control Bar */}
      <div className="px-6 py-3.5 border-b border-white/[0.08] bg-[#0c101d] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shrink-0">
        
        {/* Segmented Capsule Tabs */}
        <div className="flex items-center space-x-1.5 p-1 bg-[#121829] border border-white/[0.08] rounded-2xl shadow-inner">
          <button
            onClick={() => onTabSelect('all')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'all'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>All Leads</span>
            <span className={`px-1.5 py-0.2 rounded-md text-[10px] ${activeTab === 'all' ? 'bg-white/20' : 'bg-slate-800 text-slate-400'}`}>
              {counts.all}
            </span>
          </button>

          <button
            onClick={() => onTabSelect('priority')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition ${
              activeTab === 'priority'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-[0_0_12px_rgba(245,158,11,0.15)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span>Priority</span>
            <span className="px-1.5 py-0.2 rounded-md bg-amber-400/20 text-amber-300 text-[10px]">
              {counts.priority}
            </span>
          </button>

          <button
            onClick={() => onTabSelect('saved')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'saved'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.15)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>Saved</span>
            <span className="px-1.5 py-0.2 rounded-md bg-emerald-400/20 text-emerald-300 text-[10px]">
              {counts.saved}
            </span>
          </button>

          <button
            onClick={() => onTabSelect('applied')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 ${
              activeTab === 'applied'
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-[0_0_12px_rgba(99,102,241,0.15)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>Applied</span>
            <span className="px-1.5 py-0.2 rounded-md bg-indigo-400/20 text-indigo-300 text-[10px]">
              {counts.applied}
            </span>
          </button>
        </div>

        {/* Search Input Bar */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search role, company, or tech keyword..."
            className="w-full bg-[#121829] border border-white/[0.08] focus:border-blue-500/80 rounded-2xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none transition shadow-inner font-sans"
          />
        </div>
      </div>

      {/* High-Density Linear Job Stream */}
      <div className="flex-1 overflow-y-auto divide-y divide-white/[0.04]">
        {filteredJobs.length === 0 ? (
          <div className="py-24 text-center flex flex-col items-center justify-center text-slate-500 space-y-3">
            <div className="p-4 rounded-3xl bg-slate-900/60 border border-white/[0.06]">
              <Inbox className="w-10 h-10 text-slate-600 stroke-[1.5]" />
            </div>
            <p className="text-sm font-bold text-slate-300">No matching opportunities found</p>
            <p className="text-xs text-slate-500 max-w-sm">
              Try adjusting your filter or paste a job link in the top bar to ingest a new lead.
            </p>
          </div>
        ) : (
          filteredJobs.map((job) => (
            <div
              key={job.id}
              onClick={() => onSelectJob(job)}
              className="px-6 py-4 hover:bg-[#111728]/70 cursor-pointer transition-all duration-150 flex items-center justify-between gap-4 group"
            >
              {/* Left Details: Priority Star + Role + Company + Platform */}
              <div className="flex items-start space-x-4 min-w-0 flex-1">
                {/* Priority Star Toggle with halo */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onTogglePriority(job.id);
                  }}
                  className={`p-2 rounded-xl transition-all duration-150 mt-0.5 shrink-0 ${
                    job.is_priority
                      ? 'text-amber-400 bg-amber-400/10 border border-amber-400/30 shadow-[0_0_12px_rgba(251,191,36,0.2)]'
                      : 'text-slate-600 hover:text-slate-300 hover:bg-slate-800 border border-transparent'
                  }`}
                  title={job.is_priority ? 'Starred as Priority' : 'Mark as Priority'}
                >
                  <Star className={`w-4 h-4 ${job.is_priority ? 'fill-amber-400' : ''}`} />
                </button>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center space-x-2.5">
                    <h3 className="text-sm font-bold text-slate-100 group-hover:text-blue-400 transition-colors truncate">
                      {job.title}
                    </h3>

                    {/* Source platform tag */}
                    {job.source_platform && (
                      <span className="shrink-0 px-2 py-0.5 rounded-md text-[10px] font-mono uppercase tracking-wider bg-white/[0.06] text-slate-300 border border-white/[0.08]">
                        {job.source_platform}
                      </span>
                    )}

                    {/* Has cover letter badge */}
                    {job.cover_letter && (
                      <span className="shrink-0 px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center shadow-[0_0_8px_rgba(16,185,129,0.15)]">
                        <CheckCircle2 className="w-2.5 h-2.5 mr-1" /> CL Saved
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1 font-medium">
                    <span className="flex items-center text-slate-300 font-semibold">
                      <Building className="w-3.5 h-3.5 mr-1 text-slate-500" />
                      {job.company}
                    </span>
                    <span>•</span>
                    <span className="flex items-center">
                      <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                      {job.location || 'Remote'}
                    </span>
                    {job.created_at && (
                      <>
                        <span>•</span>
                        <span className="flex items-center text-slate-500">
                          <Calendar className="w-3.5 h-3.5 mr-1" />
                          {job.created_at.slice(0, 10)}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Controls: Status Selector & Direct Action Buttons */}
              <div
                className="flex items-center space-x-3 shrink-0"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Inline Status Dropdown with Halo styling */}
                <select
                  value={job.status}
                  onChange={(e) => onStatusChange(job.id, e.target.value as JobStatus)}
                  className={`text-xs font-bold rounded-xl px-3 py-1.5 border focus:outline-none transition shadow-sm ${
                    job.status === 'APPLIED'
                      ? 'bg-indigo-500/15 border-indigo-500/40 text-indigo-300 shadow-[0_0_12px_rgba(99,102,241,0.15)]'
                      : job.status === 'SAVED' || job.status === 'APPROVED'
                      ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 shadow-[0_0_12px_rgba(16,185,129,0.15)]'
                      : 'bg-slate-800/80 border-slate-700 text-slate-300'
                  }`}
                >
                  <option value="SAVED">Saved</option>
                  <option value="APPLIED">Applied</option>
                  <option value="ARCHIVED">Archived</option>
                  <option value="NEW">New</option>
                </select>

                {/* Direct "Tailor Resume" button right on row */}
                {onOpenResumeStudio && (
                  <button
                    type="button"
                    onClick={() => onOpenResumeStudio(job.id)}
                    className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-blue-600 hover:text-white border border-white/[0.08] hover:border-blue-500 text-slate-300 text-xs font-bold transition shadow-sm group/btn"
                    title="Open Resume Tailor Co-Pilot"
                  >
                    <Layers className="w-3.5 h-3.5 text-blue-400 group-hover/btn:text-white" />
                    <span>Tailor</span>
                  </button>
                )}

                {/* External URL Link */}
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-xl text-slate-500 hover:text-blue-400 hover:bg-slate-800/80 transition border border-transparent hover:border-white/10"
                    title="Open original job posting"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}

                {/* View Details Chevron */}
                <button
                  type="button"
                  onClick={() => onSelectJob(job)}
                  className="p-1 rounded-lg text-slate-500 group-hover:text-white transition"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
