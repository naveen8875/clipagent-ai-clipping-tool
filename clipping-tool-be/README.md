# ClipAgent Backend

This is the FastAPI backend for the open-source clipping tool monorepo.

It accepts uploaded videos and optional subtitle files, creates projects, runs
the clipping pipeline, and serves generated clip metadata and rendered clip
files back to the frontend.

## Main Responsibilities

- create and store projects
- accept local video uploads and optional `.srt` files
- run the 6-step clipping pipeline
- persist project metadata to disk
- expose project, processing, and clip-download APIs

## Local Run

### Prerequisites

- Python 3.10+ recommended
- FFmpeg installed and available on `PATH`
- at least one LLM provider key:
  - `OPENROUTER_API_KEY`, or
  - `XAI_API_KEY`

### Setup

```bash
cd clipping-tool-be
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the provider values you want to use in `.env`.

### Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Docs

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Important Endpoints

- `GET /api/v1/health`
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/process`
- `GET /api/v1/projects/{project_id}/status`
- `GET /api/v1/projects/{project_id}/clips/{clip_id}`

## Storage Model

- `data/projects.json`: project metadata
- `uploads/<project_id>/input/`: uploaded source files
- `uploads/<project_id>/output/`: generated clips and metadata

## Docker

```bash
docker compose up --build
```

See the monorepo [README](/Users/naveenchoudhary/Desktop/programming/Crazy/clipping-tool-retentionmaxxing/README.md:1)
for the full project quickstart and [docs/QUICKSTART.md](/Users/naveenchoudhary/Desktop/programming/Crazy/clipping-tool-retentionmaxxing/docs/QUICKSTART.md:1)
for the recommended local setup flow.
