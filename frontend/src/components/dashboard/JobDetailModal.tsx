import React, { useState } from 'react';
import type { Job, JobStatus } from '../../types';
import { api } from '../../api/client';
import {
  X,
  Star,
  ExternalLink,
  Edit3,
  Save,
  Sparkles,
  Printer,
  FileDown,
  FileText,
  MapPin,
  Building,
  Loader2,
  CheckCircle2,
  Layers,
  Copy,
  Check,
} from 'lucide-react';

interface JobDetailModalProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdateJob: (updatedJob: Job) => void;
  onOpenResumeStudio: (jobId: number) => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({
  job,
  isOpen,
  onClose,
  onUpdateJob,
  onOpenResumeStudio,
}) => {
  if (!isOpen || !job) return null;

  // Tabs inside modal: 'jd' or 'cover_letter'
  const [activeTab, setActiveTab] = useState<'jd' | 'cover_letter'>('jd');

  // Job Description Edit State
  const [isEditingJd, setIsEditingJd] = useState(false);
  const [descriptionDraft, setDescriptionDraft] = useState(job.cleaned_description || job.raw_description || '');
  const [savingJd, setSavingJd] = useState(false);

  // Cover Letter State
  const [coverLetterContent, setCoverLetterContent] = useState(job.cover_letter || '');
  const [generatingCl, setGeneratingCl] = useState(false);
  const [savingCl, setSavingCl] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');
  const [copiedCl, setCopiedCl] = useState(false);

  // Handle Priority Toggle
  const handleTogglePriority = async () => {
    try {
      const res = await api.toggleJobPriority(job.id);
      onUpdateJob({ ...job, is_priority: res.is_priority });
    } catch (err) {
      console.error(err);
    }
  };

  // Handle Status Change
  const handleStatusChange = async (newStatus: JobStatus) => {
    try {
      await api.updateJobStatus(job.id, newStatus);
      onUpdateJob({ ...job, status: newStatus });
    } catch (err) {
      console.error(err);
    }
  };

  // Save Edited Job Description
  const handleSaveDescription = async () => {
    try {
      setSavingJd(true);
      await api.updateJob(job.id, { description: descriptionDraft });
      onUpdateJob({ ...job, cleaned_description: descriptionDraft, raw_description: descriptionDraft });
      setIsEditingJd(false);
      showTemporarySuccess('Job description saved to database!');
    } catch (err) {
      console.error(err);
      alert('Failed to save job description.');
    } finally {
      setSavingJd(false);
    }
  };

  // Generate Cover Letter via AI
  const handleGenerateCoverLetter = async () => {
    try {
      setGeneratingCl(true);
      const res = await api.generateCoverLetter(job.id);
      setCoverLetterContent(res.draft);
      await api.saveCoverLetter(job.id, res.draft);
      onUpdateJob({ ...job, cover_letter: res.draft });
      showTemporarySuccess('Cover letter generated and saved!');
    } catch (err) {
      console.error(err);
      alert('Failed to generate cover letter.');
    } finally {
      setGeneratingCl(false);
    }
  };

  // Save Cover Letter Manually
  const handleSaveCoverLetter = async () => {
    try {
      setSavingCl(true);
      await api.saveCoverLetter(job.id, coverLetterContent);
      onUpdateJob({ ...job, cover_letter: coverLetterContent });
      showTemporarySuccess('Cover letter saved to database!');
    } catch (err) {
      console.error(err);
      alert('Failed to save cover letter.');
    } finally {
      setSavingCl(false);
    }
  };

  // Browser-Based Resume Print
  const handleBrowserResumePrint = () => {
    window.open(`/applications/${job.id}/preview/html?print=true`, '_blank');
  };

  // Download Cover Letter PDF
  const handleDownloadPdf = async () => {
    if (!coverLetterContent.trim()) return;
    try {
      setDownloadingPdf(true);
      const blob = await api.downloadCoverLetterPdf(job.id, coverLetterContent);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cover_Letter_${job.company.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error(err);
      alert('Failed to download cover letter PDF.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleCopyCl = () => {
    if (!coverLetterContent) return;
    navigator.clipboard.writeText(coverLetterContent);
    setCopiedCl(true);
    setTimeout(() => setCopiedCl(false), 2000);
  };

  const showTemporarySuccess = (msg: string) => {
    setSaveSuccessMsg(msg);
    setTimeout(() => setSaveSuccessMsg(''), 4000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 sm:p-6 animate-in fade-in">
      <div className="bg-[#0e1424] border border-white/10 rounded-3xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4.5 border-b border-white/[0.08] bg-[#121829] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shrink-0">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2.5">
              <h2 className="text-base font-bold text-white tracking-tight truncate">
                {job.title}
              </h2>
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800 transition"
                  title="Open original job posting"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
            
            <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1 font-medium">
              <span className="flex items-center text-slate-200 font-semibold">
                <Building className="w-3.5 h-3.5 mr-1 text-slate-500" />
                {job.company}
              </span>
              <span>•</span>
              <span className="flex items-center">
                <MapPin className="w-3.5 h-3.5 mr-1 text-slate-500" />
                {job.location || 'Remote'}
              </span>
              {job.source_platform && (
                <>
                  <span>•</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/[0.06] text-slate-300 border border-white/[0.08]">
                    {job.source_platform}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Quick Header Action Buttons */}
          <div className="flex items-center space-x-2 shrink-0">
            {/* Priority Star Toggle */}
            <button
              onClick={handleTogglePriority}
              className={`p-2 rounded-xl border transition-all flex items-center space-x-1.5 text-xs font-bold ${
                job.is_priority
                  ? 'bg-amber-400/15 border-amber-400/40 text-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.2)]'
                  : 'bg-[#182035] border-white/[0.08] text-slate-400 hover:text-white'
              }`}
              title={job.is_priority ? 'Starred as Priority' : 'Mark as Priority'}
            >
              <Star className={`w-4 h-4 ${job.is_priority ? 'fill-amber-400' : ''}`} />
              <span className="hidden sm:inline">
                {job.is_priority ? 'Priority' : 'Normal'}
              </span>
            </button>

            {/* Status Dropdown */}
            <select
              value={job.status}
              onChange={(e) => handleStatusChange(e.target.value as JobStatus)}
              className="bg-[#182035] border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-bold text-white focus:outline-none focus:border-blue-500 shadow-sm"
            >
              <option value="SAVED">Saved</option>
              <option value="APPLIED">Applied</option>
              <option value="ARCHIVED">Archived</option>
              <option value="NEW">New</option>
              <option value="APPROVED">Approved</option>
            </select>

            {/* Browser Native Print Resume */}
            <button
              onClick={handleBrowserResumePrint}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 border border-white/[0.08] shadow-sm"
              title="Open browser print view to save resume PDF to PC"
            >
              <Printer className="w-3.5 h-3.5 text-blue-400" />
              <span className="hidden md:inline">Print Resume</span>
            </button>

            {/* Resume Studio Action Button */}
            <button
              onClick={() => onOpenResumeStudio(job.id)}
              className="px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-lg shadow-blue-600/25 active:scale-95"
              title="Open full AI Resume Studio"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Resume Studio</span>
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Secondary Navigation: JD vs Cover Letter */}
        <div className="flex items-center justify-between px-6 pt-3 border-b border-white/[0.08] bg-[#0c101d] shrink-0">
          <div className="flex space-x-6">
            <button
              onClick={() => setActiveTab('jd')}
              className={`pb-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition ${
                activeTab === 'jd'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Job Description</span>
            </button>

            <button
              onClick={() => setActiveTab('cover_letter')}
              className={`pb-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition ${
                activeTab === 'cover_letter'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-white'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Cover Letter Generator</span>
              {coverLetterContent && (
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              )}
            </button>
          </div>

          {saveSuccessMsg && (
            <div className="flex items-center text-xs text-emerald-400 font-semibold pb-2 animate-in fade-in">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              {saveSuccessMsg}
            </div>
          )}
        </div>

        {/* Tab 1: Job Description */}
        {activeTab === 'jd' && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col min-h-0 bg-[#080c14]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                {isEditingJd ? 'Editing Job Description' : 'Full Scraped Description'}
              </span>
              <div className="flex items-center space-x-2">
                {isEditingJd ? (
                  <>
                    <button
                      onClick={() => setIsEditingJd(false)}
                      className="px-3 py-1 text-xs text-slate-400 hover:text-white"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveDescription}
                      disabled={savingJd}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-emerald-600/20"
                    >
                      {savingJd ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                      <span>Save Changes</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => {
                      setDescriptionDraft(job.cleaned_description || job.raw_description || '');
                      setIsEditingJd(true);
                    }}
                    className="px-3.5 py-1.5 bg-[#141b2e] hover:bg-[#1a233b] border border-white/[0.08] text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-sm"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-blue-400" />
                    <span>Edit Description</span>
                  </button>
                )}
              </div>
            </div>

            {isEditingJd ? (
              <textarea
                value={descriptionDraft}
                onChange={(e) => setDescriptionDraft(e.target.value)}
                className="w-full flex-1 min-h-[380px] bg-[#121829] border border-slate-700 rounded-2xl p-4 text-xs font-mono text-slate-200 leading-relaxed focus:outline-none focus:border-blue-500 resize-none shadow-inner"
                placeholder="Paste or edit the job description here..."
              />
            ) : (
              <div className="bg-[#101627] border border-white/[0.06] rounded-2xl p-6 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-wrap select-text overflow-y-auto max-h-[58vh] shadow-sm">
                {job.cleaned_description || job.raw_description || (
                  <span className="text-slate-500 italic">No job description available. Click 'Edit Description' to paste or write one.</span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Cover Letter Generator */}
        {activeTab === 'cover_letter' && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col min-h-0 bg-[#080c14]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Tailored Cover Letter
              </span>
              <div className="flex items-center space-x-2">
                {/* Generate / Regenerate */}
                <button
                  onClick={handleGenerateCoverLetter}
                  disabled={generatingCl}
                  className="px-3.5 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm"
                >
                  {generatingCl ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Drafting with AI...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{coverLetterContent ? 'Regenerate' : 'Generate with AI'}</span>
                    </>
                  )}
                </button>

                {/* Copy to clipboard */}
                {coverLetterContent && (
                  <button
                    onClick={handleCopyCl}
                    className="px-3 py-1.5 bg-[#141b2e] hover:bg-[#1a233b] border border-white/[0.08] text-slate-300 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition"
                    title="Copy to clipboard"
                  >
                    {copiedCl ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                    <span>{copiedCl ? 'Copied' : 'Copy'}</span>
                  </button>
                )}

                {/* Save Manually */}
                {coverLetterContent && (
                  <button
                    onClick={handleSaveCoverLetter}
                    disabled={savingCl}
                    className="px-3.5 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition"
                  >
                    {savingCl ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                    <span>Save</span>
                  </button>
                )}

                {/* Download PDF */}
                {coverLetterContent && (
                  <button
                    onClick={handleDownloadPdf}
                    disabled={downloadingPdf}
                    className="px-3.5 py-1.5 bg-[#141b2e] hover:bg-slate-800 border border-white/[0.08] text-slate-200 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-sm"
                  >
                    {downloadingPdf ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <FileDown className="w-3.5 h-3.5 text-blue-400" />
                    )}
                    <span>Download PDF</span>
                  </button>
                )}
              </div>
            </div>

            {/* Textarea for manual override */}
            <div className="flex-1 flex flex-col">
              <textarea
                value={coverLetterContent}
                onChange={(e) => setCoverLetterContent(e.target.value)}
                placeholder="Click 'Generate with AI' to draft a personalized cover letter referencing your Master Profile, or type your own here..."
                className="w-full flex-1 min-h-[380px] bg-[#101627] border border-white/[0.08] rounded-2xl p-5 text-xs text-slate-200 leading-relaxed font-sans focus:outline-none focus:border-blue-500 resize-none shadow-inner select-text"
              />
              <p className="text-[11px] text-slate-500 mt-2">
                * You can edit this text directly at any time. Click 'Save' to persist your changes to the database.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
