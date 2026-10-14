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
    <div className="relative bg-[#0c101d] border-b border-white/[0.08] px-6 py-6 overflow-hidden">
      {/* Subtle Radial Glow in background */}
      <div className="absolute top-0 left-1/4 w-96 h-32 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-0 right-1/4 w-96 h-32 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5 relative z-10">
        
        {/* User Identity Info */}
        <div className="flex items-center space-x-4">
          <div className="relative shrink-0">
            <div className="w-13 h-13 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-500 flex items-center justify-center text-white font-black text-2xl shadow-xl shadow-blue-500/25 ring-1 ring-white/20">
              {profile?.name ? profile.name.charAt(0) : 'Z'}
            </div>
            {/* Live Beacon Dot */}
            <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-[#0c101d] flex items-center justify-center shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            </span>
          </div>

          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-xl font-extrabold text-white tracking-tight">
                {profile?.name || 'Zet Donaue Samson'}
              </h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/10 text-blue-300 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]">
                <Sparkles className="w-3 h-3 mr-1 text-blue-400" /> Co-Pilot Ready
              </span>
            </div>

            <p className="text-xs text-slate-400 line-clamp-1 max-w-2xl mt-1 font-medium">
              {profile?.headline || 'Software Developer & DevOps Engineer'}
            </p>

            <div className="flex items-center space-x-3 mt-1.5 text-xs text-slate-500 font-medium">
              {profile?.location && (
                <span className="flex items-center text-slate-400">
                  <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                  {profile.location}
                </span>
              )}
              {profile?.skills && profile.skills.length > 0 && (
                <>
                  <span>•</span>
                  <span className="text-slate-400">
                    <span className="text-blue-400 font-semibold">{profile.skills.length}</span> Skill Categories
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Live Metrics Counter Cards */}
        <div className="flex items-center gap-2.5">
          {/* All Jobs */}
          <button
            onClick={() => onTabSelect('all')}
            className={`px-4.5 py-3 rounded-2xl border text-left transition-all duration-200 flex items-center space-x-3.5 group cursor-pointer ${
              activeTab === 'all'
                ? 'bg-gradient-to-b from-blue-600/20 to-blue-900/30 border-blue-500/60 shadow-[0_0_20px_rgba(37,99,235,0.2)]'
                : 'bg-[#121829]/80 hover:bg-[#161e33] border-white/[0.08] hover:border-white/20'
            }`}
          >
            <div className={`p-2 rounded-xl transition ${
              activeTab === 'all' ? 'bg-blue-500 text-white shadow-md' : 'bg-blue-500/15 text-blue-400 group-hover:bg-blue-500/25'
            }`}>
              <Briefcase className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">All Leads</div>
              <div className="text-xl font-extrabold text-white leading-tight font-mono">{totalJobs}</div>
            </div>
          </button>

          {/* Priority Jobs */}
          <button
            onClick={() => onTabSelect('priority')}
            className={`px-4.5 py-3 rounded-2xl border text-left transition-all duration-200 flex items-center space-x-3.5 group cursor-pointer ${
              activeTab === 'priority'
                ? 'bg-gradient-to-b from-amber-500/20 to-amber-900/30 border-amber-500/60 shadow-[0_0_20px_rgba(245,158,11,0.2)]'
                : 'bg-[#121829]/80 hover:bg-[#161e33] border-white/[0.08] hover:border-white/20'
            }`}
          >
            <div className={`p-2 rounded-xl transition ${
              activeTab === 'priority' ? 'bg-amber-500 text-slate-950 shadow-md' : 'bg-amber-500/15 text-amber-400 group-hover:bg-amber-500/25'
            }`}>
              <Star className="w-4 h-4 fill-current" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Priority</div>
              <div className="text-xl font-extrabold text-amber-300 leading-tight font-mono">{priorityJobs}</div>
            </div>
          </button>

          {/* Saved Jobs */}
          <button
            onClick={() => onTabSelect('saved')}
            className={`px-4.5 py-3 rounded-2xl border text-left transition-all duration-200 flex items-center space-x-3.5 group cursor-pointer ${
              activeTab === 'saved'
                ? 'bg-gradient-to-b from-emerald-500/20 to-emerald-900/30 border-emerald-500/60 shadow-[0_0_20px_rgba(16,185,129,0.2)]'
                : 'bg-[#121829]/80 hover:bg-[#161e33] border-white/[0.08] hover:border-white/20'
            }`}
          >
            <div className={`p-2 rounded-xl transition ${
              activeTab === 'saved' ? 'bg-emerald-500 text-white shadow-md' : 'bg-emerald-500/15 text-emerald-400 group-hover:bg-emerald-500/25'
            }`}>
              <BookmarkCheck className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Saved</div>
              <div className="text-xl font-extrabold text-emerald-300 leading-tight font-mono">{savedJobs}</div>
            </div>
          </button>
        </div>

      </div>
    </div>
  );
};
