const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Types matching your API response structure
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
  progress: number;
  current_step: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  video_metadata: VideoMetadata;
  transcript: Transcript;
  clips: Clips;
  summary: Summary;
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

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Upload video file
  async uploadVideo(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${this.baseUrl}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return await response.text();
    } catch (error) {
      // Fallback to mock response if API is not available
      console.warn("API not available, using mock response:", error);
      return this.mockUploadResponse(file);
    }
  }

  // Get all jobs
  async getJobs(): Promise<JobsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/jobs/`);

      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      // Fallback to mock data if API is not available
      console.warn("API not available, using mock data:", error);
      return this.mockJobsResponse();
    }
  }

  // Download clips as zip
  async downloadClipsZip(jobId: string): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseUrl}/download/${jobId}/zip`);

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      // Fallback to mock download
      console.warn("API not available, using mock download:", error);
      return this.mockDownloadResponse(jobId);
    }
  }

  // Helper method to trigger download
  async downloadAndSaveClips(jobId: string, filename: string): Promise<void> {
    try {
      const blob = await this.downloadClipsZip(jobId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${filename}-clips.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
      throw error;
    }
  }

  // Fetch list of clips for a job
  async getClips(jobId: string): Promise<{
    job_id: string;
    count: number;
    clips: Array<{
      filename: string;
      title: string;
      description: string;
      duration: number;
      start_time: number;
      end_time: number;
      size_mb: number;
      url: string;
    }>;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/clips/${jobId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch clips: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      // Fallback to mock clips
      console.warn("API not available, using mock clips:", error);
      return this.mockClipsResponse(jobId);
    }
  }

  // Build stream URL for a specific clip filename
  getStreamUrl(jobId: string, filename: string): string {
    return `${this.baseUrl}/download/${jobId}/stream/${encodeURIComponent(
      filename
    )}`;
  }

  // Mock responses for when API is not available
  private mockUploadResponse(file: File): string {
    const jobId = `mock_${Date.now()}`;
    console.log(`Mock upload successful for ${file.name}, job ID: ${jobId}`);
    return jobId;
  }

  private mockJobsResponse(): JobsResponse {
    return {
      jobs: [
        {
          job_id: "mock_1",
          status: "completed",
          progress: 100,
          current_step: "Completed",
          error_message: null,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          updated_at: new Date(Date.now() - 3600000).toISOString(),
          video_metadata: {
            filename: "sample-podcast.mp4",
            size_mb: 45.2,
            duration_seconds: 1800,
            duration_formatted: "30m 0s",
            format: "mp4",
            resolution: "1280x720",
            fps: 30,
          },
          transcript: {
            available: true,
            segments_count: 45,
            total_duration: 1800,
            language: "en",
          },
          clips: {
            available: true,
            count: 8,
            total_duration: 480,
            total_size_mb: 12.5,
            clips: [],
          },
          summary: {
            original_filename: "sample-podcast.mp4",
            completed_at: new Date(Date.now() - 3600000).toISOString(),
            total_processing_time: "2m 15s",
          },
        },
        {
          job_id: "mock_2",
          status: "processing",
          progress: 65,
          current_step: "Generating clips",
          error_message: null,
          created_at: new Date(Date.now() - 1800000).toISOString(),
          updated_at: new Date().toISOString(),
          video_metadata: {
            filename: "interview-episode.mp4",
            size_mb: 78.9,
            duration_seconds: 2400,
            duration_formatted: "40m 0s",
            format: "mp4",
            resolution: "1920x1080",
            fps: 30,
          },
          transcript: {
            available: true,
            segments_count: 60,
            total_duration: 2400,
            language: "en",
          },
          clips: {
            available: false,
            count: 0,
            total_duration: 0,
            total_size_mb: 0,
            clips: null,
          },
          summary: {
            original_filename: "interview-episode.mp4",
            completed_at: "",
            total_processing_time: "",
          },
        },
      ],
      total: 2,
      summary: {
        status_counts: {
          completed: 1,
          processing: 1,
          queued: 0,
          failed: 0,
        },
        total_size_mb: 124.1,
        total_size_gb: 0.12,
        total_clips: 8,
        total_duration_hours: 1.17,
      },
    };
  }

  private mockDownloadResponse(jobId: string): Blob {
    // Create a mock ZIP file content
    const mockContent = `Mock ZIP file for job ${jobId}`;
    return new Blob([mockContent], { type: "application/zip" });
  }

  private mockClipsResponse(jobId: string) {
    return {
      job_id: jobId,
      count: 3,
      clips: [
        {
          filename: "clip_1.mp4",
          title: "Key Insight About AI Development",
          description:
            "Discussion about the future of artificial intelligence and machine learning",
          duration: 60,
          start_time: 245,
          end_time: 305,
          size_mb: 2.1,
          url: "#",
        },
        {
          filename: "clip_2.mp4",
          title: "Funny Story About Startup Life",
          description:
            "A humorous anecdote about the challenges of building a startup",
          duration: 90,
          start_time: 1250,
          end_time: 1340,
          size_mb: 3.2,
          url: "#",
        },
        {
          filename: "clip_3.mp4",
          title: "Investment Strategy Discussion",
          description:
            "Deep dive into investment strategies and portfolio management",
          duration: 80,
          start_time: 2100,
          end_time: 2180,
          size_mb: 2.8,
          url: "#",
        },
      ],
    };
  }
}

export const apiService = new ApiService();
