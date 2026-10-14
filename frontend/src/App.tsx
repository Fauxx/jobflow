import { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { KanbanBoard } from './components/kanban/KanbanBoard';
import { TriageDrawer } from './components/kanban/TriageDrawer';
import { ResumeStudio } from './components/builder/ResumeStudio';
import { MasterProfile } from './components/profile/MasterProfile';
import { api } from './api/client';
import type { Job, JobStatus, TailoredResume } from './types';
import { X, RefreshCw } from 'lucide-react';

function App() {
  const [currentTab, setCurrentTab] = useState<'pipeline' | 'profile' | 'analytics'>('pipeline');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isTriageOpen, setIsTriageOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  // Resume Studio state
  const [activeTailorJobId, setActiveTailorJobId] = useState<number | null>(null);
  const [tailoredResume, setTailoredResume] = useState<TailoredResume | null>(null);
  const [loadingDraft, setLoadingDraft] = useState(false);

  // Import Job Modal state
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);

  // Load jobs from FastAPI backend
  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await api.getJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJob) {
        setSelectedJob(data[0]);
      }
    } catch (err) {
      console.error('Failed to load jobs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleStatusChange = async (jobId: number, status: JobStatus) => {
    try {
      // Optimistic update
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, status } : j))
      );
      if (selectedJob?.id === jobId) {
        setSelectedJob((prev) => (prev ? { ...prev, status } : null));
      }
      await api.updateJobStatus(jobId, status);
    } catch (err) {
      console.error(err);
      loadJobs();
    }
  };

  const handleStartTailoring = async (jobId: number) => {
    setActiveTailorJobId(jobId);
    setLoadingDraft(true);
    try {
      const draft = await api.getTailoredDraft(jobId);
      setTailoredResume(draft);
    } catch (err) {
      console.error(err);
      alert('Failed to load tailored draft for this job.');
      setActiveTailorJobId(null);
    } finally {
      setLoadingDraft(false);
    }
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importUrl.trim()) return;
    setImporting(true);
    try {
      const newJob = await api.importJob(importUrl);
      setJobs((prev) => [newJob, ...prev]);
      setSelectedJob(newJob);
      setIsImportModalOpen(false);
      setImportUrl('');
    } catch (err) {
      console.error(err);
      alert('Failed to import job from URL.');
    } finally {
      setImporting(false);
    }
  };

  // If in Resume Studio view
  if (activeTailorJobId !== null) {
    if (loadingDraft || !tailoredResume) {
      return (
        <div className="w-screen h-screen flex flex-col items-center justify-center bg-[#0B0F19] text-white space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <p className="text-sm font-bold text-gray-300">
            Generating fact-anchored resume draft with AI...
          </p>
        </div>
      );
    }

    return (
      <ResumeStudio
        jobId={activeTailorJobId}
        initialResume={tailoredResume}
        onBack={() => setActiveTailorJobId(null)}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0F19]">
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        onToggleTriage={() => setIsTriageOpen((prev) => !prev)}
        onImportClick={() => setIsImportModalOpen(true)}
      />

      <main className="flex-1 flex overflow-hidden relative">
        {currentTab === 'pipeline' && (
          <>
            {loading ? (
              <div className="flex-1 flex items-center justify-center">
                <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : (
              <KanbanBoard
                jobs={jobs}
                onSelectJob={(j) => {
                  setSelectedJob(j);
                  setIsTriageOpen(true);
                }}
                onStatusChange={handleStatusChange}
                onTailor={handleStartTailoring}
              />
            )}

            <TriageDrawer
              job={selectedJob}
              isOpen={isTriageOpen}
              onClose={() => setIsTriageOpen(false)}
              onStatusChange={handleStatusChange}
              onTailor={handleStartTailoring}
            />
          </>
        )}

        {currentTab === 'profile' && <MasterProfile />}

        {currentTab === 'analytics' && (
          <div className="flex-1 p-8 text-center text-gray-400 bg-[#0B0F19]">
            <h2 className="text-xl font-bold text-white mb-2">Analytics & Velocity</h2>
            <p className="text-sm">
              Live funnel conversion metrics, platform breakdown, and application status trends.
            </p>
          </div>
        )}
      </main>

      {/* Import Job Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
            <button
              onClick={() => setIsImportModalOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-lg font-bold text-white mb-2">Import Job from URL</h3>
            <p className="text-xs text-gray-400 mb-4">
              Paste a URL from LinkedIn, Kalibrr, or SEEK to automatically scrape and analyze it.
            </p>
            <form onSubmit={handleImportSubmit} className="space-y-4">
              <input
                type="url"
                required
                value={importUrl}
                onChange={(e) => setImportUrl(e.target.value)}
                placeholder="https://www.linkedin.com/jobs/view/..."
                className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
              />
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsImportModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold text-gray-400 hover:text-white rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={importing}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5"
                >
                  {importing && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  {importing ? 'Scraping...' : 'Import'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
