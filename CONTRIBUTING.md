# Contributing

Thanks for improving this clipping tool.

The project is being shaped as a clean open-source repo for local or self-hosted
video clipping, so contributions should stay aligned with that default product
direction unless a change is clearly marked as optional.

## Development Setup

Follow [docs/QUICKSTART.md](/Users/naveenchoudhary/Desktop/programming/Crazy/clipping-tool-retentionmaxxing/docs/QUICKSTART.md:1)
to get the backend and frontend running locally.

## Repository Layout

- `clipping-tool-be/`: FastAPI backend, project storage, and processing pipeline
- `clipping-tool-ui/`: Next.js frontend and proxy routes
- `docs/`: canonical repo-level documentation

## Workflow

1. Create a focused branch.
2. Make the smallest change that fully solves the problem.
3. Update docs when behavior, setup, or architecture changes.
4. Run the checks relevant to what you changed.

## Recommended Checks

### Backend

```bash
cd clipping-tool-be
pytest
python3 -m py_compile app/main.py app/api/projects.py app/api/processing.py
```

### Frontend

```bash
cd clipping-tool-ui
npm run lint
npm run build
```

If a check cannot be run in your environment, mention that clearly in your pull
request or handoff.

## Contribution Guidelines

- keep the default product flow local-first and easy to self-host
- prefer removing dead code over preserving unused product surfaces
- keep prompts and user-facing docs in English
- preserve existing user changes unless the change explicitly requires touching them
- document any new environment variables

## Pull Request Notes

Please include:

- what changed
- why it changed
- any setup or migration notes
- what you tested
- what you could not test

## Large Changes

For major product-shape changes, architecture moves, or new integrations:

- update `README.md` if onboarding changes
- update `docs/ARCHITECTURE.md` if system boundaries change
- update `docs/QUICKSTART.md` if setup or runtime steps change
