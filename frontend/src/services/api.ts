import axios, { AxiosError } from 'axios';
import { Token, User, UserCreate } from '../types';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

export default api;
