# Docker Deployment Notes

This file documents the intended Docker workflow for the backend.

## Current Status

The Dockerfile and compose file are aligned with the active `app/`-based backend and the English-only prompt layout.

## Prerequisites

- Docker 20.10+
- Docker Compose 2+
- At least one configured LLM provider key

## Expected Environment Variables

- `OPENROUTER_API_KEY`
- `XAI_API_KEY`
- `API_PROVIDER`
- `OPENROUTER_MODEL`
- `GROK_MODEL`
- `CHUNK_SIZE`
- `MIN_SCORE_THRESHOLD`
- `MAX_CLIPS_PER_COLLECTION`

## Intended Local Flow

1. Build the container image.
   ```bash
   docker compose build
   ```

2. Start the backend.
   ```bash
   docker compose up -d
   ```

3. Check logs.
   ```bash
   docker compose logs -f
   ```

4. Visit the API docs when the service is healthy.
   ```text
   http://localhost:8000/api/docs
   ```

## Expected Mounted Data

- `./uploads`
- `./output`
- `./data`
- `./input`

## Troubleshooting

- If the container fails early, inspect the Dockerfile path assumptions first.
- If clip generation fails, confirm `ffmpeg` is installed in the container.
- If LLM calls fail, verify the selected provider and matching API key.

## Notes

- Use `API_PROVIDER=openrouter` for the default workflow.
- Use `API_PROVIDER=grok` only if you want Grok as the general provider instead of just the timeline/scoring helper path.
