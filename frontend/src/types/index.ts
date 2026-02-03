export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export interface VideoMetadata {
  duration_seconds: number;
  resolution: string;
  fps: number;
  video_width: number;
  video_height: number;
  format: string;
}

export interface Video {
  id: string;
  user_id: string;
  title: string;
  description: string;
  file_name: string;
  file_size: number;
  format: string;
  duration_seconds: number;
  video_width: number;
  video_height: number;
  fps: number;
  created_at: string;
  updated_at: string;
}

export interface VideoUploadProgress {
  loaded: number;
  total: number;
  percent: number;
}

export interface TimeRange {
  start_percent: number;
  end_percent: number;
}

export interface TextPromptData {
  prompt: string;
}

export interface CategoryData {
  category: string;
}

export interface TimeRangeData {
  ranges: TimeRange[];
}

export interface SceneData {
  start_time: number;
  end_time: number;
  duration: number;
  confidence_score: number;
  matched_text?: string;
  matched_category?: string;
}

export interface Summary {
  id: string;
  video_id: string;
  user_id: string;
  title: string;
  request_type: 'text-prompt' | 'category' | 'time-range';
  request_data: TextPromptData | CategoryData | TimeRangeData;
  selected_scenes?: SceneData[];
  summary_duration_seconds?: number;
  output_format: string;
  storage_path?: string;
  file_size?: number;
  status: 'processing' | 'completed' | 'failed';
  progress_percent: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  updated_at: string;
}

export interface SummaryRequest {
  title: string;
  type: 'text-prompt' | 'category' | 'time-range';
  data: TextPromptData | CategoryData | TimeRangeData;
}

export interface SummaryProgressResponse {
  summary_id: string;
  status: string;
  progress_percent: number;
  error_message?: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
}
