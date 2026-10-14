import type { Job, JobStatus, UserProfile } from '../types';

export const api = {
  // Jobs
  async getJobs(): Promise<Job[]> {
    const res = await fetch('/jobs', {
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },

  async updateJobStatus(jobId: number, status: JobStatus): Promise<{ status: string }> {
    const res = await fetch(`/jobs/${jobId}/status`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update job status');
    return res.json();
  },

  async toggleJobPriority(jobId: number): Promise<{ status: string; is_priority: boolean }> {
    const res = await fetch(`/jobs/${jobId}/priority`, {
      method: 'POST',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to toggle priority');
    return res.json();
  },

  async updateJob(jobId: number, data: Partial<Job>): Promise<{ status: string }> {
    const res = await fetch(`/jobs/${jobId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update job');
    return res.json();
  },

  async createManualJob(payload: { title: string; company: string; location?: string; description: string; source_url?: string }): Promise<{ status: string; id: number }> {
    const res = await fetch('/jobs', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to save manual job');
    return res.json();
  },

  async importJob(url: string): Promise<{ status: string; job_id?: number }> {
    const res = await fetch('/scrape/import-url', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error('Failed to import job');
    return res.json();
  },

  // Cover Letter
  async generateCoverLetter(jobId: number): Promise<{ draft: string }> {
    const res = await fetch(`/applications/${jobId}/generate-cover-letter`, {
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to generate cover letter');
    return res.json();
  },

  async saveCoverLetter(jobId: number, content: string): Promise<{ status: string }> {
    const res = await fetch(`/applications/${jobId}/cover-letter`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error('Failed to save cover letter');
    return res.json();
  },

  async downloadCoverLetterPdf(jobId: number, content: string): Promise<Blob> {
    const res = await fetch(`/applications/${jobId}/cover-letter/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error('Failed to download cover letter PDF');
    return res.blob();
  },

  // Profile
  async getProfile(): Promise<UserProfile> {
    const res = await fetch('/profile', {
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(profileData: Partial<UserProfile>): Promise<{ status: string }> {
    const res = await fetch('/profile', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(profileData),
    });
    if (!res.ok) throw new Error('Failed to save profile');
    return res.json();
  },

  // Resume Tailoring
  async getTailoredDraft(jobId: number) {
    const res = await fetch(`/resume/builder/${jobId}/draft`, {
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to fetch draft');
    return res.json();
  },

  async adjustSectionWithAI(jobId: number, payload: {
    section_type: string;
    section_name: string;
    instruction: string;
    current_bullets: any[];
  }) {
    const res = await fetch(`/resume/builder/${jobId}/adjust-section`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to adjust section with AI');
    return res.json();
  },
};
