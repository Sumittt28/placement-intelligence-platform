import axios from "axios";
import type { APIResponse } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ============ Auth ============
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string; kalvium_id?: string; batch?: string; graduation_year?: number }) =>
    api.post<APIResponse>("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post<APIResponse>("/auth/login", data),
  googleAuth: (data: { access_token: string }) =>
    api.post<APIResponse>("/auth/google", data),
};

// ============ Users ============
export const userAPI = {
  getMe: () => api.get<APIResponse>("/users/me"),
  updateProfile: (data: Record<string, unknown>) => api.put<APIResponse>("/users/me/profile", data),
};

// ============ Dashboard ============
export const dashboardAPI = {
  get: () => api.get<APIResponse>("/dashboard"),
};

// ============ Companies ============
export const companyAPI = {
  list: (search?: string) => api.get<APIResponse>("/companies", { params: { search } }),
  get: (id: string) => api.get<APIResponse>(`/companies/${id}`),
  create: (data: { name: string; industry?: string; website?: string }) => api.post<APIResponse>("/companies", data),
  update: (id: string, data: Record<string, unknown>) => api.put<APIResponse>(`/companies/${id}`, data),
};

// ============ Experiences ============
export const experienceAPI = {
  create: (data: Record<string, unknown>) => api.post<APIResponse>("/experiences", data),
  list: (page = 1, limit = 20) => api.get<APIResponse>("/experiences", { params: { page, limit } }),
  get: (id: string) => api.get<APIResponse>(`/experiences/${id}`),
  delete: (id: string) => api.delete<APIResponse>(`/experiences/${id}`),
};

// ============ Mock Interviews ============
export const interviewAPI = {
  start: (data: { interview_type: string; difficulty: string; company_id?: string; mode?: string }) =>
    api.post<APIResponse>("/interviews/start", data),
  answer: (id: string, data: { answer: string; audio_url?: string }) =>
    api.post<APIResponse>(`/interviews/${id}/answer`, data),
  complete: (id: string) => api.post<APIResponse>(`/interviews/${id}/complete`),
  list: () => api.get<APIResponse>("/interviews"),
  get: (id: string) => api.get<APIResponse>(`/interviews/${id}`),
  replay: (id: string) => api.get<APIResponse>(`/interviews/${id}/replay`),
};

// ============ Evaluations ============
export const evaluationAPI = {
  get: (interviewId: string) => api.get<APIResponse>(`/evaluations/${interviewId}`),
};

// ============ Resume ============
export const resumeAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<APIResponse>("/resume/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  insights: () => api.get<APIResponse>("/resume/insights"),
  data: () => api.get<APIResponse>("/resume/data"),
};

// ============ Intelligence ============
export const weaknessAPI = {
  list: () => api.get<APIResponse>("/weaknesses"),
  resolve: (id: string) => api.put<APIResponse>(`/weaknesses/${id}/resolve`),
};

export const recommendationAPI = {
  list: () => api.get<APIResponse>("/recommendations"),
  complete: (id: string) => api.put<APIResponse>(`/recommendations/${id}/complete`),
};

export const readinessAPI = {
  overall: () => api.get<APIResponse>("/readiness"),
  company: (id: string) => api.get<APIResponse>(`/readiness/${id}`),
};

export const searchAPI = {
  search: (params: { q: string; type?: string; company?: string; round_type?: string; difficulty?: string; page?: number }) =>
    api.get<APIResponse>("/search", { params }),
};

// ============ Voice ============
export const voiceAPI = {
  transcribe: (file: Blob) => {
    const formData = new FormData();
    formData.append("file", file, "audio.wav");
    return api.post<APIResponse>("/voice/transcribe", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  synthesize: (text: string) => api.post<APIResponse>("/voice/synthesize", { text }),
};

// ============ Admin ============
export const adminAPI = {
  listExperiences: (status?: string) => api.get<APIResponse>("/admin/experiences", { params: { status } }),
  approve: (id: string) => api.put<APIResponse>(`/admin/experiences/${id}/approve`),
  flag: (id: string, reason: string) => api.put<APIResponse>(`/admin/experiences/${id}/flag`, { reason }),
  analytics: () => api.get<APIResponse>("/admin/analytics"),
};

export default api;
