import React, { useState, useEffect } from 'react';
import type { UserProfile } from '../../types';
import { api } from '../../api/client';
import { Briefcase, FolderGit2, Award, RefreshCw } from 'lucide-react';

export const MasterProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'skills' | 'projects' | 'experience'>('skills');

  useEffect(() => {
    api
      .getProfile()
      .then((data) => setProfile(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0B0F19]">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex-1 p-8 text-center text-gray-400 bg-[#0B0F19]">
        Failed to load profile. Please make sure the backend is running.
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#0B0F19] flex justify-center">
      <div className="w-full max-w-5xl space-y-6">
        {/* Profile Header Card */}
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-600/20 border border-blue-500/30 rounded-2xl flex items-center justify-center text-blue-400 font-bold text-2xl">
              {profile.name?.charAt(0) || 'Z'}
            </div>
            <div>
              <h1 className="text-2xl font-black text-white">{profile.name}</h1>
              <p className="text-xs text-gray-400 mt-1 max-w-2xl">{profile.headline}</p>
            </div>
          </div>
          <a
            href="/profile/preview"
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-xl text-xs font-bold transition border border-gray-700 self-start md:self-auto"
          >
            Open Full HTML Preview
          </a>
        </div>

        {/* Section Segmented Control */}
        <div className="flex space-x-2 border-b border-gray-800 pb-2">
          <button
            onClick={() => setActiveTab('skills')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'skills'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            <Award className="w-4 h-4" />
            Skills ({profile.skills.length})
          </button>
          <button
            onClick={() => setActiveTab('projects')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'projects'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            <FolderGit2 className="w-4 h-4" />
            Projects ({profile.projects.length})
          </button>
          <button
            onClick={() => setActiveTab('experience')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'experience'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-900'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            Experience ({profile.experiences.length})
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'skills' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profile.skills.map((s, idx) => (
              <div key={idx} className="bg-gray-900 border border-gray-800 p-4 rounded-xl">
                <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">
                  {s.category}
                </h3>
                <p className="text-xs text-gray-300 leading-relaxed">{s.name}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="space-y-4">
            {profile.projects.map((proj, idx) => (
              <div key={idx} className="bg-gray-900 border border-gray-800 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">{proj.name}</h3>
                  <span className="text-xs text-gray-400">{proj.date_range}</span>
                </div>
                <p className="text-xs text-blue-400 font-semibold mb-3">{proj.role}</p>
                {proj.detailed_context && (
                  <p className="text-xs text-gray-400 bg-gray-950/60 p-3 rounded-xl border border-gray-800/80 mb-4 leading-relaxed">
                    {proj.detailed_context}
                  </p>
                )}
                <div className="space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-gray-500 block">
                    Curated Knowledge Base Bullets ({proj.bullets.length})
                  </span>
                  {proj.bullets.map((b, bIdx) => (
                    <div
                      key={bIdx}
                      className="text-xs text-gray-300 bg-gray-950/40 p-2.5 rounded-lg border border-gray-800/60 flex items-start gap-2"
                    >
                      <span className="text-blue-500 font-bold">•</span>
                      <span className="flex-1">{b.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'experience' && (
          <div className="space-y-4">
            {profile.experiences.map((exp, idx) => (
              <div key={idx} className="bg-gray-900 border border-gray-800 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">{exp.company}</h3>
                  <span className="text-xs text-gray-400">{exp.date_range}</span>
                </div>
                <p className="text-xs text-blue-400 font-semibold mb-3">{exp.title}</p>
                <div className="space-y-2">
                  {exp.bullets.map((b, bIdx) => (
                    <div
                      key={bIdx}
                      className="text-xs text-gray-300 bg-gray-950/40 p-2.5 rounded-lg border border-gray-800/60 flex items-start gap-2"
                    >
                      <span className="text-blue-500 font-bold">•</span>
                      <span className="flex-1">{b.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
