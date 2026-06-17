export interface Clip {
  id: string;
  title?: string | null;
  start_time: string;
  end_time: string;
  final_score: number;
  recommend_reason: string;
  generated_title?: string | null;
  outline: string;
  content: string[];
  chunk_index?: number | null;
}

export interface Collection {
  id: string;
  collection_title: string;
  collection_summary: string;
  clip_ids: string[];
  collection_type?: string;
  created_at?: string | null;
}

export interface Project {
  id: string;
  name: string;
  video_path: string;
  status: "uploading" | "processing" | "completed" | "error";
  created_at: string;
  updated_at: string;
  video_category?: string;
  clips?: Clip[];
  collections?: Collection[];
  current_step?: number | null;
  total_steps?: number | null;
  error_message?: string | null;
}

export interface ProjectStatus {
  status: "uploading" | "processing" | "completed" | "error";
  current_step?: number | null;
  total_steps?: number | null;
  step_name?: string | null;
  progress?: number | null;
  error_message?: string | null;
}
