# Clipping Tool UI

This folder contains the Next.js frontend for the clipping tool monorepo.

## Main Flow

The frontend is centered around a project-based clipping workflow:

- create a project by uploading a video file
- optionally upload an SRT subtitle file
- start processing immediately through the backend
- monitor project status
- open a project and download generated clips

## Backend Integration

The UI now talks to the backend through project-oriented proxy routes:

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/:id`
- `GET /api/projects/:id/status`
- `POST /api/projects/:id/process`
- `GET /api/projects/:id/clips/:clipId`

These routes proxy to the FastAPI backend in `clipping-tool-be/`.

## Current State

The main clipping product path is already wired to the backend project model.

Legacy hosted-product code has been reduced substantially. What remains is mostly:

- optional auth API routes
- a few archive placeholder pages for old account paths

Those pieces are no longer part of the primary clipping workflow.

## Documentation

- archived UI planning and implementation notes: `docs/`
- monorepo overview: `../README.md`

## Local Development

- `npm run dev`: stable local development server
- `npm run dev:turbo`: optional Turbopack path
