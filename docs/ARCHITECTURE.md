# Architecture

This repository is a two-part clipping system:

- `clipping-tool-be/`: FastAPI backend and clipping pipeline
- `clipping-tool-ui/`: Next.js frontend and backend proxy layer

## High-Level Flow

1. a user uploads a video and optional subtitle file in the frontend
2. the frontend posts multipart form data to `clipping-tool-ui/app/api/projects/route.ts`
3. that route proxies the upload to `POST /api/v1/projects` on the backend
4. the frontend proxy then calls `POST /api/v1/projects/{id}/process`
5. the backend runs the clipping pipeline in the background
6. the frontend polls project status and fetches project details
7. completed clips are downloaded through frontend proxy routes backed by the backend clip endpoints

## Frontend Shape

The active frontend product path is intentionally small:

- `app/page.tsx`: main project dashboard
- `components/dashboard/UploadModal.tsx`: local upload flow
- `components/dashboard/VideoCard.tsx`: project summary
- `components/dashboard/VideoDetailsPopup.tsx`: clip review and download
- `app/api/projects/**`: proxy routes that translate frontend calls to backend project APIs

Legacy hosted-product pages still exist only as archive placeholders for routes
like `/auth` and `/profile`. They are not part of the clipping workflow.

## Backend Shape

The backend is organized around projects and a 6-step processing pipeline.

### API Layer

- `app/main.py`: FastAPI app entry point
- `app/api/projects.py`: project CRUD, upload, and clip file serving
- `app/api/processing.py`: process start, retry, status, and logs

### Service Layer

- `app/services/project_service.py`: project persistence and filesystem management
- `app/services/processing_service.py`: orchestration of project processing

### Pipeline Layer

- `app/pipeline/step1_outline.py`
- `app/pipeline/step2_timeline.py`
- `app/pipeline/step3_scoring.py`
- `app/pipeline/step4_title.py`
- `app/pipeline/step5_clustering.py`
- `app/pipeline/step6_video.py`

### Configuration

- `app/config.py`: provider settings, categories, path config, and prompt mapping
- `prompts/en/`: active English prompt templates

## Storage Model

The system uses filesystem storage plus JSON metadata.

### Backend Metadata

- `clipping-tool-be/data/projects.json`: top-level project metadata store

### Per-Project Files

- `clipping-tool-be/uploads/<project_id>/input/`: uploaded source files
- `clipping-tool-be/uploads/<project_id>/output/clips/`: rendered clip files
- `clipping-tool-be/uploads/<project_id>/output/metadata/`: generated clip and collection metadata
- `clipping-tool-be/uploads/<project_id>/logs/`: processing logs when produced

## Processing Model

The backend currently allows only one active processing job at a time.

That behavior is managed in `project_service.py` and reflected in the frontend,
which warns users that new work may queue behind the current project.

## Provider Model

The current active LLM path is:

- OpenRouter
- xAI Grok

The backend reads provider configuration from environment variables:

- `API_PROVIDER`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `XAI_API_KEY`
- `GROK_MODEL`

## Why the Frontend Uses Proxy Routes

The Next.js app does not call the FastAPI backend directly from browser code for
its main flow. Instead, it uses `app/api/projects/**` proxy routes so the UI can:

- centralize backend URL configuration
- keep request/response shaping in one place
- remain flexible if deployment topology changes later

## Open-Source Product Boundary

The intended open-source product boundary is:

- local or self-hosted video upload
- project creation and processing
- clip review and download

Billing, credits, and hosted multi-user account features are outside the main
product path and have been removed or isolated from the runtime experience.
