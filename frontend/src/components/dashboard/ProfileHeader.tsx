import React from 'react';
import type { UserProfile } from '../../types';
import { Briefcase, Star, BookmarkCheck, MapPin, Sparkles } from 'lucide-react';

interface ProfileHeaderProps {
  profile: UserProfile | null;
  totalJobs: number;
  priorityJobs: number;
  savedJobs: number;
  activeTab: 'all' | 'priority' | 'saved' | 'applied';
  onTabSelect: (tab: 'all' | 'priority' | 'saved' | 'applied') => void;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  profile,
  totalJobs,
  priorityJobs,
  savedJobs,
  activeTab,
  onTabSelect,
}) => {
  return (
    <div className="bg-[#111625] border-b border-neutral-800 px-6 py-5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* User Identity Info */}
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-blue-500/20 shrink-0">
            {profile?.name ? profile.name.charAt(0) : 'Z'}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-white tracking-tight">
                {profile?.name || 'Zet Donaue Samson'}
              </h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                <Sparkles className="w-3 h-3 mr-1" /> Active Jobflow
              </span>
            </div>
            <p className="text-xs text-neutral-400 line-clamp-1 max-w-2xl mt-0.5">
              {profile?.headline || 'Software Developer & DevOps Engineer'}
            </p>
            {profile?.location && (
              <p className="text-xs text-neutral-500 flex items-center mt-1">
                <MapPin className="w-3 h-3 mr-1" /> {profile.location}
              </p>
            )}
          </div>
        </div>

        {/* Live Metrics Counter Cards */}
        <div className="flex items-center gap-2">
          {/* All Jobs */}
          <button
            onClick={() => onTabSelect('all')}
            className={`px-4 py-2.5 rounded-xl border text-left transition flex items-center space-x-3 ${
              activeTab === 'all'
                ? 'bg-blue-600/15 border-blue-500/50 text-white shadow-sm'
                : 'bg-[#182032] border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700'
            }`}
          >
            <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
              <Briefcase className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs text-neutral-400 font-medium">All Jobs</div>
              <div className="text-lg font-bold text-white leading-tight">{totalJobs}</div>
            </div>
          </button>

          {/* Priority Jobs */}
          <button
            onClick={() => onTabSelect('priority')}
            className={`px-4 py-2.5 rounded-xl border text-left transition flex items-center space-x-3 ${
              activeTab === 'priority'
                ? 'bg-amber-500/15 border-amber-500/50 text-white shadow-sm'
                : 'bg-[#182032] border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700'
            }`}
          >
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
              <Star className="w-4 h-4 fill-amber-400" />
            </div>
            <div>
              <div className="text-xs text-neutral-400 font-medium">Priority</div>
              <div className="text-lg font-bold text-amber-400 leading-tight">{priorityJobs}</div>
            </div>
          </button>

          {/* Saved Jobs */}
          <button
            onClick={() => onTabSelect('saved')}
            className={`px-4 py-2.5 rounded-xl border text-left transition flex items-center space-x-3 ${
              activeTab === 'saved'
                ? 'bg-emerald-500/15 border-emerald-500/50 text-white shadow-sm'
                : 'bg-[#182032] border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700'
            }`}
          >
            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
              <BookmarkCheck className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs text-neutral-400 font-medium">Saved</div>
              <div className="text-lg font-bold text-emerald-400 leading-tight">{savedJobs}</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};
