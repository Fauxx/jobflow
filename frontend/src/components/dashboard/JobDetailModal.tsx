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
  FileDown,
  FileText,
  MapPin,
  Building,
  Loader2,
  CheckCircle2,
  Layers,
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

  const showTemporarySuccess = (msg: string) => {
    setSaveSuccessMsg(msg);
    setTimeout(() => setSaveSuccessMsg(''), 4000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 sm:p-6">
      <div className="bg-[#111625] border border-neutral-800 rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-neutral-800 bg-[#141b2d] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3">
              <h2 className="text-lg font-bold text-white tracking-tight truncate">
                {job.title}
              </h2>
              {/* External Posting Link */}
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1 rounded text-neutral-400 hover:text-blue-400 transition"
                  title="Open original job posting"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
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
              {job.source_platform && (
                <>
                  <span>•</span>
                  <span className="px-2 py-0.5 rounded bg-neutral-800 text-neutral-300 text-[10px] font-mono">
                    {job.source_platform}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Quick Header Controls */}
          <div className="flex items-center space-x-2 shrink-0">
            {/* Priority Toggle */}
            <button
              onClick={handleTogglePriority}
              className={`p-2 rounded-xl border transition flex items-center space-x-1.5 text-xs font-semibold ${
                job.is_priority
                  ? 'bg-amber-500/20 border-amber-500/50 text-amber-400'
                  : 'bg-[#182032] border-neutral-700/60 text-neutral-400 hover:text-white'
              }`}
              title={job.is_priority ? 'Remove from Priority' : 'Mark as Priority'}
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
              className="bg-[#182032] border border-neutral-700/60 rounded-xl px-3 py-1.5 text-xs font-semibold text-white focus:outline-none focus:border-blue-500"
            >
              <option value="SAVED">Saved</option>
              <option value="APPLIED">Applied</option>
              <option value="ARCHIVED">Archived</option>
              <option value="NEW">New</option>
              <option value="APPROVED">Approved</option>
            </select>

            {/* Resume Studio Action Button */}
            <button
              onClick={() => onOpenResumeStudio(job.id)}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm shadow-blue-500/20"
              title="Open fact-anchored AI resume tailor"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Resume Tailor</span>
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl text-neutral-400 hover:text-white hover:bg-neutral-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Secondary Navigation: JD vs Cover Letter */}
        <div className="flex items-center justify-between px-6 pt-3 border-b border-neutral-800 bg-[#0e1320]">
          <div className="flex space-x-6">
            <button
              onClick={() => setActiveTab('jd')}
              className={`pb-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition ${
                activeTab === 'jd'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-neutral-400 hover:text-white'
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
                  : 'border-transparent text-neutral-400 hover:text-white'
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
            <div className="flex items-center text-xs text-emerald-400 font-medium pb-2 animate-in fade-in">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              {saveSuccessMsg}
            </div>
          )}
        </div>

        {/* Tab 1: Job Description */}
        {activeTab === 'jd' && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col min-h-0 bg-[#0B0F19]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">
                {isEditingJd ? 'Editing Job Description' : 'Full Scraped Description'}
              </span>
              <div className="flex items-center space-x-2">
                {isEditingJd ? (
                  <>
                    <button
                      onClick={() => setIsEditingJd(false)}
                      className="px-3 py-1 text-xs text-neutral-400 hover:text-white"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveDescription}
                      disabled={savingJd}
                      className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center space-x-1"
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
                    className="px-3 py-1 bg-[#182032] hover:bg-neutral-800 border border-neutral-700 text-neutral-300 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition"
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
                className="w-full flex-1 min-h-[350px] bg-[#141b2d] border border-neutral-700 rounded-xl p-4 text-xs font-mono text-neutral-200 leading-relaxed focus:outline-none focus:border-blue-500 resize-none"
                placeholder="Paste or edit the job description here..."
              />
            ) : (
              <div className="bg-[#141b2d] border border-neutral-800/80 rounded-xl p-5 text-sm text-neutral-300 leading-relaxed font-sans whitespace-pre-wrap select-text overflow-y-auto max-h-[55vh]">
                {job.cleaned_description || job.raw_description || (
                  <span className="text-neutral-500 italic">No job description available. Click 'Edit Description' to add one.</span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Cover Letter Generator */}
        {activeTab === 'cover_letter' && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col min-h-0 bg-[#0B0F19]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">
                Tailored Cover Letter
              </span>
              <div className="flex items-center space-x-2">
                {/* Generate / Regenerate */}
                <button
                  onClick={handleGenerateCoverLetter}
                  disabled={generatingCl}
                  className="px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-400 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition"
                >
                  {generatingCl ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Writing with AI...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{coverLetterContent ? 'Regenerate' : 'Generate with AI'}</span>
                    </>
                  )}
                </button>

                {/* Save Manually */}
                {coverLetterContent && (
                  <button
                    onClick={handleSaveCoverLetter}
                    disabled={savingCl}
                    className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-400 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition"
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
                    className="px-3 py-1.5 bg-[#182032] hover:bg-neutral-800 border border-neutral-700 text-neutral-300 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition"
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
                className="w-full flex-1 min-h-[350px] bg-[#141b2d] border border-neutral-700/80 rounded-xl p-5 text-sm text-neutral-200 leading-relaxed font-sans focus:outline-none focus:border-blue-500 resize-none shadow-inner"
              />
              <p className="text-[11px] text-neutral-500 mt-2">
                * You can edit this text directly at any time. Click 'Save' to persist your manual changes to the database.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
