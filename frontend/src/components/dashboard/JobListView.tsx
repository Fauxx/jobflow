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
} from 'lucide-react';

interface JobListViewProps {
  jobs: Job[];
  activeTab: 'all' | 'priority' | 'saved' | 'applied';
  onTabSelect: (tab: 'all' | 'priority' | 'saved' | 'applied') => void;
  onSelectJob: (job: Job) => void;
  onTogglePriority: (jobId: number) => Promise<void>;
  onStatusChange: (jobId: number, status: JobStatus) => Promise<void>;
}

export const JobListView: React.FC<JobListViewProps> = ({
  jobs,
  activeTab,
  onTabSelect,
  onSelectJob,
  onTogglePriority,
  onStatusChange,
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
      // Tab filter
      if (activeTab === 'priority' && !job.is_priority) return false;
      if (activeTab === 'saved') {
        const isSaved = job.status === 'SAVED' || job.status === 'NEW' || job.status === 'APPROVED';
        if (!isSaved) return false;
      }
      if (activeTab === 'applied' && job.status !== 'APPLIED') return false;

      // Search query filter
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
    <div className="flex-1 flex flex-col min-h-0 bg-[#0B0F19] overflow-hidden">
      {/* Top Filter and Search Bar */}
      <div className="px-6 py-3.5 border-b border-neutral-800 bg-[#0e1320] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        {/* Segmented Filter Tabs */}
        <div className="flex items-center space-x-1.5 p-1 bg-[#141b2d] border border-neutral-800 rounded-xl">
          <button
            onClick={() => onTabSelect('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'all'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            All Jobs ({counts.all})
          </button>

          <button
            onClick={() => onTabSelect('priority')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'priority'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span>Priority ({counts.priority})</span>
          </button>

          <button
            onClick={() => onTabSelect('saved')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'saved'
                ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Saved ({counts.saved})
          </button>

          <button
            onClick={() => onTabSelect('applied')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'applied'
                ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Applied ({counts.applied})
          </button>
        </div>

        {/* Search Field */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-neutral-500 absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by title, company, or tech..."
            className="w-full bg-[#141b2d] border border-neutral-700/60 rounded-xl pl-9 pr-4 py-1.5 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500 transition"
          />
        </div>
      </div>

      {/* High-Density Job List */}
      <div className="flex-1 overflow-y-auto divide-y divide-neutral-800/60">
        {filteredJobs.length === 0 ? (
          <div className="py-20 text-center flex flex-col items-center justify-center text-neutral-500 space-y-3">
            <Inbox className="w-10 h-10 text-neutral-600 stroke-[1.5]" />
            <p className="text-sm font-medium">No jobs match this filter.</p>
            <p className="text-xs text-neutral-600">
              Paste a job link into the top bar to import new opportunities.
            </p>
          </div>
        ) : (
          filteredJobs.map((job) => (
            <div
              key={job.id}
              onClick={() => onSelectJob(job)}
              className="px-6 py-4 hover:bg-[#141b2d]/60 cursor-pointer transition flex items-center justify-between gap-4 group"
            >
              {/* Left Details: Priority Star + Role + Company */}
              <div className="flex items-start space-x-3.5 min-w-0 flex-1">
                {/* Priority Star Toggle */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onTogglePriority(job.id);
                  }}
                  className={`p-1.5 rounded-lg transition mt-0.5 shrink-0 ${
                    job.is_priority
                      ? 'text-amber-400 hover:bg-amber-400/10'
                      : 'text-neutral-600 hover:text-neutral-400 hover:bg-neutral-800'
                  }`}
                  title={job.is_priority ? 'Starred as Priority' : 'Mark as Priority'}
                >
                  <Star className={`w-4 h-4 ${job.is_priority ? 'fill-amber-400' : ''}`} />
                </button>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition truncate">
                      {job.title}
                    </h3>

                    {/* Source platform tag */}
                    {job.source_platform && (
                      <span className="shrink-0 px-2 py-0.5 rounded text-[10px] font-mono bg-neutral-800 text-neutral-400 border border-neutral-700/60">
                        {job.source_platform}
                      </span>
                    )}

                    {/* Has cover letter badge */}
                    {job.cover_letter && (
                      <span className="shrink-0 px-1.5 py-0.2 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center">
                        <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" /> CL
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-neutral-400 mt-1">
                    <span className="flex items-center text-neutral-300 font-medium">
                      <Building className="w-3.5 h-3.5 mr-1 text-neutral-500" />
                      {job.company}
                    </span>
                    <span>•</span>
                    <span className="flex items-center">
                      <MapPin className="w-3.5 h-3.5 mr-1 text-neutral-500" />
                      {job.location || 'Remote'}
                    </span>
                    {job.created_at && (
                      <>
                        <span>•</span>
                        <span className="flex items-center text-neutral-500">
                          <Calendar className="w-3 h-3 mr-1" />
                          {job.created_at.slice(0, 10)}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Controls: Status Selector & Actions */}
              <div
                className="flex items-center space-x-3 shrink-0"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Inline Status Dropdown */}
                <select
                  value={job.status}
                  onChange={(e) => onStatusChange(job.id, e.target.value as JobStatus)}
                  className={`text-xs font-semibold rounded-lg px-2.5 py-1 border focus:outline-none transition ${
                    job.status === 'APPLIED'
                      ? 'bg-indigo-500/15 border-indigo-500/40 text-indigo-300'
                      : job.status === 'SAVED' || job.status === 'APPROVED'
                      ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                      : 'bg-neutral-800 border-neutral-700 text-neutral-400'
                  }`}
                >
                  <option value="SAVED">Saved</option>
                  <option value="APPLIED">Applied</option>
                  <option value="ARCHIVED">Archived</option>
                  <option value="NEW">New</option>
                </select>

                {/* External URL Link */}
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 rounded-lg text-neutral-500 hover:text-blue-400 hover:bg-neutral-800 transition"
                    title="Open original job link"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}

                {/* View Details Chevron */}
                <button
                  type="button"
                  onClick={() => onSelectJob(job)}
                  className="p-1 rounded-lg text-neutral-500 group-hover:text-white transition"
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
