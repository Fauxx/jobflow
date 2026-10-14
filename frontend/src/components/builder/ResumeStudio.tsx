import React, { useState } from 'react';
import type { TailoredResume, TailoredBullet } from '../../types';
import { ArrowLeft, Sparkles, Download, RefreshCw } from 'lucide-react';
import { api } from '../../api/client';

interface ResumeStudioProps {
  jobId: number;
  initialResume: TailoredResume;
  onBack: () => void;
}

export const ResumeStudio: React.FC<ResumeStudioProps> = ({
  jobId,
  initialResume,
  onBack,
}) => {
  const [resume, setResume] = useState<TailoredResume>(initialResume);
  const [activeSection, setActiveSection] = useState<'experiences' | 'projects'>('experiences');
  const [customPrompt, setCustomPrompt] = useState('');
  const [isAdjusting, setIsAdjusting] = useState(false);

  const handleAdjustSection = async (sectionName: string, sectionType: string, currentBullets: TailoredBullet[]) => {
    if (!customPrompt.trim()) return;
    setIsAdjusting(true);
    try {
      const res = await api.adjustSectionWithAI(jobId, {
        section_name: sectionName,
        section_type: sectionType,
        instruction: customPrompt,
        current_bullets: currentBullets,
      });

      if (res && res.bullets) {
        // Update the section bullets in state
        if (sectionType === 'experience') {
          setResume((prev) => ({
            ...prev,
            experiences: prev.experiences.map((exp) =>
              exp.company === sectionName ? { ...exp, bullets: res.bullets } : exp
            ),
          }));
        } else {
          setResume((prev) => ({
            ...prev,
            projects: prev.projects.map((proj) =>
              proj.name === sectionName ? { ...proj, bullets: res.bullets } : proj
            ),
          }));
        }
        setCustomPrompt('');
      }
    } catch (err) {
      console.error(err);
      alert('Failed to adjust section with AI.');
    } finally {
      setIsAdjusting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0F19]">
      {/* Studio Header */}
      <div className="h-14 border-b border-gray-800 bg-gray-900 px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-white transition bg-gray-800 px-3 py-1.5 rounded-lg border border-gray-700"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Pipeline
          </button>
          <span className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            AI Resume Studio
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href={`/applications/${jobId}/generate`}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            Export ATS PDF
          </a>
        </div>
      </div>

      {/* Split-Pane Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: AI Curator & Bullet Customizer */}
        <div className="w-full md:w-1/2 border-r border-gray-800 flex flex-col bg-gray-950/40">
          {/* Section Navigation Tabs */}
          <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveSection('experiences')}
                className={`text-xs px-3 py-1.5 rounded-lg font-bold transition ${
                  activeSection === 'experiences'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                Experience ({resume.experiences.length})
              </button>
              <button
                onClick={() => setActiveSection('projects')}
                className={`text-xs px-3 py-1.5 rounded-lg font-bold transition ${
                  activeSection === 'projects'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                Projects ({resume.projects.length})
              </button>
            </div>
          </div>

          {/* AI Custom Prompt Box */}
          <div className="p-4 bg-gray-900 border-b border-gray-800">
            <label className="text-xs font-bold text-gray-300 block mb-1.5">
              Refine active section with AI Instruction:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="e.g. Highlight Kubernetes orchestration, omit frontend details..."
                className="flex-1 bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
              />
              <button
                disabled={isAdjusting || !customPrompt.trim()}
                onClick={() => {
                  const target =
                    activeSection === 'experiences'
                      ? resume.experiences[0]
                      : resume.projects[0];
                  if (target) {
                    handleAdjustSection(
                      activeSection === 'experiences' ? (target as any).company : (target as any).name,
                      activeSection === 'experiences' ? 'experience' : 'project',
                      target.bullets
                    );
                  }
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition shrink-0 flex items-center gap-1.5"
              >
                {isAdjusting ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5" />
                )}
                Curate
              </button>
            </div>
          </div>

          {/* Cards List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {activeSection === 'experiences'
              ? resume.experiences.map((exp, idx) => (
                  <div key={idx} className="bg-gray-900 border border-gray-800 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold text-sm text-white">{exp.company}</h4>
                      <span className="text-xs text-gray-400">{exp.date_range}</span>
                    </div>
                    <p className="text-xs text-blue-400 font-semibold mb-3">{exp.title}</p>
                    <div className="space-y-2">
                      {exp.bullets.map((b, bIdx) => (
                        <div
                          key={bIdx}
                          className="text-xs text-gray-300 bg-gray-950/60 p-2.5 rounded-lg border border-gray-800/80 flex items-start gap-2"
                        >
                          <span className="text-blue-500 font-bold">•</span>
                          <span className="flex-1">{b.tailored_text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              : resume.projects.map((proj, idx) => (
                  <div key={idx} className="bg-gray-900 border border-gray-800 p-4 rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold text-sm text-white">{proj.name}</h4>
                      <span className="text-xs text-gray-400">{proj.date_range}</span>
                    </div>
                    <p className="text-xs text-purple-400 font-semibold mb-3">{proj.role}</p>
                    <div className="space-y-2">
                      {proj.bullets.map((b, bIdx) => (
                        <div
                          key={bIdx}
                          className="text-xs text-gray-300 bg-gray-950/60 p-2.5 rounded-lg border border-gray-800/80 flex items-start gap-2"
                        >
                          <span className="text-purple-500 font-bold">•</span>
                          <span className="flex-1">{b.tailored_text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
          </div>
        </div>

        {/* Right Pane: Live Pixel-Accurate A4 Preview */}
        <div className="w-full md:w-1/2 p-6 overflow-y-auto bg-gray-950 flex flex-col items-center justify-start">
          <div className="w-full max-w-[650px] bg-white text-gray-900 shadow-2xl rounded-sm p-8 text-xs font-sans">
            {/* Header */}
            <div className="border-b border-gray-300 pb-3 mb-4 text-center">
              <h1 className="text-xl font-bold text-gray-900 uppercase tracking-tight">
                Zet Donaue Samson
              </h1>
              <p className="text-[11px] text-gray-600 mt-1">
                Pasig City, Philippines • zetsamson@gmail.com • +63 998 280 6036 • linkedin.com/in/zet02
              </p>
            </div>

            {/* Summary */}
            <div className="mb-4">
              <h2 className="text-xs font-bold uppercase tracking-wider text-gray-900 border-b border-gray-200 pb-1 mb-2">
                Professional Summary
              </h2>
              <p className="text-[11px] text-gray-700 leading-relaxed">{resume.summary}</p>
            </div>

            {/* Experience */}
            <div className="mb-4">
              <h2 className="text-xs font-bold uppercase tracking-wider text-gray-900 border-b border-gray-200 pb-1 mb-2">
                Professional Experience
              </h2>
              <div className="space-y-3">
                {resume.experiences.map((exp, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between font-bold text-gray-800 text-[11px]">
                      <span>{exp.title}</span>
                      <span>{exp.date_range}</span>
                    </div>
                    <div className="text-[11px] text-gray-600 italic mb-1">{exp.company}</div>
                    <ul className="list-disc pl-4 space-y-1 text-[10.5px] text-gray-700">
                      {exp.bullets.map((b, bIdx) => (
                        <li key={bIdx}>{b.tailored_text}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Projects */}
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-gray-900 border-b border-gray-200 pb-1 mb-2">
                Technical Projects
              </h2>
              <div className="space-y-3">
                {resume.projects.map((proj, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between font-bold text-gray-800 text-[11px]">
                      <span>{proj.name}</span>
                      <span>{proj.date_range}</span>
                    </div>
                    <div className="text-[11px] text-gray-600 italic mb-1">{proj.role}</div>
                    <ul className="list-disc pl-4 space-y-1 text-[10.5px] text-gray-700">
                      {proj.bullets.map((b, bIdx) => (
                        <li key={bIdx}>{b.tailored_text}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
