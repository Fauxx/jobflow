import React, { useState } from 'react';
import { Link2, Sparkles, FileText, Loader2, X, Plus } from 'lucide-react';
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
    <div className="bg-[#0e1320] border-b border-neutral-800/80 px-6 py-3.5 sticky top-0 z-20 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center gap-3">
        {/* URL Scraper Input */}
        <form onSubmit={handleUrlSubmit} className="flex-1 flex items-center w-full relative">
          <div className="absolute left-3.5 text-neutral-500 pointer-events-none">
            <Link2 className="w-4 h-4" />
          </div>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste job link (LinkedIn, Indeed, JobStreet, Kalibrr, or any website)..."
            disabled={loading}
            className="w-full bg-[#182032] border border-neutral-700/60 rounded-xl pl-10 pr-36 py-2.5 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="absolute right-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-800 disabled:text-neutral-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition shadow-sm"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Scraping...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Scrape & Import</span>
              </>
            )}
          </button>
        </form>

        {/* Manual Paste Trigger Button */}
        <button
          type="button"
          onClick={() => setIsManualModalOpen(true)}
          className="shrink-0 px-3.5 py-2.5 bg-[#182032] hover:bg-neutral-800 border border-neutral-700/60 text-neutral-300 hover:text-white rounded-xl text-xs font-medium flex items-center space-x-2 transition"
          title="Paste Job Description manually if scraping is blocked"
        >
          <FileText className="w-4 h-4 text-blue-400" />
          <span>Paste Raw JD</span>
        </button>
      </div>

      {/* Manual Paste Modal */}
      {isManualModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#111625] border border-neutral-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Manual Job Ingestion</h3>
              </div>
              <button
                onClick={() => setIsManualModalOpen(false)}
                className="p-1 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleManualFormSubmit} className="p-6 space-y-4 overflow-y-auto flex-1">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={manualTitle}
                    onChange={(e) => setManualTitle(e.target.value)}
                    placeholder="e.g. Senior DevOps Engineer"
                    className="w-full bg-[#182032] border border-neutral-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={manualCompany}
                    onChange={(e) => setManualCompany(e.target.value)}
                    placeholder="e.g. Acme Corp"
                    className="w-full bg-[#182032] border border-neutral-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Location
                  </label>
                  <input
                    type="text"
                    value={manualLocation}
                    onChange={(e) => setManualLocation(e.target.value)}
                    placeholder="e.g. Remote / Manila, PH"
                    className="w-full bg-[#182032] border border-neutral-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Job URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={manualSourceUrl}
                    onChange={(e) => setManualSourceUrl(e.target.value)}
                    placeholder="https://..."
                    className="w-full bg-[#182032] border border-neutral-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-400 mb-1.5">
                  Raw Job Description *
                </label>
                <textarea
                  required
                  rows={8}
                  value={manualDescription}
                  onChange={(e) => setManualDescription(e.target.value)}
                  placeholder="Paste the full job requirements, description, and responsibilities here..."
                  className="w-full bg-[#182032] border border-neutral-700 rounded-xl p-3.5 text-sm text-white focus:outline-none focus:border-blue-500 font-mono text-xs leading-relaxed"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-neutral-800">
                <button
                  type="button"
                  onClick={() => setIsManualModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-neutral-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingManual}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition flex items-center space-x-2"
                >
                  {submittingManual ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Save to Jobflow</span>
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
