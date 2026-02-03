-- Migration: Create summaries table for video summarization
-- Date: 2024-02-03

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

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_summaries_video_id ON summaries(video_id);
CREATE INDEX IF NOT EXISTS idx_summaries_user_id ON summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_summaries_status ON summaries(status);
CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_summaries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_summaries_updated_at
    BEFORE UPDATE ON summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_summaries_updated_at();

-- Add comments for documentation
COMMENT ON TABLE summaries IS 'Stores video summarization requests and results';
COMMENT ON COLUMN summaries.request_type IS 'Type of summarization: text-prompt, category, or time-range';
COMMENT ON COLUMN summaries.request_data IS 'JSON data specific to the request type';
COMMENT ON COLUMN summaries.selected_scenes IS 'JSON array of selected scenes with timing and confidence data';
COMMENT ON COLUMN summaries.status IS 'Processing status: processing, completed, or failed';
