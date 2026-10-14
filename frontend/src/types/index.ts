export type JobStatus = 'SAVED' | 'APPLIED' | 'ARCHIVED' | 'NEW' | 'APPROVED' | 'SKIPPED';

export interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  url?: string;
  source_platform?: string;
  source_job_id?: string;
  description?: string;
  raw_description?: string;
  cleaned_description?: string;
  salary_min?: number;
  salary_max?: number;
  currency?: string;
  is_remote?: boolean;
  status: JobStatus;
  is_priority?: boolean;
  cover_letter?: string;
  fit_score?: number;
  fit_reason?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ManualJobPayload {
  title: string;
  company: string;
  location?: string;
  description: string;
  source_url?: string;
}

export interface ProfileBullet {
  id: string;
  text: string;
  order: number;
}

export interface ProfileProject {
  id: number;
  name: string;
  role?: string;
  date_range?: string;
  tech_stack?: string;
  url?: string;
  detailed_context?: string;
  order: number;
  bullets: ProfileBullet[];
}

export interface ProfileExperience {
  id: number;
  company: string;
  title?: string;
  location?: string;
  date_range?: string;
  detailed_context?: string;
  order: number;
  bullets: ProfileBullet[];
}

export interface ProfileSkill {
  id: number;
  category: string;
  name: string;
}

export interface UserProfile {
  id: number;
  name: string;
  headline?: string;
  summary?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  skills: ProfileSkill[];
  projects: ProfileProject[];
  experiences: ProfileExperience[];
  education: Array<{
    id: number;
    institution: string;
    degree: string;
    date_str?: string;
    location?: string;
  }>;
}

export interface TailoredBullet {
  id: string;
  original_text: string;
  tailored_text: string;
  highly_recommended: boolean;
  reason?: string;
}

export interface TailoredSection {
  company?: string;
  name?: string;
  title?: string;
  role?: string;
  location?: string;
  date_range?: string;
  tech_stack?: string;
  bullets: TailoredBullet[];
}

export interface TailoredResume {
  summary: string;
  skills: string[];
  experiences: TailoredSection[];
  projects: TailoredSection[];
  matched_skills?: string[];
  missing_skills?: string[];
}
