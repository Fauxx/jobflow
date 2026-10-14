import React, { useState } from 'react';
import { Link2, Sparkles, FileText, Loader2, X, Plus, CornerDownLeft } from 'lucide-react';
import type { ManualJobPayload } from '../../types';

interface ScraperBarProps {
  onScrapeUrl: (url: string) => Promise<void>;
  onManualSubmit: (payload: ManualJobPayload) => Promise<void>;
  loading: boolean;
}

export const ScraperBar: React.FC<ScraperBarProps> = ({
  onScrapeUrl,
  onManualSubmit,
  loading,
}) => {
  const [url, setUrl] = useState('');
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);

  // Manual Form State
  const [manualTitle, setManualTitle] = useState('');
  const [manualCompany, setManualCompany] = useState('');
  const [manualLocation, setManualLocation] = useState('Remote');
  const [manualSourceUrl, setManualSourceUrl] = useState('');
  const [manualDescription, setManualDescription] = useState('');
  const [submittingManual, setSubmittingManual] = useState(false);

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    await onScrapeUrl(url.trim());
    setUrl('');
  };

  const handleManualFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualTitle.trim() || !manualCompany.trim() || !manualDescription.trim()) {
      alert('Please fill in Title, Company, and Job Description.');
      return;
    }

    try {
      setSubmittingManual(true);
      await onManualSubmit({
        title: manualTitle.trim(),
        company: manualCompany.trim(),
        location: manualLocation.trim() || 'Remote',
        source_url: manualSourceUrl.trim() || '',
        description: manualDescription.trim(),
      });
      // Reset form
      setManualTitle('');
      setManualCompany('');
      setManualLocation('Remote');
      setManualSourceUrl('');
      setManualDescription('');
      setIsManualModalOpen(false);
    } catch (err) {
      console.error(err);
      alert('Failed to save manual job.');
    } finally {
      setSubmittingManual(false);
    }
  };

  return (
    <div className="bg-[#0a0e19]/95 border-b border-white/[0.08] px-6 py-4 sticky top-0 z-20 backdrop-blur-xl shadow-lg shadow-black/20">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center gap-3.5">
        
        {/* URL Scraper Input Bar (Command Bar Style) */}
        <form
          onSubmit={handleUrlSubmit}
          className="flex-1 flex items-center w-full relative bg-[#121829] border border-white/[0.1] rounded-2xl p-1.5 focus-within:border-blue-500/80 focus-within:ring-4 focus-within:ring-blue-500/15 transition-all shadow-inner"
        >
          <div className="pl-3 pr-2 text-slate-400 pointer-events-none">
            <Link2 className="w-4 h-4 text-blue-400" />
          </div>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste job URL from LinkedIn, Indeed, JobStreet, Kalibrr, or any career portal..."
            disabled={loading}
            className="w-full bg-transparent border-none py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none disabled:opacity-50 font-sans"
          />

          <div className="flex items-center gap-2 pr-1 shrink-0">
            {url.trim() && !loading && (
              <span className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-white/10 text-slate-300">
                <CornerDownLeft className="w-2.5 h-2.5 mr-0.5" /> Enter
              </span>
            )}
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition shadow-md shadow-blue-600/25 active:scale-95"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Ingesting...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-blue-200" />
                  <span>Scrape & Import</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Manual Paste Action Pill */}
        <button
          type="button"
          onClick={() => setIsManualModalOpen(true)}
          className="shrink-0 px-4 py-3 bg-[#121829] hover:bg-[#182035] border border-white/[0.08] hover:border-white/20 text-slate-300 hover:text-white rounded-2xl text-xs font-semibold flex items-center space-x-2 transition shadow-sm active:scale-95"
          title="Paste Job Description manually if scraping is blocked"
        >
          <FileText className="w-4 h-4 text-blue-400" />
          <span>Paste Raw JD</span>
        </button>
      </div>

      {/* Manual Paste Modal */}
      {isManualModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
          <div className="bg-[#0e1424] border border-white/10 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4.5 border-b border-white/[0.08] bg-[#121829]">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-blue-500/15 text-blue-400">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Manual Job Ingestion</h3>
                  <p className="text-[11px] text-slate-400">Paste job requirements directly into Jobflow</p>
                </div>
              </div>
              <button
                onClick={() => setIsManualModalOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleManualFormSubmit} className="p-6 space-y-4.5 overflow-y-auto flex-1">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={manualTitle}
                    onChange={(e) => setManualTitle(e.target.value)}
                    placeholder="e.g. Senior DevOps Engineer"
                    className="w-full bg-[#141b2e] border border-slate-700/60 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={manualCompany}
                    onChange={(e) => setManualCompany(e.target.value)}
                    placeholder="e.g. Acme Corp"
                    className="w-full bg-[#141b2e] border border-slate-700/60 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Location
                  </label>
                  <input
                    type="text"
                    value={manualLocation}
                    onChange={(e) => setManualLocation(e.target.value)}
                    placeholder="e.g. Remote / Manila, PH"
                    className="w-full bg-[#141b2e] border border-slate-700/60 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Job URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={manualSourceUrl}
                    onChange={(e) => setManualSourceUrl(e.target.value)}
                    placeholder="https://..."
                    className="w-full bg-[#141b2e] border border-slate-700/60 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Raw Job Description *
                </label>
                <textarea
                  required
                  rows={9}
                  value={manualDescription}
                  onChange={(e) => setManualDescription(e.target.value)}
                  placeholder="Paste the full job requirements, description, and responsibilities here..."
                  className="w-full bg-[#141b2e] border border-slate-700/60 rounded-xl p-4 text-xs text-white focus:outline-none focus:border-blue-500 font-mono text-[11px] leading-relaxed resize-none shadow-inner"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsManualModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingManual}
                  className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center space-x-2 shadow-lg shadow-blue-600/25 active:scale-95"
                >
                  {submittingManual ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Save Opportunity</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
