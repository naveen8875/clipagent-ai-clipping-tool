# AI Video Processing Backend API Documentation

## 📋 Overview

This document provides comprehensive API documentation for the AI Video Processing Backend with Supabase integration. All endpoints return JSON responses with detailed schemas for easy UI mapping.

## 🔑 Authentication

All API endpoints require authentication via API key header:

```http
x-api-key: your-api-key-here
```

## 📊 Base URL

```
http://localhost:8000
```

---

## 🎬 Video Endpoints

### 1. Upload Video

**Endpoint:** `POST /api/v1/videos/upload`

**Description:** Upload a video for AI processing via HeyGen API

**Request Body:**

```json
{
  "data": {
    "video_input_type": "url",
    "video_key": "https://www.youtube.com/watch?v=example",
    "name": "Video Title",
    "input_language": "",
    "output_settings": {
      "prompt": "Create compelling clips",
      "duration_types": ["60"],
      "aspect_ratio": "landscape",
      "is_captions_enabled": true
    },
    "source_type": "video_repurpose"
  },
  "title": "Custom Video Title",
  "description": "Video description"
}
```

**Response Schema:**

```json
{
  "id": "user_id_video_timestamp",
  "filename": "Video Title",
  "status": "submitted",
  "message": "Video submitted to HeyGen for processing",
  "created_at": "2025-01-19T10:30:00.000Z"
}
```

**Status Codes:**

- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

---

### 2. List Videos

**Endpoint:** `GET /api/v1/videos`

**Description:** Get paginated list of user's videos

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `status` (optional): Filter by status (`uploaded`, `submitted`, `processing`, `completed`, `failed`)

**Example:**

```http
GET /api/v1/videos?page=1&per_page=10&status=completed
```

**Response Schema:**

```json
{
  "videos": [
    {
      "id": "user_id_video_timestamp",
      "user_id": "user-uuid",
      "filename": "Video Title",
      "status": "completed",
      "progress": 100,
      "title": "Custom Video Title",
      "description": "Video description",
      "highlights": [
        {
          "id": "clip-uuid-1",
          "name": "Amazing Moment"
        },
        {
          "id": "clip-uuid-2",
          "name": "Key Insight"
        }
      ],
      "thumbnails": {
        "clip-uuid-1": {
          "name": "Amazing Moment",
          "thumbnails": {
            "720p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/720p_thumb",
            "1080p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/1080p_thumb"
          }
        },
        "clip-uuid-2": {
          "name": "Key Insight",
          "thumbnails": {
            "720p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-2/720p_thumb"
          }
        }
      },
      "video_urls": {
        "clip-uuid-1": {
          "name": "Amazing Moment",
          "videos": {
            "360p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/360p",
            "720p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/720p",
            "1080p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/1080p"
          }
        },
        "clip-uuid-2": {
          "name": "Key Insight",
          "videos": {
            "720p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-2/720p"
          }
        }
      },
      "heygen_project_id": "project-uuid",
      "heygen_status": 100,
      "created_at": "2025-01-19T10:30:00.000Z",
      "updated_at": "2025-01-19T10:35:00.000Z",
      "completed_at": "2025-01-19T10:35:00.000Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "has_next": true,
  "has_previous": false
}
```

---

### 3. Get Video Details

**Endpoint:** `GET /api/v1/videos/{video_id}`

**Description:** Get detailed information about a specific video

**Response Schema:**

```json
{
  "id": "user_id_video_timestamp",
  "user_id": "user-uuid",
  "filename": "Video Title",
  "unique_filename": "unique_filename.mp4",
  "file_path": "/path/to/file.mp4",
  "file_size": 10485760,
  "file_hash": "sha256_hash",
  "uploaded_at": "2025-01-19T10:30:00.000Z",
  "status": "completed",
  "progress": 100,
  "title": "Custom Video Title",
  "description": "Video description",
  "customizations": {
    "video_input_type": "url",
    "video_key": "https://www.youtube.com/watch?v=example",
    "name": "Video Title",
    "input_language": "",
    "output_settings": {
      "prompt": "Create compelling clips",
      "duration_types": ["60"],
      "aspect_ratio": "landscape",
      "is_captions_enabled": true
    },
    "source_type": "video_repurpose"
  },
  "highlights": [
    {
      "id": "clip-uuid-1",
      "name": "Amazing Moment"
    },
    {
      "id": "clip-uuid-2",
      "name": "Key Insight"
    }
  ],
  "thumbnails": {
    "clip-uuid-1": {
      "name": "Amazing Moment",
      "thumbnails": {
        "640x360": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/640x360",
        "1280x720": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/1280x720",
        "1920x1080": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/1920x1080",
        "360p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/360p_thumb",
        "720p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/720p_thumb",
        "1080p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/1080p_thumb",
        "original_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-1/original_thumb"
      }
    },
    "clip-uuid-2": {
      "name": "Key Insight",
      "thumbnails": {
        "720p_thumb": "/api/v1/videos/user_id_video_timestamp/thumbnail/clip/clip-uuid-2/720p_thumb"
      }
    }
  },
  "video_urls": {
    "clip-uuid-1": {
      "name": "Amazing Moment",
      "videos": {
        "360p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/360p",
        "720p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/720p",
        "1080p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/1080p",
        "original": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-1/original"
      }
    },
    "clip-uuid-2": {
      "name": "Key Insight",
      "videos": {
        "720p": "/api/v1/videos/user_id_video_timestamp/download/clip/clip-uuid-2/720p"
      }
    }
  },
  "heygen_project_id": "project-uuid",
  "heygen_status": 100,
  "heygen_progress": 100,
  "heygen_error_message": null,
  "raw_heygen_data": {
    "code": 100,
    "data": "project-uuid",
    "msg": null,
    "message": null
  },
  "created_at": "2025-01-19T10:30:00.000Z",
  "updated_at": "2025-01-19T10:35:00.000Z",
  "completed_at": "2025-01-19T10:35:00.000Z"
}
```

---

### 4. Get Video Status

**Endpoint:** `GET /api/v1/videos/{video_id}/status`

**Description:** Get real-time status of a video processing

**Response Schema:**

```json
{
  "id": "user_id_video_timestamp",
  "status": "processing",
  "progress": 75,
  "heygen_status": 75,
  "heygen_project_id": "project-uuid",
  "message": "Video is being processed by HeyGen",
  "estimated_completion": "2025-01-19T10:40:00.000Z",
  "last_updated": "2025-01-19T10:35:00.000Z"
}
```

**Status Values:**

- `uploaded`: Video uploaded, ready for processing
- `submitted`: Submitted to HeyGen API
- `processing`: Being processed by HeyGen
- `completed`: Processing completed successfully
- `failed`: Processing failed

---

### 5. Delete Video

**Endpoint:** `DELETE /api/v1/videos/{video_id}`

**Description:** Delete a video and all associated data

**Response Schema:**

```json
{
  "message": "Video deleted successfully",
  "video_id": "user_id_video_timestamp",
  "deleted_at": "2025-01-19T10:30:00.000Z"
}
```

---

## 📊 Data Models & Schemas

### Video Record Schema

```typescript
interface VideoRecord {
  // Core identifiers
  id: string; // Format: {user_id}_video_{timestamp}
  user_id: string; // UUID of the user
  filename: string; // Original filename
  unique_filename: string; // Unique filename for storage

  // File information
  file_path: string; // Local file path (if applicable)
  file_size: number; // File size in bytes
  file_hash: string; // SHA256 hash of file
  uploaded_at: string; // ISO timestamp

  // Processing status
  status: VideoStatus; // Current processing status
  progress: number; // Progress percentage (0-100)

  // Video metadata
  title: string; // User-defined title
  description: string; // User-defined description
  customizations: object; // HeyGen API customization data

  // HeyGen integration
  heygen_project_id: string; // HeyGen project identifier
  heygen_status: number; // HeyGen processing status code
  heygen_progress: number; // HeyGen progress percentage
  heygen_error_message: string; // Error message from HeyGen
  raw_heygen_data: object; // Complete HeyGen response data

  // Results
  highlights: Highlight[]; // Array of generated video clips
  thumbnails: ThumbnailSet; // Thumbnail URLs
  video_urls: VideoUrlSet; // Video URLs

  // Timestamps
  created_at: string; // Record creation time
  updated_at: string; // Last update time
  completed_at: string; // Completion time (if completed)
}
```

### Video Status Enum

```typescript
enum VideoStatus {
  UPLOADED = "uploaded",
  SUBMITTED = "submitted",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}
```

### Highlight Schema

```typescript
interface Highlight {
  id: string; // Unique clip identifier
  title: string; // Clip title
  duration: number; // Duration in seconds
  start_time: number; // Start time in original video
  end_time: number; // End time in original video
  video_url: string; // URL to clip video file
  thumbnail_url: string; // URL to clip thumbnail
  transcript: string; // Text transcript of clip
  summary: string; // AI-generated summary
  engagement_score: number; // Predicted engagement score
  keywords: string[]; // Extracted keywords
}
```

### Thumbnail Set Schema

```typescript
interface ThumbnailSet {
  main: string; // Main video thumbnail
  preview: string; // Preview thumbnail
  clips: string[]; // Array of clip thumbnails
}
```

### Video URL Set Schema

```typescript
interface VideoUrlSet {
  original: string; // Original uploaded video
  processed: string; // HeyGen processed video
  clips: string[]; // Array of clip video URLs
}
```

### Pagination Schema

```typescript
interface PaginationResponse<T> {
  data: T[]; // Array of items
  total: number; // Total number of items
  page: number; // Current page number
  per_page: number; // Items per page
  has_next: boolean; // Has next page
  has_previous: boolean; // Has previous page
}
```

---

## 🗄️ Database Schema & Relationships

### Table Structure

#### 1. **users** Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

#### 2. **videos** Table

```sql
CREATE TABLE videos (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    unique_filename VARCHAR(255),
    file_path TEXT,
    file_size BIGINT DEFAULT 0,
    file_hash VARCHAR(255),
    uploaded_at TIMESTAMP WITH TIME ZONE,

    -- HeyGen Integration
    heygen_project_id VARCHAR(255),
    heygen_status INTEGER,
    heygen_progress INTEGER,
    heygen_error_message TEXT,

    -- Processing Status
    status VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0,

    -- Video Metadata
    title VARCHAR(500),
    description TEXT,
    customizations JSONB DEFAULT '{}',

    -- Results (Rich JSON structures)
    highlights JSONB DEFAULT '[]',
    thumbnails JSONB DEFAULT '{}',
    video_urls JSONB DEFAULT '{}',
    raw_heygen_data JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
```

#### 3. **video_analytics** Table

```sql
CREATE TABLE video_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id VARCHAR(255) REFERENCES videos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- 'download', 'view', 'share', etc.
    event_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4. **system_logs** Table

```sql
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(20) NOT NULL, -- 'INFO', 'ERROR', 'WARNING', etc.
    message TEXT NOT NULL,
    module VARCHAR(100),
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 5. **system_config** Table

```sql
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB DEFAULT '{}',
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🔗 Database Relationships

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│    users    │       │   videos    │       │ video_analytics │
│             │       │             │       │                 │
│ • id (PK)   │◄──────┤ • user_id   │       │ • video_id      │
│ • email     │       │ • id (PK)   │◄──────┤ • user_id       │
│ • name      │       │ • filename  │       │ • event_type    │
│ • api_key   │       │ • status    │       │ • event_data    │
│ • created_at│       │ • highlights│       │ • created_at    │
└─────────────┘       │ • thumbnails│       └─────────────────┘
                      │ • video_urls│
                      │ • created_at│
                      └─────────────┘
                              │
                              │
                      ┌─────────────┐
                      │ system_logs │
                      │             │
                      │ • level     │
                      │ • message   │
                      │ • module    │
                      │ • data      │
                      └─────────────┘
```

### Relationship Details

#### 1. **Users → Videos** (One-to-Many)

- **Relationship**: `users.id` → `videos.user_id`
- **Cardinality**: One user can have many videos
- **Cascade**: DELETE CASCADE (deleting user removes all their videos)
- **Index**: `idx_videos_user_id`

#### 2. **Videos → Analytics** (One-to-Many)

- **Relationship**: `videos.id` → `video_analytics.video_id`
- **Cardinality**: One video can have many analytics events
- **Cascade**: DELETE CASCADE (deleting video removes all its analytics)
- **Index**: `idx_video_analytics_video_id`

#### 3. **Users → Analytics** (One-to-Many)

- **Relationship**: `users.id` → `video_analytics.user_id`
- **Cardinality**: One user can have many analytics events
- **Cascade**: DELETE CASCADE (deleting user removes all their analytics)
- **Index**: `idx_video_analytics_user_id`

### Key Indexes for Performance

```sql
-- Video indexes
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_heygen_project_id ON videos(heygen_project_id);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);

-- Analytics indexes
CREATE INDEX idx_video_analytics_video_id ON video_analytics(video_id);
CREATE INDEX idx_video_analytics_user_id ON video_analytics(user_id);
CREATE INDEX idx_video_analytics_event_type ON video_analytics(event_type);
CREATE INDEX idx_video_analytics_created_at ON video_analytics(created_at DESC);

-- JSONB indexes for rich queries
CREATE INDEX idx_videos_highlights_gin ON videos USING GIN(highlights);
CREATE INDEX idx_videos_customizations_gin ON videos USING GIN(customizations);
CREATE INDEX idx_videos_raw_heygen_data_gin ON videos USING GIN(raw_heygen_data);
```

---

## 🔍 Query Examples

### Get User's Videos with Pagination

```sql
SELECT * FROM videos
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;
```

### Get Videos by Status

```sql
SELECT * FROM videos
WHERE status = $1
AND user_id = $2
ORDER BY created_at DESC;
```

### Get Video Analytics

```sql
SELECT va.*, v.title, v.filename
FROM video_analytics va
JOIN videos v ON va.video_id = v.id
WHERE va.user_id = $1
ORDER BY va.created_at DESC;
```

### Search Videos by Customization Data

```sql
SELECT * FROM videos
WHERE user_id = $1
AND customizations->>'prompt' ILIKE $2
ORDER BY created_at DESC;
```

---

## 🚨 Error Handling

### Standard Error Response

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

### Common Error Codes

- `INVALID_API_KEY`: Invalid or missing API key
- `VIDEO_NOT_FOUND`: Video with specified ID not found
- `UNAUTHORIZED`: User not authorized for this resource
- `VALIDATION_ERROR`: Request validation failed
- `HEYGEN_ERROR`: HeyGen API error
- `DATABASE_ERROR`: Database operation failed

---

## 🔄 Background Processing

### Status Monitoring

The system continuously monitors HeyGen processing status and updates video records automatically.

### Processing Flow

1. **Upload**: Video uploaded via API
2. **Submission**: Sent to HeyGen API
3. **Processing**: HeyGen processes the video
4. **Completion**: Results stored in database
5. **Notification**: Status updates available via API

---

## 📈 Performance Considerations

### Database Optimization

- **Connection Pooling**: Supabase handles connection pooling
- **Indexing**: Optimized indexes for common queries
- **JSONB**: Efficient JSON storage and querying
- **Pagination**: All list endpoints support pagination

### API Optimization

- **Async Processing**: Non-blocking video processing
- **Caching**: Response caching where appropriate
- **Rate Limiting**: Built-in rate limiting protection
- **Fast Streaming**: Optimized streaming service with 64KB chunks
- **Proxy URLs**: Branded download URLs that mask HeyGen sources
- **Smart Validation**: Skip validation for small files (thumbnails) for faster downloads
- **Connection Pooling**: Efficient HTTP client with connection reuse

---

## 📥 Download Endpoints

### 1. Download Video by Quality

**Endpoint:** `GET /api/v1/videos/{video_id}/download/{quality}`

**Description:** Download video file by quality (360p, 720p, 1080p, original)

**Parameters:**

- `video_id` (path): Video ID
- `quality` (path): Video quality (`360p`, `720p`, `1080p`, `original`)

**Headers:**

```http
x-api-key: your-api-key-here
Accept: video/mp4
```

**Response:** Binary video file stream

**Response Headers:**

```http
Content-Type: video/mp4
Content-Disposition: attachment; filename="Video_Title_720p.mp4"
Content-Length: 52428800
Cache-Control: public, max-age=3600
X-Content-Source: heygen-proxy
```

**Example:**

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8000/api/v1/videos/abc123/download/720p" \
  --output video_720p.mp4
```

### 2. Download Video Clip

**Endpoint:** `GET /api/v1/videos/{video_id}/download/clip/{clip_id}`

**Description:** Download specific video clip

**Parameters:**

- `video_id` (path): Video ID
- `clip_id` (path): Clip ID from highlights

**Headers:**

```http
x-api-key: your-api-key-here
Accept: video/mp4
```

**Response:** Binary video file stream

**Example:**

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8000/api/v1/videos/abc123/download/clip/clip-uuid-1" \
  --output clip.mp4
```

**Note:** This endpoint automatically selects the best available quality for the clip. For specific quality downloads, use the clip quality endpoint below.

### 2b. Download Video Clip by Quality

**Endpoint:** `GET /api/v1/videos/{video_id}/download/clip/{clip_id}/{quality}`

**Description:** Download specific video clip with specified quality

**Parameters:**

- `video_id` (path): Video ID
- `clip_id` (path): Clip ID from highlights
- `quality` (path): Video quality (`360p`, `720p`, `1080p`, `original`)

**Headers:**

```http
x-api-key: your-api-key-here
Accept: video/mp4
```

**Response:** Binary video file stream

**Example:**

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8000/api/v1/videos/abc123/download/clip/clip-uuid-1/720p" \
  --output clip_720p.mp4
```

### 3. Download Thumbnail

**Endpoint:** `GET /api/v1/videos/{video_id}/thumbnail/{thumbnail_type}`

**Description:** Download thumbnail image (main or preview)

**Parameters:**

- `video_id` (path): Video ID
- `thumbnail_type` (path): Thumbnail type (`main`, `preview`)

**Headers:**

```http
x-api-key: your-api-key-here
Accept: image/jpeg
```

**Response:** Binary image file stream

**Example:**

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8000/api/v1/videos/abc123/thumbnail/main" \
  --output thumbnail.jpg
```

### 4. Download Clip Thumbnail

**Endpoint:** `GET /api/v1/videos/{video_id}/thumbnail/clip/{clip_id}/{size}`

**Description:** Download clip-specific thumbnail image

**Parameters:**

- `video_id` (path): Video ID
- `clip_id` (path): Clip ID from highlights
- `size` (path): Thumbnail size (`360p_thumb`, `720p_thumb`, `1080p_thumb`, `original_thumb`)

**Headers:**

```http
x-api-key: your-api-key-here
Accept: image/jpeg
```

**Response:** Binary image file stream

**Example:**

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8000/api/v1/videos/abc123/thumbnail/clip/clip_456/720p_thumb" \
  --output clip_thumbnail.jpg
```

### 5. Get Download URLs

**Endpoint:** `GET /api/v1/videos/{video_id}/downloads`

**Description:** Get all available download URLs for a video - UI ready format

**Parameters:**

- `video_id` (path): Video ID

**Headers:**

```http
x-api-key: your-api-key-here
```

**Response:**

```json
{
  "video_id": "abc123",
  "downloads": {
    "qualities": [
      {
        "quality": "360p",
        "download_url": "/api/v1/videos/abc123/download/360p",
        "size_bytes": 15728640,
        "size_human": "15.7 MB",
        "filename": "video_360p.mp4",
        "content_type": "video/mp4"
      },
      {
        "quality": "720p",
        "download_url": "/api/v1/videos/abc123/download/720p",
        "size_bytes": 52428800,
        "size_human": "52.4 MB",
        "filename": "video_720p.mp4",
        "content_type": "video/mp4"
      }
    ],
    "clips": [
      {
        "id": "clip_456",
        "title": "Amazing Moment",
        "download_url": "/api/v1/videos/abc123/download/clip/clip_456",
        "thumbnail_url": "/api/v1/videos/abc123/thumbnail/clip/clip_456/720p_thumb",
        "duration": 60,
        "size_bytes": 8388608,
        "size_human": "8.2 MB"
      }
    ],
    "thumbnails": {
      "main": {
        "download_url": "/api/v1/videos/abc123/thumbnail/main",
        "size_human": "245 KB"
      },
      "preview": {
        "download_url": "/api/v1/videos/abc123/thumbnail/preview",
        "size_human": "180 KB"
      }
    }
  },
  "metadata": {
    "total_size": "76.1 MB",
    "available_qualities": ["360p", "720p"],
    "clip_count": 1,
    "last_updated": "2025-01-19T10:30:00.000Z"
  }
}
```

### 6. Get Download Info

**Endpoint:** `GET /api/v1/videos/{video_id}/download-info`

**Description:** Get download information and metadata for UI rendering

**Parameters:**

- `video_id` (path): Video ID

**Headers:**

```http
x-api-key: your-api-key-here
```

**Response:**

```json
{
  "video_id": "abc123",
  "download_info": {
    "has_downloads": true,
    "available_qualities": ["360p", "720p"],
    "clip_count": 1,
    "download_ready": true,
    "total_size_human": "76.1 MB",
    "thumbnail_available": true
  },
  "ui_data": {
    "can_download": true,
    "download_types": ["video", "clips", "thumbnails"],
    "recommended_quality": "720p",
    "fastest_download": "thumbnail"
  }
}
```

---

## 🎯 UI Integration Examples

### React/Next.js Component

```jsx
// VideoDownloadComponent.jsx
function VideoDownloadComponent({ video }) {
  const [downloads, setDownloads] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadDownloads = async () => {
    setLoading(true);
    const response = await fetch(`/api/v1/videos/${video.id}`, {
      headers: { "x-api-key": API_KEY },
    });
    const videoData = await response.json();
    setDownloads(videoData); // The video data already contains all download URLs
    setLoading(false);
  };

  const handleDownload = (url, filename) => {
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
  };

  if (!downloads) {
    return <button onClick={loadDownloads}>Load Downloads</button>;
  }

  return (
    <div className="download-section">
      {/* Video Clips */}
      <div className="clips-section">
        <h3>Video Clips</h3>
        {downloads.highlights.map((clip) => (
          <div key={clip.id} className="clip-card">
            <img
              src={downloads.thumbnails[clip.id]?.thumbnails["720p_thumb"]}
              alt={clip.name}
            />
            <div className="clip-info">
              <h4>{clip.name}</h4>
              <div className="quality-buttons">
                {Object.entries(
                  downloads.video_urls[clip.id]?.videos || {}
                ).map(([quality, url]) => (
                  <button
                    key={quality}
                    onClick={() =>
                      handleDownload(url, `${clip.name}_${quality}.mp4`)
                    }
                    className="quality-btn"
                  >
                    Download {quality}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Thumbnails */}
      <div className="thumbnails-section">
        <h3>Clip Thumbnails</h3>
        {downloads.highlights.map((clip) => (
          <div key={clip.id} className="thumbnail-item">
            <img
              src={downloads.thumbnails[clip.id]?.thumbnails["720p_thumb"]}
              alt={clip.name}
            />
            <h4>{clip.name}</h4>
            <div className="thumbnail-sizes">
              {Object.entries(
                downloads.thumbnails[clip.id]?.thumbnails || {}
              ).map(([size, url]) => (
                <button
                  key={size}
                  onClick={() =>
                    handleDownload(url, `${clip.name}_${size}.jpg`)
                  }
                  className="thumbnail-btn"
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Vue.js Component

```vue
<!-- VideoDownloads.vue -->
<template>
  <div class="downloads-section">
    <!-- Quality Downloads -->
    <div class="quality-section">
      <h3>Download Video</h3>
      <div class="quality-buttons">
        <button
          v-for="quality in downloads.downloads.qualities"
          :key="quality.quality"
          @click="downloadFile(quality.download_url, quality.filename)"
          class="download-btn"
        >
          📥 {{ quality.quality }} ({{ quality.size_human }})
        </button>
      </div>
    </div>

    <!-- Clips -->
    <div class="clips-section">
      <h3>Video Clips</h3>
      <div class="clips-grid">
        <div v-for="clip in video.highlights" :key="clip.id" class="clip-card">
          <img
            :src="video.thumbnails[clip.id]?.thumbnails['720p_thumb']"
            :alt="clip.name"
          />
          <div class="clip-details">
            <h4>{{ clip.name }}</h4>
            <div class="quality-buttons">
              <button
                v-for="(url, quality) in video.video_urls[clip.id]?.videos ||
                {}"
                :key="quality"
                @click="downloadFile(url, `${clip.name}_${quality}.mp4`)"
                class="quality-btn"
              >
                Download {{ quality }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ["video"],
  data() {
    return {
      downloads: null,
      loading: false,
    };
  },
  async mounted() {
    await this.loadDownloads();
  },
  methods: {
    async loadDownloads() {
      this.loading = true;
      const response = await fetch(`/api/v1/videos/${this.video.id}`, {
        headers: { "x-api-key": this.$store.state.apiKey },
      });
      const videoData = await response.json();
      this.downloads = videoData; // The video data already contains all download URLs
      this.loading = false;
    },
    downloadFile(url, filename) {
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
    },
  },
};
</script>
```

### JavaScript/Ajax Example

```javascript
// Simple JavaScript video data handler
async function loadVideoData(videoId, apiKey) {
  try {
    const response = await fetch(`/api/v1/videos/${videoId}`, {
      headers: {
        "x-api-key": apiKey,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const videoData = await response.json();
    return videoData;
  } catch (error) {
    console.error("Error loading video data:", error);
    throw error;
  }
}

// Usage
loadVideoData("abc123", "your-api-key")
  .then((video) => {
    console.log("Video data:", video);
    console.log("Available clips:", video.highlights);
    console.log("Video URLs:", video.video_urls);
    console.log("Thumbnails:", video.thumbnails);

    // Render UI with download options
    video.highlights.forEach((clip) => {
      const clipVideos = video.video_urls[clip.id]?.videos || {};
      const clipThumbnails = video.thumbnails[clip.id]?.thumbnails || {};

      console.log(`Clip: ${clip.name}`);
      console.log("Available qualities:", Object.keys(clipVideos));
      console.log("Available thumbnails:", Object.keys(clipThumbnails));
    });
  })
  .catch((error) => {
    console.error("Failed to load video data:", error);
  });
```

---

## 🔐 Security Features

### Authentication

- **API Key**: Secure API key authentication
- **Row Level Security**: Supabase RLS policies
- **User Isolation**: Users can only access their own data

### Data Protection

- **Input Validation**: Comprehensive request validation
- **SQL Injection**: Protected via parameterized queries
- **XSS Protection**: Input sanitization

---

## 🆕 Recent Updates & Fixes

### Latest Improvements (v1.0.0)

#### ✅ **Download System Overhaul**

- **New Download Endpoints**: Complete set of download endpoints for videos, clips, and thumbnails
- **Proxy URL System**: Branded download URLs that mask HeyGen sources
- **Fast Streaming**: Optimized streaming service with 64KB chunks for 3-5x faster downloads
- **Smart Validation**: Skip validation for small files (thumbnails) for instant downloads

#### ✅ **Authentication & Database**

- **Supabase Integration**: Complete migration from JSON to Supabase PostgreSQL
- **Row Level Security**: Secure user data isolation with RLS policies
- **API Key Authentication**: Robust API key system with user management
- **Automatic Initialization**: Self-initializing database connections

#### ✅ **Data Processing**

- **Nested Data Extraction**: Proper handling of HeyGen's complex nested data structures
- **Clean Response Format**: Simplified highlights data (removed file_meta and item_type)
- **Proxy URL Generation**: Automatic generation of branded download URLs
- **Error Handling**: Comprehensive error handling with detailed logging

#### ✅ **Performance Optimizations**

- **Streaming Fixes**: Resolved StreamClosed errors in download endpoints
- **Timeout Configuration**: Fixed httpx timeout configuration issues
- **Reduced Logging**: Optimized logging for better performance
- **Connection Pooling**: Efficient HTTP client management

#### ✅ **Production Ready**

- **Docker Support**: Production and development Docker configurations
- **Deployment Scripts**: Automated deployment with health checks
- **Comprehensive Documentation**: Complete API documentation with UI examples
- **Error Recovery**: Robust error handling and recovery mechanisms

### Breaking Changes

- **Highlights Format**: Simplified from complex objects to `{id, name}` only
- **URL Format**: All download URLs now use proxy format (`/api/v1/videos/{id}/download/...`)
- **Authentication**: Moved from placeholder to Supabase-based API key system

### Migration Notes

- **Database**: Migrate from JSON files to Supabase using provided migration scripts
- **API Keys**: Create user accounts in Supabase and generate API keys
- **URL Updates**: Update UI to use new proxy download URLs
- **Response Parsing**: Update highlights parsing to handle simplified format

---

This documentation provides everything needed to integrate with the API and understand the database structure for UI development.
