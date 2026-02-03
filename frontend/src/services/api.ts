import axios, { AxiosError } from 'axios';
import { Token, User, UserCreate, Video, Summary, TimeRange, Category, SummaryProgressResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = import.meta.env.VITE_API_BASE_URL || `${API_BASE}`;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const authApi = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('vdsm_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('vdsm_token');
      localStorage.removeItem('vdsm_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(email: string, password: string): Promise<Token> {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await authApi.post<Token>('/auth/login', params);
    return response.data;
  },

  async register(data: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('vdsm_token');
    localStorage.removeItem('vdsm_user');
  }
};

export const videoService = {
  async uploadVideo(
    file: File,
    title: string,
    description: string,
    onProgress: (progress: number) => void
  ): Promise<Video> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) {
      formData.append('description', description);
    }

    const response = await api.post<Video>('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  async getVideos(skip: number = 0, limit: number = 20): Promise<Video[]> {
    const response = await api.get<Video[]>('/videos/', {
      params: { skip, limit },
    });
    return response.data;
  },

  async getVideoById(videoId: string): Promise<Video> {
    const response = await api.get<Video>(`/videos/${videoId}`);
    return response.data;
  },

  async deleteVideo(videoId: string): Promise<void> {
    await api.delete(`/videos/${videoId}`);
  },

  async getDownloadUrl(videoId: string): Promise<string> {
    return `${API_BASE}/videos/${videoId}/download`;
  },

  async downloadVideo(videoId: string): Promise<void> {
    window.open(`${API_BASE}/videos/${videoId}/download`, '_blank');
  }
};

export const summaryService = {
  async createTextPromptSummary(
    videoId: string, 
    title: string, 
    prompt: string
  ): Promise<Summary> {
    const response = await api.post<Summary>(`/videos/${videoId}/summaries/text-prompt`, {
      title,
      prompt
    });
    return response.data;
  },

  async createCategorySummary(
    videoId: string,
    title: string,
    category: string
  ): Promise<Summary> {
    const response = await api.post<Summary>(`/videos/${videoId}/summaries/category`, {
      title,
      category
    });
    return response.data;
  },

  async createTimeRangeSummary(
    videoId: string,
    title: string,
    ranges: TimeRange[]
  ): Promise<Summary> {
    const response = await api.post<Summary>(`/videos/${videoId}/summaries/time-range`, {
      title,
      ranges
    });
    return response.data;
  },

  async getSummaries(videoId: string): Promise<Summary[]> {
    const response = await api.get<Summary[]>(`/videos/${videoId}/summaries`);
    return response.data;
  },

  async getSummaryById(summaryId: string): Promise<Summary> {
    const response = await api.get<Summary>(`/summaries/${summaryId}`);
    return response.data;
  },

  async getSummaryProgress(summaryId: string): Promise<SummaryProgressResponse> {
    const response = await api.get<SummaryProgressResponse>(`/summaries/${summaryId}/progress`);
    return response.data;
  },

  async deleteSummary(summaryId: string): Promise<void> {
    await api.delete(`/summaries/${summaryId}`);
  },

  async getDownloadUrl(summaryId: string): Promise<string> {
    return `${API_BASE}/summaries/${summaryId}/download`;
  },

  async downloadSummary(summaryId: string): Promise<void> {
    window.open(`${API_BASE}/summaries/${summaryId}/download`, '_blank');
  },

  async getCategories(): Promise<{ categories: Category[] }> {
    const response = await api.get<{ categories: Category[] }>('/categories');
    return response.data;
  }
};

export default api;
