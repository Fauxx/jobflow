import type { Job, JobStatus, UserProfile } from '../types';

export const api = {
  // Jobs
  async getJobs(): Promise<Job[]> {
    const res = await fetch('/jobs');
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },

  async updateJobStatus(jobId: number, status: JobStatus): Promise<{ status: string }> {
    const res = await fetch(`/jobs/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update job status');
    return res.json();
  },

  async importJob(url: string): Promise<Job> {
    const res = await fetch('/scraper/import-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error('Failed to import job');
    return res.json();
  },

  // Profile
  async getProfile(): Promise<UserProfile> {
    const res = await fetch('/profile');
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(profileData: Partial<UserProfile>): Promise<{ status: string }> {
    const res = await fetch('/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    });
    if (!res.ok) throw new Error('Failed to save profile');
    return res.json();
  },

  // Resume Tailoring
  async getTailoredDraft(jobId: number) {
    const res = await fetch(`/resumes/builder/${jobId}/draft`);
    if (!res.ok) throw new Error('Failed to fetch draft');
    return res.json();
  },

  async adjustSectionWithAI(jobId: number, payload: {
    section_type: string;
    section_name: string;
    instruction: string;
    current_bullets: any[];
  }) {
    const res = await fetch(`/resumes/builder/${jobId}/adjust-section`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to adjust section with AI');
    return res.json();
  },
};
