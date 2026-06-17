// Legacy Upload interface for backward compatibility
export interface Upload {
  id: string;
  fileName: string;
  status: "processing" | "ready" | "downloaded";
  uploadedAt: string;
  duration: string;
  estimatedClips?: number;
  clipsGenerated?: number;
  fileSize?: string;
  downloadSize?: string;
  resolution?: string;
  processingTime?: string;
}

// New API-based interfaces
export interface VideoMetadata {
  filename: string;
  size_mb: number;
  duration_seconds: number;
  duration_formatted: string;
  format: string;
  resolution: string;
  fps: number;
}

export interface Transcript {
  available: boolean;
  segments_count: number;
  total_duration: number;
  language: string;
}

export interface Clips {
  available: boolean;
  count: number;
  total_duration: number;
  total_size_mb: number;
  clips: any[] | null;
}

export interface Summary {
  original_filename: string;
  completed_at: string;
  total_processing_time: string;
}

export interface Job {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress?: number;
  current_step?: string;
  error_message?: string | null;
  created_at?: string;
  updated_at?: string;
  video_metadata?: Partial<VideoMetadata>;
  transcript?: { available: boolean } | Partial<Transcript>;
  clips?: { available: boolean } | Partial<Clips>;
  summary?: Partial<Summary>;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  summary: {
    status_counts: Record<string, number>;
    total_size_mb: number;
    total_size_gb: number;
    total_clips: number;
    total_duration_hours: number;
  };
}

export interface Clip {
  id: string;
  title: string;
  startTime: number;
  endTime: number;
  confidence: number;
  topic: string;
  emoji: string;
  duration: number;
  thumbnail?: string;
}

export interface ClipResult {
  uploadId: string;
  fileName: string;
  totalClips: number;
  clips: Clip[];
  totalDuration: number;
  processingTime: number;
}
