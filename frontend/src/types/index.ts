// ============ API Response ============
export interface APIResponse<T = unknown> {
  success: boolean;
  data: T;
  error: string | null;
}

// ============ Auth ============
export interface UserBrief {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserBrief;
}

// ============ Profile ============
export interface Profile {
  id: string;
  user_id: string;
  full_name: string;
  kalvium_id?: string;
  batch?: string;
  graduation_year?: number;
  resume_url?: string;
  linkedin_url?: string;
  github_url?: string;
  target_companies?: string[];
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  auth_provider: string;
  is_active: boolean;
  created_at: string;
  profile: Profile | null;
}

// ============ Company ============
export interface Company {
  id: string;
  name: string;
  industry?: string;
  website?: string;
  logo_url?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export interface CompanyAnalytics {
  total_experiences: number;
  total_questions: number;
  top_topics: { topic: string; count: number }[];
  difficulty_dist: Record<string, number>;
  round_dist: Record<string, number>;
  success_rate: number;
  common_weaknesses: string[];
  last_computed?: string;
}

export interface CompanyIntelligence {
  company: Company;
  analytics: CompanyAnalytics;
  recent_experiences: ExperienceBrief[];
  frequently_asked_questions: { question: string; topic: string; frequency: number }[];
  questions_by_round: Record<string, { question: string; topic: string }[]>;
}

// ============ Interview Experience ============
export interface InterviewQuestion {
  id: string;
  topic: string;
  question_text: string;
  could_answer: string;
  ai_tags?: Record<string, unknown>;
  created_at: string;
}

export interface InterviewExperience {
  id: string;
  user_id: string;
  company_id: string;
  company_name?: string;
  role: string;
  interview_date: string;
  round_type: string;
  difficulty: string;
  outcome: string;
  student_notes?: string;
  ai_extracted?: Record<string, unknown>;
  is_approved: boolean;
  questions: InterviewQuestion[];
  created_at: string;
}

export interface ExperienceBrief {
  id: string;
  role: string;
  round_type: string;
  difficulty: string;
  outcome: string;
  interview_date: string;
}

// ============ Mock Interview ============
export interface MockInterviewQuestion {
  id: string;
  sequence_num: number;
  question_text: string;
  question_type?: string;
  topic?: string;
}

export interface MockInterview {
  id: string;
  interview_type: string;
  difficulty: string;
  mode: string;
  status: string;
  company_id?: string;
  started_at: string;
  completed_at?: string;
  questions?: MockInterviewQuestion[];
}

export interface ReplayQuestion {
  id: string;
  sequence_num: number;
  question_text: string;
  question_type?: string;
  topic?: string;
  student_answer?: string;
  ideal_answer?: string;
  evaluation?: Record<string, unknown>;
  feedback?: string;
  audio_url?: string;
}

// ============ Evaluation ============
export interface ScoreDimension {
  score: number;
  reason: string;
}

export interface Evaluation {
  id: string;
  interview_id: string;
  communication: ScoreDimension;
  technical: ScoreDimension;
  confidence: ScoreDimension;
  problem_solving: ScoreDimension;
  behavioral: ScoreDimension;
  project: ScoreDimension;
  overall_score: number;
  overall_feedback: string;
  strengths: string[];
  improvements: string[];
  created_at: string;
}

// ============ Intelligence ============
export interface Weakness {
  id: string;
  topic: string;
  category?: string;
  occurrence_count: number;
  severity?: string;
  sources: string[];
  recommended_actions: string[];
  is_resolved: boolean;
  first_detected: string;
  last_detected: string;
}

export interface Recommendation {
  id: string;
  type: string;
  title: string;
  description?: string;
  priority: number;
  is_completed: boolean;
  created_at: string;
}

export interface ReadinessDimension {
  name: string;
  score: number;
  gap: string;
}

export interface CompanyReadiness {
  company_id: string;
  company_name: string;
  readiness_percent: number;
  dimensions: ReadinessDimension[];
  recommendations: string[];
}

export interface ResumeInsights {
  skills: string[];
  projects: { name: string; description: string; technologies: string[] }[];
  experience: { title: string; company: string; duration: string }[];
  technologies: string[];
  domains: string[];
  insights: {
    missing_skills?: string[];
    strength_areas?: string[];
    potential_interview_topics?: string[];
  };
  parsed_at?: string;
}

// ============ Dashboard ============
export interface DashboardData {
  profile_summary: {
    full_name: string;
    batch?: string;
    resume_status: string;
    target_companies: string;
  };
  stats: {
    interviews_attempted: number;
    ai_interviews_completed: number;
    contributions_submitted: number;
    company_reports_viewed: number;
  };
  recent_activity: {
    action: string;
    resource?: string;
    resource_id?: string;
    created_at: string;
  }[];
  performance: {
    communication: number;
    technical_depth: number;
    problem_solving: number;
    behavioral: number;
    project_discussions: number;
  };
  trends: {
    date: string;
    scores: {
      communication: number;
      technical_depth: number;
      problem_solving: number;
      behavioral: number;
      project_discussions: number;
    };
  }[];
}

// ============ Search ============
export interface SearchResult {
  question_text: string;
  topic: string;
  company_name: string;
  round_type: string;
  difficulty: string;
  frequency: number;
}
