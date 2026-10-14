import React, { useState } from 'react';
import type { TailoredResume, TailoredBullet, Job } from '../../types';
import {
  ArrowLeft,
  Sparkles,
  Printer,
  Eye,
  Save,
  CheckCircle2,
  Trash2,
  Plus,
  Loader2,
  ExternalLink,
  Briefcase,
  X,
  Send,
} from 'lucide-react';
import { api } from '../../api/client';

interface ResumeStudioProps {
  jobId: number;
  initialResume: TailoredResume;
  job?: Job | null;
  onBack: () => void;
}

export const ResumeStudio: React.FC<ResumeStudioProps> = ({
  jobId,
  initialResume,
  job,
  onBack,
}) => {
  const [resume, setResume] = useState<TailoredResume>(initialResume);
  const [activeTab, setActiveTab] = useState<'experiences' | 'projects'>('experiences');

  // Summary state
  const [summaryDraft, setSummaryDraft] = useState(resume.summary || '');
  const [summaryPrompt, setSummaryPrompt] = useState('');
  const [isRefiningSummary, setIsRefiningSummary] = useState(false);

  // Skills state
  const [skillsList, setSkillsList] = useState<string[]>(resume.skills || []);
  const [newSkillInput, setNewSkillInput] = useState('');
  const [skillsPrompt, setSkillsPrompt] = useState('');
  const [isRefiningSkills, setIsRefiningSkills] = useState(false);

  // Card-level AI Prompt
  const [cardPrompts, setCardPrompts] = useState<{ [key: string]: string }>({});
  const [loadingCardId, setLoadingCardId] = useState<string | null>(null);

  // Global Co-Pilot Prompt
  const [globalPrompt, setGlobalPrompt] = useState('');
  const [isGlobalAdjusting, setIsGlobalAdjusting] = useState(false);

  // Status & Modals
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const showSaveSuccess = (msg: string) => {
    setSaveMsg(msg);
    setTimeout(() => setSaveMsg(''), 3500);
  };

  // 1. Browser-Based Print / Save to PC (Native Print Engine)
  const handleBrowserPrint = () => {
    // Open the browser print endpoint in a new tab which triggers window.print()
    window.open(`/applications/${jobId}/preview/html?print=true`, '_blank');
  };

  // 2. Save Entire Tailored Resume to DB
  const handleSaveToDb = async () => {
    try {
      setSaving(true);
      const payload: TailoredResume = {
        ...resume,
        summary: summaryDraft,
        skills: skillsList,
      };
      await api.saveTailoredResume(jobId, payload);
      setResume(payload);
      showSaveSuccess('Saved tailored resume to database!');
    } catch (err) {
      console.error(err);
      alert('Failed to save resume draft.');
    } finally {
      setSaving(false);
    }
  };

  // 3. AI Refine Summary
  const handleRefineSummary = async () => {
    if (!summaryPrompt.trim()) return;
    try {
      setIsRefiningSummary(true);
      const res = await api.adjustSummaryWithAI(jobId, summaryPrompt.trim(), summaryDraft);
      setSummaryDraft(res.summary);
      setSummaryPrompt('');
      showSaveSuccess('Summary refined by AI!');
    } catch (err) {
      console.error(err);
      alert('Failed to adjust summary with AI.');
    } finally {
      setIsRefiningSummary(false);
    }
  };

  // 4. AI Refine Skills
  const handleRefineSkills = async () => {
    if (!skillsPrompt.trim()) return;
    try {
      setIsRefiningSkills(true);
      const res = await api.adjustSkillsWithAI(jobId, skillsPrompt.trim(), skillsList);
      setSkillsList(res.skills);
      setSkillsPrompt('');
      showSaveSuccess('Skills refined by AI!');
    } catch (err) {
      console.error(err);
      alert('Failed to adjust skills with AI.');
    } finally {
      setIsRefiningSkills(false);
    }
  };

  // Add / Remove Skills
  const handleAddSkill = () => {
    if (!newSkillInput.trim()) return;
    setSkillsList([...skillsList, newSkillInput.trim()]);
    setNewSkillInput('');
  };

  const handleRemoveSkill = (indexToRemove: number) => {
    setSkillsList(skillsList.filter((_, idx) => idx !== indexToRemove));
  };

  // 5. Card-level Bullet Refinement
  const handleRefineCard = async (sectionName: string, sectionType: 'experience' | 'project', currentBullets: TailoredBullet[]) => {
    const prompt = cardPrompts[sectionName];
    if (!prompt || !prompt.trim()) return;

    try {
      setLoadingCardId(sectionName);
      const res = await api.adjustSectionWithAI(jobId, {
        section_name: sectionName,
        section_type: sectionType,
        instruction: prompt.trim(),
        current_bullets: currentBullets.map((b) => b.tailored_text || b.original_text),
      });

      if (res && res.bullets) {
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
        setCardPrompts((prev) => ({ ...prev, [sectionName]: '' }));
        showSaveSuccess(`Updated bullets for ${sectionName}!`);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to refine section with AI.');
    } finally {
      setLoadingCardId(null);
    }
  };

  // Delete Bullet
  const handleDeleteBullet = (sectionType: 'experience' | 'project', sectionIndex: number, bulletIndex: number) => {
    if (sectionType === 'experience') {
      const updated = [...resume.experiences];
      updated[sectionIndex].bullets = updated[sectionIndex].bullets.filter((_, i) => i !== bulletIndex);
      setResume({ ...resume, experiences: updated });
    } else {
      const updated = [...resume.projects];
      updated[sectionIndex].bullets = updated[sectionIndex].bullets.filter((_, i) => i !== bulletIndex);
      setResume({ ...resume, projects: updated });
    }
  };

  // Edit Bullet Text
  const handleEditBulletText = (
    sectionType: 'experience' | 'project',
    sectionIndex: number,
    bulletIndex: number,
    newText: string
  ) => {
    if (sectionType === 'experience') {
      const updated = [...resume.experiences];
      updated[sectionIndex].bullets[bulletIndex].tailored_text = newText;
      setResume({ ...resume, experiences: updated });
    } else {
      const updated = [...resume.projects];
      updated[sectionIndex].bullets[bulletIndex].tailored_text = newText;
      setResume({ ...resume, projects: updated });
    }
  };

  // 6. Global Resume Adjustment
  const handleGlobalAdjust = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!globalPrompt.trim()) return;
    try {
      setIsGlobalAdjusting(true);
      await api.adjustEntireResumeWithAI(jobId, globalPrompt.trim());
      const freshDraft = await api.getTailoredDraft(jobId);
      setResume(freshDraft);
      setSummaryDraft(freshDraft.summary || '');
      setSkillsList(freshDraft.skills || []);
      setGlobalPrompt('');
      showSaveSuccess('Entire resume adjusted by AI!');
    } catch (err) {
      console.error(err);
      alert('Failed to adjust entire resume.');
    } finally {
      setIsGlobalAdjusting(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#080c14] text-slate-100 overflow-hidden">
      {/* ── Top Header ──────────────────────────────────────────────────────── */}
      <header className="h-15 border-b border-white/[0.08] bg-[#0d1322] px-6 flex items-center justify-between shrink-0 z-30 shadow-md">
        <div className="flex items-center space-x-4 min-w-0">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs font-bold text-slate-300 hover:text-white transition bg-slate-800/80 hover:bg-slate-700 px-3 py-1.5 rounded-xl border border-white/10 shadow-sm"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <div className="min-w-0">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
                AI Resume Co-Pilot
              </span>
              <span className="text-slate-600">•</span>
              <h1 className="text-sm font-bold text-white truncate max-w-lg">
                Targeting: {job?.title || 'Job Application'}
              </h1>
              {job?.company && (
                <span className="text-xs text-slate-400 font-medium">
                  at {job.company}
                </span>
              )}
              {job?.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-500 hover:text-blue-400"
                  title="View original posting"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2.5 shrink-0">
          {saveMsg && (
            <span className="text-xs text-emerald-400 font-medium flex items-center mr-2 animate-in fade-in">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              {saveMsg}
            </span>
          )}

          {/* Live Preview Button */}
          <button
            onClick={() => setIsPreviewOpen(true)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold rounded-xl border border-white/10 transition flex items-center gap-1.5 shadow-sm"
            title="Preview 1-page paper layout"
          >
            <Eye className="w-3.5 h-3.5 text-slate-400" />
            <span>Live Preview</span>
          </button>

          {/* Save Draft Button */}
          <button
            onClick={handleSaveToDb}
            disabled={saving}
            className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold rounded-xl border border-white/10 transition flex items-center gap-1.5 shadow-sm"
          >
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5 text-blue-400" />}
            <span>Save Draft</span>
          </button>

          {/* Native Browser Print / Save PDF Button */}
          <button
            onClick={handleBrowserPrint}
            className="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-lg shadow-blue-500/25 ring-1 ring-white/20"
            title="Open browser print dialog to save PDF directly to PC"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print / Save to PC (PDF)</span>
          </button>
        </div>
      </header>

      {/* ── Main Split Screen ───────────────────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Pane: Job Description (38% width) */}
        <section className="w-full md:w-[38%] border-r border-white/[0.08] bg-[#0a0e18] flex flex-col h-full overflow-hidden shrink-0">
          <div className="p-4 bg-[#0d1322] border-b border-white/[0.08] shrink-0 flex items-center justify-between">
            <h2 className="font-bold text-slate-200 flex items-center space-x-2 text-xs uppercase tracking-wider">
              <Briefcase className="w-3.5 h-3.5 text-blue-400" />
              <span>Job Description & Requirements</span>
            </h2>
            {job?.source_platform && (
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                {job.source_platform}
              </span>
            )}
          </div>

          <div className="p-6 overflow-y-auto flex-1 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-wrap select-text">
            {job?.cleaned_description || job?.raw_description || (
              <div className="text-slate-500 italic py-10 text-center">
                No job description content available.
              </div>
            )}
          </div>
        </section>

        {/* Right Pane: Interactive Co-Pilot Resume Editor (62% width) */}
        <section className="flex-1 bg-[#080c14] flex flex-col h-full overflow-hidden relative min-w-0">
          
          <div className="flex-1 overflow-y-auto p-6 space-y-6 pb-28">
            
            {/* 1. Professional Summary Card */}
            <div className="bg-[#0e1424] border border-white/[0.08] rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                  <span>Tailored Professional Summary</span>
                </h3>
              </div>

              <textarea
                rows={3}
                value={summaryDraft}
                onChange={(e) => setSummaryDraft(e.target.value)}
                placeholder="Professional summary..."
                className="w-full bg-[#131b2e] border border-slate-700/60 rounded-xl p-3 text-xs text-slate-200 leading-relaxed focus:outline-none focus:border-blue-500 resize-none font-sans"
              />

              {/* AI summary prompt */}
              <div className="mt-2.5 flex items-center gap-2">
                <input
                  type="text"
                  value={summaryPrompt}
                  onChange={(e) => setSummaryPrompt(e.target.value)}
                  placeholder="Ask AI to refine summary (e.g. emphasize 5+ yrs cloud experience)..."
                  className="flex-1 bg-[#131b2e] border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleRefineSummary}
                  disabled={isRefiningSummary || !summaryPrompt.trim()}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 shrink-0 transition"
                >
                  {isRefiningSummary ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  <span>Refine</span>
                </button>
              </div>
            </div>

            {/* 2. Technical Skills Card */}
            <div className="bg-[#0e1424] border border-white/[0.08] rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                  <span>Targeted Technical Skills</span>
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">
                  {skillsList.length} skills listed
                </span>
              </div>

              {/* Skills Tags */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                {skillsList.map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700/60 group"
                  >
                    <span>{skill}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(idx)}
                      className="ml-1.5 text-slate-500 hover:text-red-400 transition"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>

              {/* Add Skill + Refine Skills */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                    placeholder="Add skill tag..."
                    className="flex-1 bg-[#131b2e] border border-slate-700/60 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={handleAddSkill}
                    className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold flex items-center"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-center gap-1.5">
                  <input
                    type="text"
                    value={skillsPrompt}
                    onChange={(e) => setSkillsPrompt(e.target.value)}
                    placeholder="AI prompt to tailor skill set..."
                    className="flex-1 bg-[#131b2e] border border-slate-700/60 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={handleRefineSkills}
                    disabled={isRefiningSkills || !skillsPrompt.trim()}
                    className="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 shrink-0"
                  >
                    {isRefiningSkills ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                    <span>Refine</span>
                  </button>
                </div>
              </div>
            </div>

            {/* 3. Section Segmented Tabs (Experience vs Projects) */}
            <div className="flex items-center space-x-2 border-b border-white/[0.08] pb-3">
              <button
                onClick={() => setActiveTab('experiences')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
                  activeTab === 'experiences'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'bg-[#101626] text-slate-400 hover:text-white border border-white/[0.06]'
                }`}
              >
                <span>Work Experience</span>
                <span className="px-1.5 py-0.2 rounded-md bg-white/10 text-[10px]">
                  {resume.experiences.length}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('projects')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
                  activeTab === 'projects'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'bg-[#101626] text-slate-400 hover:text-white border border-white/[0.06]'
                }`}
              >
                <span>Projects Portfolio</span>
                <span className="px-1.5 py-0.2 rounded-md bg-white/10 text-[10px]">
                  {resume.projects.length}
                </span>
              </button>
            </div>

            {/* Tab: Work Experience Cards */}
            {activeTab === 'experiences' && (
              <div className="space-y-4">
                {resume.experiences.map((exp, secIdx) => (
                  <div
                    key={secIdx}
                    className="bg-[#0e1424] border border-white/[0.08] rounded-2xl p-5 shadow-sm"
                  >
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 mb-3 border-b border-slate-800/80 gap-1">
                      <div>
                        <h4 className="text-sm font-bold text-white">{exp.company}</h4>
                        <p className="text-xs text-blue-400 font-medium">
                          {exp.title} {exp.location && `• ${exp.location}`}
                        </p>
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        {exp.date_range}
                      </span>
                    </div>

                    {/* Bullets List */}
                    <div className="space-y-2.5 mb-4">
                      {exp.bullets.map((bullet, bIdx) => (
                        <div
                          key={bIdx}
                          className="flex items-start space-x-2.5 p-2 rounded-xl hover:bg-slate-800/40 transition group"
                        >
                          <span className="text-blue-400 mt-1 font-bold">•</span>
                          <textarea
                            rows={2}
                            value={bullet.tailored_text || bullet.original_text}
                            onChange={(e) =>
                              handleEditBulletText('experience', secIdx, bIdx, e.target.value)
                            }
                            className="w-full bg-transparent text-xs text-slate-200 leading-relaxed focus:bg-[#131b2e] focus:p-2 focus:rounded-lg focus:border focus:border-blue-500/50 outline-none resize-none"
                          />
                          <button
                            type="button"
                            onClick={() => handleDeleteBullet('experience', secIdx, bIdx)}
                            className="p-1 rounded text-slate-600 hover:text-red-400 transition opacity-0 group-hover:opacity-100 shrink-0"
                            title="Remove bullet"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>

                    {/* Card-Level AI Refine Bar */}
                    <div className="pt-3 border-t border-slate-800/80 flex items-center gap-2">
                      <input
                        type="text"
                        value={cardPrompts[exp.company || ''] || ''}
                        onChange={(e) =>
                          setCardPrompts({ ...cardPrompts, [exp.company || '']: e.target.value })
                        }
                        placeholder={`Ask AI to refine ${exp.company} bullets (e.g. emphasize scale and metrics)...`}
                        className="flex-1 bg-[#131b2e] border border-slate-700/60 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                      />
                      <button
                        onClick={() =>
                          handleRefineCard(exp.company || '', 'experience', exp.bullets)
                        }
                        disabled={
                          loadingCardId === exp.company ||
                          !cardPrompts[exp.company || '']?.trim()
                        }
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 shrink-0"
                      >
                        {loadingCardId === exp.company ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Sparkles className="w-3.5 h-3.5" />
                        )}
                        <span>Refine Role</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab: Projects Cards */}
            {activeTab === 'projects' && (
              <div className="space-y-4">
                {resume.projects.map((proj, secIdx) => (
                  <div
                    key={secIdx}
                    className="bg-[#0e1424] border border-white/[0.08] rounded-2xl p-5 shadow-sm"
                  >
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 mb-3 border-b border-slate-800/80 gap-1">
                      <div>
                        <h4 className="text-sm font-bold text-white">{proj.name}</h4>
                        <p className="text-xs text-blue-400 font-medium">
                          {proj.role} {proj.tech_stack && `• ${proj.tech_stack}`}
                        </p>
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        {proj.date_range}
                      </span>
                    </div>

                    {/* Bullets List */}
                    <div className="space-y-2.5 mb-4">
                      {proj.bullets.map((bullet, bIdx) => (
                        <div
                          key={bIdx}
                          className="flex items-start space-x-2.5 p-2 rounded-xl hover:bg-slate-800/40 transition group"
                        >
                          <span className="text-indigo-400 mt-1 font-bold">•</span>
                          <textarea
                            rows={2}
                            value={bullet.tailored_text || bullet.original_text}
                            onChange={(e) =>
                              handleEditBulletText('project', secIdx, bIdx, e.target.value)
                            }
                            className="w-full bg-transparent text-xs text-slate-200 leading-relaxed focus:bg-[#131b2e] focus:p-2 focus:rounded-lg focus:border focus:border-blue-500/50 outline-none resize-none"
                          />
                          <button
                            type="button"
                            onClick={() => handleDeleteBullet('project', secIdx, bIdx)}
                            className="p-1 rounded text-slate-600 hover:text-red-400 transition opacity-0 group-hover:opacity-100 shrink-0"
                            title="Remove bullet"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>

                    {/* Card-Level AI Refine Bar */}
                    <div className="pt-3 border-t border-slate-800/80 flex items-center gap-2">
                      <input
                        type="text"
                        value={cardPrompts[proj.name || ''] || ''}
                        onChange={(e) =>
                          setCardPrompts({ ...cardPrompts, [proj.name || '']: e.target.value })
                        }
                        placeholder={`Ask AI to refine ${proj.name} bullets...`}
                        className="flex-1 bg-[#131b2e] border border-slate-700/60 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                      />
                      <button
                        onClick={() =>
                          handleRefineCard(proj.name || '', 'project', proj.bullets)
                        }
                        disabled={
                          loadingCardId === proj.name ||
                          !cardPrompts[proj.name || '']?.trim()
                        }
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 shrink-0"
                      >
                        {loadingCardId === proj.name ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Sparkles className="w-3.5 h-3.5" />
                        )}
                        <span>Refine Project</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Floating Global AI Co-Pilot Prompt Bar (Bottom) ─────────────── */}
          <div className="absolute bottom-4 left-6 right-6 z-20">
            <form
              onSubmit={handleGlobalAdjust}
              className="bg-[#0e1424]/90 backdrop-blur-xl border border-white/[0.12] rounded-2xl p-2 shadow-2xl flex items-center gap-2"
            >
              <div className="pl-3 text-blue-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={globalPrompt}
                onChange={(e) => setGlobalPrompt(e.target.value)}
                placeholder="Ask Co-Pilot to adjust entire resume (e.g. emphasize DevOps, Kubernetes, and high availability)..."
                className="flex-1 bg-transparent border-none text-xs text-white placeholder-slate-400 focus:outline-none py-1.5"
              />
              <button
                type="submit"
                disabled={isGlobalAdjusting || !globalPrompt.trim()}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm"
              >
                {isGlobalAdjusting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Thinking...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>Adjust All</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </section>
      </div>

      {/* ── Live 1-Page Paper Preview Modal ──────────────────────────────────── */}
      {isPreviewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 sm:p-6">
          <div className="bg-[#111625] border border-white/10 rounded-2xl w-full max-w-4xl h-[92vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-3.5 border-b border-slate-800 bg-[#0d1322] flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-bold text-white">
                  Live 1-Page ATS Resume Preview
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleBrowserPrint}
                  className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1.5 transition"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / Save to PC</span>
                </button>
                <button
                  onClick={() => setIsPreviewOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex-1 bg-slate-900 overflow-hidden">
              <iframe
                src={`/applications/${jobId}/preview/html?t=${Date.now()}`}
                title="Resume Paper Preview"
                className="w-full h-full border-none"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
