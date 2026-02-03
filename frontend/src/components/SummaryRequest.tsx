import React, { useState, useEffect } from 'react';
import { summaryService } from '../services/api';
import { Category, TimeRange } from '../types';

interface SummaryRequestProps {
  videoId: string;
  videoDuration?: number; // in seconds, for time range visualization
  onSummaryCreated?: () => void;
}

type TabType = 'text-prompt' | 'category' | 'time-range';

const SummaryRequest: React.FC<SummaryRequestProps> = ({ 
  videoId, 
  videoDuration,
  onSummaryCreated 
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('text-prompt');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);

  // Text prompt state
  const [textPromptTitle, setTextPromptTitle] = useState('');
  const [textPrompt, setTextPrompt] = useState('');

  // Category state
  const [categoryTitle, setCategoryTitle] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  // Time range state
  const [timeRangeTitle, setTimeRangeTitle] = useState('');
  const [timeRanges, setTimeRanges] = useState<TimeRange[]>([{ start_percent: 0, end_percent: 25 }]);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const result = await summaryService.getCategories();
      setCategories(result.categories);
      if (result.categories.length > 0) {
        setSelectedCategory(result.categories[0].id);
      }
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  };

  const handleTextPromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await summaryService.createTextPromptSummary(videoId, textPromptTitle, textPrompt);
      setSuccess(true);
      setTextPromptTitle('');
      setTextPrompt('');
      if (onSummaryCreated) onSummaryCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create summary');
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await summaryService.createCategorySummary(videoId, categoryTitle, selectedCategory);
      setSuccess(true);
      setCategoryTitle('');
      if (onSummaryCreated) onSummaryCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create summary');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await summaryService.createTimeRangeSummary(videoId, timeRangeTitle, timeRanges);
      setSuccess(true);
      setTimeRangeTitle('');
      setTimeRanges([{ start_percent: 0, end_percent: 25 }]);
      if (onSummaryCreated) onSummaryCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create summary');
    } finally {
      setLoading(false);
    }
  };

  const addTimeRange = () => {
    const lastRange = timeRanges[timeRanges.length - 1];
    const newStart = Math.min(lastRange.end_percent + 1, 99);
    setTimeRanges([...timeRanges, { start_percent: newStart, end_percent: Math.min(newStart + 25, 100) }]);
  };

  const removeTimeRange = (index: number) => {
    if (timeRanges.length > 1) {
      setTimeRanges(timeRanges.filter((_, i) => i !== index));
    }
  };

  const updateTimeRange = (index: number, field: 'start_percent' | 'end_percent', value: number) => {
    const newRanges = [...timeRanges];
    newRanges[index][field] = Math.max(0, Math.min(100, value));
    setTimeRanges(newRanges);
  };

  const formatTime = (percent: number): string => {
    if (!videoDuration) return `${percent.toFixed(1)}%`;
    const seconds = (percent / 100) * videoDuration;
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')} (${percent.toFixed(1)}%)`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Create Video Summary</h2>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('text-prompt')}
            className={`${
              activeTab === 'text-prompt'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Text Prompt
          </button>
          <button
            onClick={() => setActiveTab('category')}
            className={`${
              activeTab === 'category'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Category
          </button>
          <button
            onClick={() => setActiveTab('time-range')}
            className={`${
              activeTab === 'time-range'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Time Range
          </button>
        </nav>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          Summary created successfully! Processing will begin shortly.
        </div>
      )}

      {/* Tab Content */}
      <div className="tab-content">
        {/* Text Prompt Tab */}
        {activeTab === 'text-prompt' && (
          <form onSubmit={handleTextPromptSubmit} className="space-y-4">
            <div>
              <label htmlFor="text-prompt-title" className="block text-sm font-medium text-gray-700 mb-2">
                Summary Title *
              </label>
              <input
                id="text-prompt-title"
                type="text"
                value={textPromptTitle}
                onChange={(e) => setTextPromptTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Action Scenes Compilation"
                required
                maxLength={255}
              />
            </div>
            <div>
              <label htmlFor="text-prompt" className="block text-sm font-medium text-gray-700 mb-2">
                Prompt *
              </label>
              <textarea
                id="text-prompt"
                value={textPrompt}
                onChange={(e) => setTextPrompt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder="Describe the scenes you want to find... Examples:&#10;• action scenes&#10;• dialogue moments&#10;• beautiful landscapes&#10;• people smiling"
                required
                maxLength={500}
              />
              <p className="mt-2 text-sm text-gray-500">
                Tip: Be specific! CLIP AI will find scenes matching your description.
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Generate Summary'}
            </button>
          </form>
        )}

        {/* Category Tab */}
        {activeTab === 'category' && (
          <form onSubmit={handleCategorySubmit} className="space-y-4">
            <div>
              <label htmlFor="category-title" className="block text-sm font-medium text-gray-700 mb-2">
                Summary Title *
              </label>
              <input
                id="category-title"
                type="text"
                value={categoryTitle}
                onChange={(e) => setCategoryTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., All Dialogue Scenes"
                required
                maxLength={255}
              />
            </div>
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                id="category"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              {selectedCategory && (
                <p className="mt-2 text-sm text-gray-600">
                  {categories.find((c) => c.id === selectedCategory)?.description}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Generate Summary'}
            </button>
          </form>
        )}

        {/* Time Range Tab */}
        {activeTab === 'time-range' && (
          <form onSubmit={handleTimeRangeSubmit} className="space-y-4">
            <div>
              <label htmlFor="time-range-title" className="block text-sm font-medium text-gray-700 mb-2">
                Summary Title *
              </label>
              <input
                id="time-range-title"
                type="text"
                value={timeRangeTitle}
                onChange={(e) => setTimeRangeTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Highlights Compilation"
                required
                maxLength={255}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Ranges *</label>
              {timeRanges.map((range, index) => (
                <div key={index} className="flex items-center space-x-2 mb-3">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Start</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={range.start_percent}
                      onChange={(e) => updateTimeRange(index, 'start_percent', parseFloat(e.target.value))}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                    <span className="text-xs text-gray-500">{formatTime(range.start_percent)}</span>
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">End</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={range.end_percent}
                      onChange={(e) => updateTimeRange(index, 'end_percent', parseFloat(e.target.value))}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                    <span className="text-xs text-gray-500">{formatTime(range.end_percent)}</span>
                  </div>
                  {timeRanges.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTimeRange(index)}
                      className="mt-4 px-2 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={addTimeRange}
                className="mt-2 px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
              >
                + Add Range
              </button>
              <p className="mt-2 text-sm text-gray-500">
                Total duration: {timeRanges.reduce((sum, r) => sum + (r.end_percent - r.start_percent), 0).toFixed(1)}%
              </p>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Generate Summary'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default SummaryRequest;
