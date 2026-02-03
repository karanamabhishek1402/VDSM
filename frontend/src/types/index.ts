export interface User {
  id: string;
  email: string;
  full_name?: string;
}

export interface Video {
  id: string;
  title: string;
  description?: string;
  duration?: number;
  uploaded_at: string;
  processed: boolean;
  file_path: string;
}

export interface Summary {
  id: string;
  video_id: string;
  content: string;
  created_at: string;
}
