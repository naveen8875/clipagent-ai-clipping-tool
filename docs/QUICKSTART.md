# Quickstart

This quickstart brings up the current open-source clipping flow:

1. start the FastAPI backend
2. start the Next.js frontend
3. upload a video
4. monitor processing and download clips

## Prerequisites

- Python 3.10+ recommended
- Node.js 20+ recommended
- FFmpeg installed and available on `PATH`
- one LLM provider key:
  - `OPENROUTER_API_KEY`, or
  - `XAI_API_KEY`

## 1. Start the Backend

```bash
cd clipping-tool-be
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and provide the provider values you want to use:

```bash
API_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=tngtech/deepseek-r1t2-chimera:free
```

Or:

```bash
API_PROVIDER=grok
XAI_API_KEY=your-key
GROK_MODEL=grok-build-0.1
```

Run the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs will be available at `http://localhost:8000/api/docs`.

## 2. Start the Frontend

Open a second terminal:

```bash
cd clipping-tool-ui
npm install
cp .env.example .env.local
```

For the default local flow, the only required frontend env is the backend URL:

```bash
MAIN_BACKEND_URL=http://localhost:8000
```

Run the frontend:

```bash
npm run dev
```

Open `http://localhost:3000`.

If Turbopack-specific development issues appear on your machine, keep using the
default `npm run dev` script. A separate `npm run dev:turbo` script exists for
people who explicitly want to try Turbopack.

## 3. Create a Project

From the homepage:

- click `Upload Project`
- choose a local video file
- optionally add an `.srt` subtitle file
- choose a category
- submit the project

The frontend will create the project through its `/api/projects` proxy route and
immediately trigger backend processing.

## 4. Monitor Processing

The homepage polls project status while work is running.

The backend currently processes one project at a time, so additional projects
may queue behind the current run.

## 5. Review and Download Clips

Once a project completes:

- open the project details
- review generated clips
- download each rendered clip from the UI

## Optional Auth

The default open-source clipping flow does not require sign-in.

Some optional Supabase-oriented auth API routes still exist in the frontend for
teams that want to extend the project into a hosted multi-user product later.

## Troubleshooting

### Backend does not start

- verify FFmpeg is installed
- verify your `.env` contains a valid LLM provider key
- check `http://localhost:8000/api/docs`

### Frontend cannot fetch projects

- confirm the backend is running on port `8000`
- confirm `MAIN_BACKEND_URL` or `BACKEND_URL` points to the backend
- check browser and terminal logs for `/api/projects` proxy errors

### Project uploads work but processing fails

- confirm the backend provider key is valid
- inspect backend logs
- inspect `uploads/<project_id>/logs/processing.log` when available
