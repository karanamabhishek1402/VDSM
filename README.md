# VDSM - Video Summarization Platform

A video summarization website where users can upload long videos (up to 4 hours) and generate short summaries based on text prompts, categories, and time ranges.

## Features

- **Upload & Processing**: Upload videos up to 4 hours long.
- **Smart Summarization**: Generate summaries using text prompts, categories, or specific time ranges.
- **Advanced Technology**: Powered by CLIP embeddings for content understanding.
- **Background Processing**: Asynchronous video processing using Redis Queue.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via Supabase)
- **Storage**: Supabase Storage
- **Task Queue**: RQ (Redis Queue)
- **Video Processing**: FFmpeg
- **AI/ML**: CLIP (Contrastive Language-Image Pre-training)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS / Material UI
- **State Management**: Context API

## Project Structure

```
/
├── backend/            # FastAPI backend application
│   ├── app/            # Application source code
│   │   ├── api/        # API route handlers
│   │   ├── models/     # Pydantic models
│   │   ├── services/   # Business logic services
│   │   └── tasks/      # Background tasks (RQ)
│   ├── main.py         # Application entry point
│   └── requirements.txt
│
└── frontend/           # React frontend application
    ├── src/            # Source code
    │   ├── components/ # Reusable UI components
    │   ├── pages/      # Page components
    │   ├── services/   # API client services
    │   └── context/    # React context providers
    ├── package.json
    └── vite.config.ts
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- Redis (for task queue)
- Supabase account (or local instance)
- FFmpeg installed on system

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env` and fill in your Supabase and Redis credentials.
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   Copy `.env.example` to `.env` and fill in the API URL and Supabase credentials.
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

Check the `.env.example` files in both `backend` and `frontend` directories for the complete list of required environment variables.
