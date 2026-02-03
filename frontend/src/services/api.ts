import axios, { AxiosError } from 'axios';
import { Token, User, UserCreate, Video } from '../types';

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

export default api;
