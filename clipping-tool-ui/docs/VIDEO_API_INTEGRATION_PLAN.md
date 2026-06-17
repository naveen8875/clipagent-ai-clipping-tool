# Video API Integration Plan

## 📋 Overview

This document outlines the integration plan for connecting our Next.js frontend with the AI Video Processing Backend API. We'll implement video upload and listing functionality with proper authentication, pagination, and filtering.

## 🎯 Goals

1. **Upload Integration**: Allow users to upload videos through our frontend
2. **Video Listing**: Display user's videos with pagination and filtering
3. **Authentication**: Use x-api-key header for secure API communication
4. **Credit System**: Integrate with existing credit management
5. **UI Enhancement**: Add pagination and filtering to the homepage

---

## 🔧 Technical Architecture

### Current System Analysis

**Frontend (Next.js):**

- ✅ User authentication via Supabase
- ✅ Credit system with RLS policies
- ✅ User profile management
- ✅ API key stored in `public.users.api_key`

**Backend API (External):**

- ✅ Video upload endpoint: `POST /api/v1/videos/upload`
- ✅ Video listing endpoint: `GET /api/v1/videos`
- ✅ Authentication via `x-api-key` header
- ✅ Pagination support
- ✅ Status filtering

### Integration Strategy

```
Frontend (Next.js) → Next.js API Routes → External Backend API
     ↓                    ↓                    ↓
User Uploads Video → Proxy with Auth → Process Video
     ↓                    ↓                    ↓
Credit Check → Deduct Credits → Store in DB
```

---

## 📁 File Structure Changes

### New Files to Create

```
app/api/videos/
├── route.ts                 # Video listing endpoint
├── upload/
│   └── route.ts            # Video upload endpoint
└── [id]/
    ├── route.ts            # Individual video details
    └── status/
        └── route.ts        # Video status check

components/videos/
├── VideoUploadForm.tsx     # Upload form component
├── VideoList.tsx          # Video listing component
├── VideoCard.tsx          # Individual video card
├── VideoFilters.tsx       # Filter component
└── VideoPagination.tsx    # Pagination component

lib/
├── video-api.ts           # Video API utilities
└── upload-utils.ts        # Upload helper functions
```

### Files to Modify

```
app/page.tsx               # Add video listing with pagination
components/dashboard/
├── Header.tsx             # Add upload button
└── VideoCard.tsx          # Update for new API structure
```

---

## 🔐 Authentication Flow

### API Key Management

1. **Server-Side Retrieval**: Next.js API routes fetch user's API key from `public.users.api_key`
2. **Header Injection**: Add `x-api-key` header to all backend requests
3. **User Isolation**: Ensure users can only access their own videos

### Implementation Pattern

```typescript
// lib/video-api.ts
export async function getAuthenticatedVideoRequest(userId: string) {
  const supabase = createServerClient();

  // Get user's API key
  const { data: user } = await supabase
    .from("public.users")
    .select("api_key")
    .eq("id", userId)
    .single();

  if (!user?.api_key) {
    throw new Error("User API key not found");
  }

  return {
    headers: {
      "x-api-key": user.api_key,
      "Content-Type": "application/json",
    },
  };
}
```

---

## 📤 Upload Integration

### Upload Flow

1. **Frontend Form**: User enters YouTube URL and fills metadata
2. **API Proxy**: Next.js route receives upload request
3. **Server-Side Credit Check**: Verify user has available credits (server-side validation)
4. **Backend Forward**: Forward to backend API with auth only if credits available
5. **Automatic Credit Deduction**: Database triggers handle credit deduction automatically
6. **Response**: Return upload status to frontend

### Upload Form Structure

```typescript
interface UploadFormData {
  video_input_type: "url"; // Only URL uploads supported
  video_key: string; // YouTube URL (required)
  name: string; // Video title
  input_language?: string;
  output_settings: {
    prompt: string;
    duration_types: string[];
    aspect_ratio: "landscape" | "portrait" | "square";
    is_captions_enabled: boolean;
  };
  source_type: "video_repurpose";
  title: string; // Custom title
  description: string; // Custom description
}
```

### Upload API Route

```typescript
// app/api/videos/upload/route.ts
export async function POST(request: Request) {
  // 1. Get authenticated user from session
  // 2. Server-side credit verification (prevent malicious requests)
  // 3. Validate URL upload data (YouTube URL validation)
  // 4. Forward to backend API only if credits available
  // 5. Database triggers automatically handle credit deduction
  // 6. Return response with proper error handling
}
```

---

## 📋 Video Listing Integration

### Listing Flow

1. **Frontend Request**: User navigates to dashboard
2. **API Proxy**: Next.js route fetches videos from backend
3. **Data Processing**: Transform backend response for frontend
4. **Pagination**: Handle pagination on both frontend and backend
5. **Filtering**: Apply status and date filters

### Video List API Route

```typescript
// app/api/videos/route.ts
export async function GET(request: Request) {
  // 1. Get authenticated user
  // 2. Extract query parameters (page, per_page, status)
  // 3. Forward to backend API with auth
  // 4. Transform response for frontend
  // 5. Return paginated results
}
```

### Response Transformation

**Backend Response:**

```json
{
  "videos": [...],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "has_next": true,
  "has_previous": false
}
```

**Frontend Response:**

```json
{
  "success": true,
  "data": {
    "videos": [...],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 25,
      "items_per_page": 10,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

## 🎨 UI Components Design

### Video Upload Form

**Features:**

- YouTube URL input (file uploads not supported)
- Video metadata fields (title, description, prompt)
- Output settings (duration, aspect ratio, captions)
- Real-time credit check
- Upload progress indicator
- Error handling

**Layout:**

```
┌─────────────────────────────────────┐
│ Video Upload                        │
├─────────────────────────────────────┤
│ YouTube URL: [________________]      │
│                                     │
│ Title: [________________]            │
│ Description: [________________]      │
│ Prompt: [________________]           │
├─────────────────────────────────────┤
│ Duration: [60s] [90s] [120s]        │
│ Aspect: [Landscape] [Portrait]       │
│ Captions: [✓] Enable                │
├─────────────────────────────────────┤
│ Credits Required: 1                  │
│ Available: 2 credits                 │
│ [Upload Video]                       │
└─────────────────────────────────────┘
```

### Video List Component

**Features:**

- Grid/list view toggle
- Status filtering (All, Processing, Completed, Failed)
- Date range filtering
- Search by title/description
- Pagination controls
- Bulk actions (delete, download)

**Layout:**

```
┌─────────────────────────────────────┐
│ My Videos                    [+ New]│
├─────────────────────────────────────┤
│ [All] [Processing] [Completed] [Failed] │
│ Search: [________________] [Filter] │
├─────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│ │Video│ │Video│ │Video│ │Video│      │
│ │  1  │ │  2  │ │  3  │ │  4  │      │
│ └─────┘ └─────┘ └─────┘ └─────┘      │
├─────────────────────────────────────┤
│ ← Previous  Page 1 of 3  Next →     │
└─────────────────────────────────────┘
```

### Video Card Component

**Features:**

- Thumbnail preview
- Status indicator
- Progress bar (for processing)
- Quick actions (view, download, delete)
- Metadata display (title, date, duration)

**Layout:**

```
┌─────────────────────────────────────┐
│ [Thumbnail]                         │
│                                     │
│ Video Title                    [⋮]  │
│ Uploaded: Jan 19, 2025              │
│ Status: [Completed]                  │
│                                     │
│ [View] [Download] [Delete]          │
└─────────────────────────────────────┘
```

---

## 🔄 State Management

### React Query Integration

**Query Keys:**

```typescript
const queryKeys = {
  videos: ["videos"] as const,
  videosList: (filters: VideoFilters) => ["videos", "list", filters] as const,
  videoDetail: (id: string) => ["videos", "detail", id] as const,
  videoStatus: (id: string) => ["videos", "status", id] as const,
};
```

**Mutations:**

```typescript
const mutations = {
  uploadVideo: () => ["videos", "upload"] as const,
  deleteVideo: (id: string) => ["videos", "delete", id] as const,
};
```

### State Structure

```typescript
interface VideoListState {
  videos: Video[];
  pagination: PaginationInfo;
  filters: VideoFilters;
  loading: boolean;
  error: string | null;
}

interface VideoFilters {
  status?: VideoStatus;
  search?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  per_page?: number;
}
```

---

## 📊 Pagination Strategy

### Backend Pagination

**Parameters:**

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response:**

```json
{
  "videos": [...],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "has_next": true,
  "has_previous": false
}
```

### Frontend Pagination

**Components:**

- `VideoPagination`: Page navigation controls
- `ItemsPerPageSelector`: Change items per page
- `PaginationInfo`: Show current page info

**Features:**

- Page numbers with ellipsis for large datasets
- Previous/Next navigation
- Jump to page input
- Items per page selection (10, 20, 50, 100)

---

## 🔍 Filtering System

### Available Filters

1. **Status Filter:**

   - All Videos
   - Uploaded
   - Processing
   - Completed
   - Failed

2. **Date Range Filter:**

   - Last 7 days
   - Last 30 days
   - Last 3 months
   - Custom range

3. **Search Filter:**

   - Title search
   - Description search
   - Filename search

4. **Sort Options:**
   - Newest first
   - Oldest first
   - Status
   - File size

### Filter Implementation

```typescript
interface VideoFilters {
  status?: "uploaded" | "processing" | "completed" | "failed";
  search?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: "created_at" | "status" | "filename";
  sort_order?: "asc" | "desc";
  page?: number;
  per_page?: number;
}
```

---

## 🚀 Implementation Phases

### Phase 1: Core API Integration

- [ ] Create video API routes (`/api/videos/upload`, `/api/videos`)
- [ ] Implement server-side authentication helper functions
- [ ] Implement server-side credit verification system
- [ ] Set up error handling and logging
- [ ] Test API connectivity and security

### Phase 2: Upload Functionality

- [ ] Create `VideoUploadForm` component
- [ ] Implement file upload handling
- [ ] Implement server-side credit checking and deduction
- [ ] Create upload progress indicators
- [ ] Add comprehensive error handling and validation
- [ ] Test credit security and prevent bypass attempts

### Phase 3: Video Listing

- [ ] Create `VideoList` component
- [ ] Implement `VideoCard` component
- [ ] Add basic pagination
- [ ] Create status indicators
- [ ] Add loading states

### Phase 4: Advanced Features

- [ ] Implement filtering system
- [ ] Add search functionality
- [ ] Create advanced pagination
- [ ] Add bulk actions
- [ ] Implement real-time status updates

### Phase 5: UI Polish

- [ ] Add responsive design
- [ ] Implement dark mode support
- [ ] Add animations and transitions
- [ ] Create empty states
- [ ] Add accessibility features

---

## 🔒 Security Considerations

### API Key Protection

- Store API keys securely in database
- Never expose API keys in frontend code
- Use server-side proxy for all backend requests
- Implement rate limiting on upload endpoints

### Credit Security

- **Server-Side Validation**: All credit checks happen in API routes, not frontend
- **Automatic Deduction**: Database triggers handle credit deduction automatically
- **Transaction Safety**: Database triggers ensure atomic operations
- **Malicious Request Prevention**: Frontend cannot bypass credit checks
- **Audit Trail**: Database triggers log all credit transactions automatically

### Server-Side Credit Verification Implementation

```typescript
// lib/credit-verification.ts
export async function verifyUserCredits(
  userId: string
): Promise<{ success: boolean; credits_remaining: number; error?: string }> {
  const supabase = createServerClient();

  try {
    // Check credits using RPC function
    const { data: creditCheck, error: creditError } = await supabase.rpc(
      "check_user_credits",
      { auth_user_id: userId }
    );

    if (creditError || !creditCheck?.can_upload) {
      return {
        success: false,
        credits_remaining: creditCheck?.credits_available || 0,
        error: "Insufficient credits",
      };
    }

    return {
      success: true,
      credits_remaining: creditCheck.credits_available,
    };
  } catch (error) {
    console.error("Credit verification error:", error);
    return {
      success: false,
      credits_remaining: 0,
      error: "Internal server error",
    };
  }
}
```

### Upload Route Security Implementation

```typescript
// app/api/videos/upload/route.ts
export async function POST(request: Request) {
  try {
    // 1. Get authenticated user from session
    const user = await getAuthenticatedUser(request);
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 2. Server-side credit verification (CRITICAL SECURITY STEP)
    const creditCheck = await verifyUserCredits(user.id);
    if (!creditCheck.success) {
      return NextResponse.json(
        {
          error: creditCheck.error,
          credits_remaining: creditCheck.credits_remaining,
        },
        { status: 402 }
      ); // Payment Required
    }

    // 3. Validate URL upload data (YouTube URL validation)
    const uploadData = await request.json();
    const validation = validateUrlUploadData(uploadData);
    if (!validation.valid) {
      return NextResponse.json({ error: validation.error }, { status: 400 });
    }

    // 4. Forward to backend API with authentication
    const authHeaders = await getAuthenticatedVideoRequest(user.id);
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/videos/upload`, {
      method: "POST",
      headers: authHeaders.headers,
      body: JSON.stringify(uploadData),
    });

    // 5. Handle backend response
    if (!backendResponse.ok) {
      return NextResponse.json(
        {
          error: "Backend processing failed",
        },
        { status: 500 }
      );
    }

    // 6. Success - database triggers will handle credit deduction
    const result = await backendResponse.json();
    return NextResponse.json({
      success: true,
      data: result,
      credits_remaining: creditCheck.credits_remaining - 1, // Approximate
    });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json(
      {
        error: "Internal server error",
      },
      { status: 500 }
    );
  }
}
```

### Input Validation

- Validate YouTube URL format and accessibility
- Sanitize user inputs (title, description, prompt)
- Check credit limits before processing
- Implement CSRF protection

### Error Handling

- Don't expose internal errors to users
- Log errors for debugging
- Implement graceful fallbacks
- Handle network timeouts

---

## 📈 Performance Optimizations

### Frontend Optimizations

- Implement virtual scrolling for large video lists
- Use React Query for caching and background updates
- Implement lazy loading for video thumbnails
- Add skeleton loaders for better UX

### Backend Optimizations

- Implement request caching where appropriate
- Use connection pooling for external API calls
- Add request timeout handling
- Implement retry logic for failed requests

---

## 🧪 Testing Strategy

### Unit Tests

- Test API route functions
- Test utility functions
- Test component rendering
- Test error handling

### Integration Tests

- Test upload flow end-to-end
- Test video listing with pagination
- Test filtering functionality
- Test credit deduction flow

### E2E Tests

- Test complete user journey
- Test error scenarios
- Test responsive design
- Test accessibility

---

## 📝 API Documentation Updates

### New Endpoints

1. **POST /api/videos/upload**

   - Upload video for processing
   - Requires authentication
   - Checks credits
   - Returns upload status

2. **GET /api/videos**

   - List user's videos
   - Supports pagination and filtering
   - Returns video metadata

3. **GET /api/videos/[id]**

   - Get individual video details
   - Returns full video information

4. **GET /api/videos/[id]/status**
   - Get real-time video status
   - For progress tracking

### Response Schemas

Update existing API documentation with new response formats and error codes.

---

## 🎯 Success Metrics

### Functional Metrics

- Upload success rate > 95%
- Video listing load time < 2 seconds
- Pagination response time < 500ms
- Filter application time < 300ms

### User Experience Metrics

- Upload form completion rate
- Video discovery rate (via search/filters)
- User engagement with video cards
- Error recovery success rate

---

## 🔄 Future Enhancements

### Phase 6+ Features

- Real-time video processing updates
- Video preview functionality
- Advanced analytics dashboard
- Bulk video operations
- Video sharing capabilities
- Mobile app integration

### Scalability Considerations

- Implement video CDN integration
- Add video compression options
- Implement background job processing
- Add video storage optimization
- Implement advanced caching strategies

---

This plan provides a comprehensive roadmap for integrating the video upload and listing APIs into our current system while maintaining security, performance, and user experience standards.
