import { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { ProfileHeader } from './components/dashboard/ProfileHeader';
import { ScraperBar } from './components/dashboard/ScraperBar';
import { JobListView } from './components/dashboard/JobListView';
import { JobDetailModal } from './components/dashboard/JobDetailModal';
import { ResumeStudio } from './components/builder/ResumeStudio';
import { MasterProfile } from './components/profile/MasterProfile';
import { api } from './api/client';
import type { Job, JobStatus, TailoredResume, UserProfile, ManualJobPayload } from './types';
import { RefreshCw } from 'lucide-react';

function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'profile'>('dashboard');
  const [activeFilterTab, setActiveFilterTab] = useState<'all' | 'priority' | 'saved' | 'applied'>('all');
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  // Job Detail & Action Modal state
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // Resume Studio state
  const [activeTailorJobId, setActiveTailorJobId] = useState<number | null>(null);
  const [tailoredResume, setTailoredResume] = useState<TailoredResume | null>(null);
  const [loadingDraft, setLoadingDraft] = useState(false);

  // Load jobs and profile data
  const loadData = async () => {
    try {
      setLoading(true);
      const [jobsData, profileData] = await Promise.all([
        api.getJobs(),
        api.getProfile().catch(() => null),
      ]);
      setJobs(jobsData);
      setProfile(profileData);
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Priority toggle handler
  const handleTogglePriority = async (jobId: number) => {
    // Optimistic toggle
    setJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, is_priority: !j.is_priority } : j))
    );
    if (selectedJob?.id === jobId) {
      setSelectedJob((prev) => (prev ? { ...prev, is_priority: !prev.is_priority } : null));
    }
    try {
      const res = await api.toggleJobPriority(jobId);
      // Align with server state
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, is_priority: res.is_priority } : j))
      );
    } catch (err) {
      console.error('Failed to toggle priority', err);
      // Revert on failure
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, is_priority: !j.is_priority } : j))
      );
    }
  };

  // Status change handler
  const handleStatusChange = async (jobId: number, status: JobStatus) => {
    setJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, status } : j))
    );
    if (selectedJob?.id === jobId) {
      setSelectedJob((prev) => (prev ? { ...prev, status } : null));
    }
    try {
      await api.updateJobStatus(jobId, status);
    } catch (err) {
      console.error('Failed to update status', err);
      loadData();
    }
  };

  // Scrape URL handler
  const handleScrapeUrl = async (url: string) => {
    try {
      setScraping(true);
      await api.importJob(url);
      // Wait a moment for background task to initialize, then reload
      setTimeout(async () => {
        const updatedJobs = await api.getJobs();
        setJobs(updatedJobs);
        setScraping(false);
      }, 1500);
    } catch (err) {
      console.error('Failed to import job', err);
      alert('Failed to scrape job. You can use "Paste Raw JD" to enter it manually.');
      setScraping(false);
    }
  };

  // Manual job submit handler
  const handleManualSubmit = async (payload: ManualJobPayload) => {
    try {
      setScraping(true);
      await api.createManualJob(payload);
      const updatedJobs = await api.getJobs();
      setJobs(updatedJobs);
    } catch (err) {
      console.error('Failed to create manual job', err);
      throw err;
    } finally {
      setScraping(false);
    }
  };

  // Open Resume Studio from Modal
  const handleOpenResumeStudio = async (jobId: number) => {
    setIsDetailModalOpen(false);
    setActiveTailorJobId(jobId);
    setLoadingDraft(true);
    try {
      const draft = await api.getTailoredDraft(jobId);
      setTailoredResume(draft);
    } catch (err) {
      console.error('Failed to load draft for Resume Studio', err);
      alert('Failed to load tailored draft for this job.');
      setActiveTailorJobId(null);
    } finally {
      setLoadingDraft(false);
    }
  };

  // Update single job in state (e.g. after JD edit or cover letter save)
  const handleUpdateJob = (updatedJob: Job) => {
    setJobs((prev) => prev.map((j) => (j.id === updatedJob.id ? updatedJob : j)));
    if (selectedJob?.id === updatedJob.id) {
      setSelectedJob(updatedJob);
    }
  };

  // Open modal for a selected job
  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
    setIsDetailModalOpen(true);
  };

  // If in Resume Studio view
  if (activeTailorJobId !== null) {
    if (loadingDraft || !tailoredResume) {
      return (
        <div className="w-screen h-screen flex flex-col items-center justify-center bg-[#0B0F19] text-white space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <p className="text-sm font-bold text-neutral-300">
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

  // Live count computations
  const totalJobs = jobs.length;
  const priorityJobs = jobs.filter((j) => j.is_priority).length;
  const savedJobs = jobs.filter(
    (j) => j.status === 'SAVED' || j.status === 'NEW' || j.status === 'APPROVED'
  ).length;

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0F19]">
      {/* Top Navbar */}
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
      />

      <main className="flex-1 flex flex-col overflow-hidden relative">
        {currentTab === 'dashboard' && (
          <>
            {/* 1. Profile Overview Header */}
            <ProfileHeader
              profile={profile}
              totalJobs={totalJobs}
              priorityJobs={priorityJobs}
              savedJobs={savedJobs}
              activeTab={activeFilterTab}
              onTabSelect={setActiveFilterTab}
            />

            {/* 2. Sticky Scraper & Manual Ingestion Bar */}
            <ScraperBar
              onScrapeUrl={handleScrapeUrl}
              onManualSubmit={handleManualSubmit}
              loading={scraping}
            />

            {/* 3. High-Density Interactive Job List */}
            {loading ? (
              <div className="flex-1 flex items-center justify-center">
                <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : (
              <JobListView
                jobs={jobs}
                activeTab={activeFilterTab}
                onTabSelect={setActiveFilterTab}
                onSelectJob={handleSelectJob}
                onTogglePriority={handleTogglePriority}
                onStatusChange={handleStatusChange}
              />
            )}

            {/* 4. Comprehensive Job Action & Detail Modal */}
            <JobDetailModal
              job={selectedJob}
              isOpen={isDetailModalOpen}
              onClose={() => setIsDetailModalOpen(false)}
              onUpdateJob={handleUpdateJob}
              onOpenResumeStudio={handleOpenResumeStudio}
            />
          </>
        )}

        {currentTab === 'profile' && <MasterProfile />}
      </main>
    </div>
  );
}

export default App;
