# VDSM Setup Guide - Video Summarization System

## Prerequisites

- Python 3.9+
- Node.js 16+
- Redis (for RQ task queue)
- FFmpeg (for video processing)
- Supabase account (or local instance)

## Database Setup

### 1. Create Supabase Tables

Run the following SQL in your Supabase SQL editor:

```sql
-- Create users table (if not exists)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create videos table (if not exists)
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_name VARCHAR(500) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    duration_seconds INTEGER,
    format VARCHAR(20) NOT NULL,
    resolution VARCHAR(20),
    video_width INTEGER,
    video_height INTEGER,
    fps FLOAT,
    upload_status VARCHAR(50) DEFAULT 'uploaded',
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    request_data JSONB NOT NULL,
    selected_scenes JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary_duration_seconds INTEGER,
    output_format VARCHAR(20) DEFAULT 'mp4',
    storage_path VARCHAR(500),
    file_size BIGINT,
    status VARCHAR(50) DEFAULT 'processing',
    progress_percent INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_summaries_video_id ON summaries(video_id);
CREATE INDEX IF NOT EXISTS idx_summaries_user_id ON summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_summaries_status ON summaries(status);
CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_summaries_updated_at
    BEFORE UPDATE ON summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2. Create Supabase Storage Buckets

In Supabase Storage, create two buckets:
- `videos` (for uploaded videos)
- `summaries` (for generated summary videos)

Both should be set to public or use signed URLs for access.

## Backend Setup

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg redis-server
```

**macOS:**
```bash
brew install python ffmpeg redis
brew services start redis
```

### 2. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Note: This will install CLIP, PyTorch, and other dependencies. It may take several minutes.

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# App Settings
APP_NAME=VDSM API
DEBUG=True

# Authentication (generate a secure secret key)
JWT_SECRET=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_STORAGE_BUCKET=videos

# Video Upload
MAX_VIDEO_SIZE_MB=4000
SUPPORTED_VIDEO_FORMATS=mp4,mov,wmv,avi,mkv,webm

# Redis Settings
REDIS_URL=redis://localhost:6379

# CLIP and Processing
CLIP_MODEL_NAME=ViT-B/32
FRAME_SAMPLE_RATE=30
SCENE_SIMILARITY_THRESHOLD=0.3
TARGET_SUMMARY_DURATION_SECONDS=300

# Summary Storage
SUMMARY_STORAGE_PATH=summaries
SUMMARY_STORAGE_BUCKET=summaries
```

### 5. Start Redis

Make sure Redis is running:

```bash
redis-server
```

### 6. Start RQ Worker

In a separate terminal, start the RQ worker to process video summarization tasks:

```bash
cd backend
source venv/bin/activate
rq worker --with-scheduler
```

### 7. Start Backend Server

In another terminal:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### 1. Register an Account

Navigate to `http://localhost:5173/register` and create an account.

### 2. Upload a Video

- Go to Dashboard
- Click "Upload Video"
- Select a video file (up to 4 hours long)
- Wait for upload and processing to complete

### 3. Create a Summary

On the video detail page, you can create summaries using three methods:

**Text Prompt:**
- Enter a description like "action scenes", "dialogue moments", or "beautiful landscapes"
- CLIP AI will find matching scenes

**Category:**
- Select from predefined categories (Action, Dialogue, Landscape, People, Text, Key Moments)
- Each category has optimized prompts

**Time Range:**
- Manually select time ranges using percentages
- Add multiple ranges for compilation videos

### 4. Monitor Progress

- Summaries show real-time progress bars
- Processing time depends on video length
- You can navigate away and check back later

### 5. View and Download

- Once complete, view summaries in the built-in player
- Download summary videos to your device
- See which scenes were selected and their confidence scores

## Troubleshooting

### CLIP Model Issues

If CLIP fails to load:
```bash
# Force reinstall
pip uninstall clip
pip install git+https://github.com/openai/CLIP.git
```

### FFmpeg Errors

Ensure FFmpeg is properly installed:
```bash
ffmpeg -version
```

### Redis Connection Issues

Check if Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Supabase Connection Issues

- Verify your Supabase URL and keys are correct
- Check that buckets are created
- Ensure RLS policies allow authenticated access

## Performance Tuning

### For Long Videos (2-4 hours)

Increase frame sample rate to reduce processing time:
```env
FRAME_SAMPLE_RATE=60  # Sample 1 frame every 60 frames
```

### For Better Scene Matching

Adjust similarity threshold:
```env
SCENE_SIMILARITY_THRESHOLD=0.25  # Lower = more scenes matched
```

### For Different Summary Lengths

```env
TARGET_SUMMARY_DURATION_SECONDS=180  # 3 minute summaries
```

## Development Notes

- CLIP model downloads once on first startup (~350MB)
- Frame extraction is memory-intensive for long videos
- Background tasks timeout after 4 hours by default
- Summary videos are stored in Supabase Storage
- Progress updates occur every 2 seconds

## Production Deployment

For production:
1. Set `DEBUG=False`
2. Use a strong `JWT_SECRET`
3. Configure proper CORS origins
4. Use a production-grade Redis instance
5. Consider GPU acceleration for CLIP
6. Implement rate limiting
7. Add monitoring and logging
8. Set up proper backup procedures
