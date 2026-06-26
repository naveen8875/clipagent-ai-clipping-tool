#!/usr/bin/env python3
"""
Backfill clip videos and metadata for existing projects in uploads/.

This script is useful when the scoring threshold filtered out every clip, but
earlier pipeline metadata still contains usable timestamped clip candidates.
It cuts clips from the source video, writes them to output/clips, and refreshes
clips_metadata.json so the UI can display downloadable previews.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.video_processor import VideoProcessor


logger = logging.getLogger("backfill_clips")

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi")
METADATA_CANDIDATES = (
    "step4_titles.json",
    "step3_all_scored.json",
    "step2_5_timeline.json",
    "step2_timeline.json",
)


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render fallback clips for uploads projects.")
    parser.add_argument("--project-id", help="Only process a single project ID.")
    parser.add_argument(
        "--uploads-dir",
        default=str(PROJECT_ROOT / "uploads"),
        help="Uploads directory that contains project folders.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum final_score to keep when score data exists.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Maximum number of clips to render per project.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-render clips even if matching MP4s already exist.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def iter_projects(uploads_dir: Path, project_id: str | None) -> Iterable[Path]:
    if project_id:
        project_dir = uploads_dir / project_id
        if not project_dir.exists():
            raise FileNotFoundError(f"Project not found: {project_dir}")
        yield project_dir
        return

    for child in sorted(uploads_dir.iterdir()):
        if child.is_dir():
            yield child


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def first_video_file(input_dir: Path) -> Path | None:
    for extension in VIDEO_EXTENSIONS:
        matches = sorted(input_dir.glob(f"*{extension}"))
        if matches:
            return matches[0]
    return None


def first_existing_metadata(metadata_dir: Path) -> tuple[Path | None, list[dict[str, Any]]]:
    for filename in METADATA_CANDIDATES:
        candidate = metadata_dir / filename
        if not candidate.exists():
            continue
        payload = load_json(candidate)
        if isinstance(payload, list) and payload:
            return candidate, payload
    return None, []


def normalize_clip(clip: dict[str, Any], fallback_index: int) -> dict[str, Any]:
    clip_id = str(clip.get("id") or fallback_index + 1)
    outline = clip.get("outline") or f"Clip {clip_id}"
    generated_title = clip.get("generated_title") or clip.get("title") or outline

    return {
        "id": clip_id,
        "title": clip.get("title") or generated_title,
        "generated_title": generated_title,
        "start_time": clip["start_time"],
        "end_time": clip["end_time"],
        "final_score": float(clip.get("final_score", 0.0) or 0.0),
        "recommend_reason": clip.get("recommend_reason") or "Backfilled from existing project metadata.",
        "outline": outline,
        "content": clip.get("content") or [],
        "chunk_index": clip.get("chunk_index"),
    }


def select_clips(raw_clips: list[dict[str, Any]], min_score: float, limit: int) -> list[dict[str, Any]]:
    normalized = [normalize_clip(clip, index) for index, clip in enumerate(raw_clips)]

    scored = [clip for clip in normalized if clip["final_score"] >= min_score]
    if scored:
        scored.sort(key=lambda item: item["final_score"], reverse=True)
        return scored[:limit]

    return normalized[:limit]


def render_project(project_dir: Path, min_score: float, limit: int, overwrite: bool) -> dict[str, Any]:
    input_dir = project_dir / "input"
    metadata_dir = project_dir / "output" / "metadata"
    clips_dir = project_dir / "output" / "clips"
    collections_dir = project_dir / "output" / "collections"

    input_video = first_video_file(input_dir)
    if input_video is None:
        raise FileNotFoundError(f"No input video found in {input_dir}")

    metadata_path, raw_clips = first_existing_metadata(metadata_dir)
    if metadata_path is None:
        raise FileNotFoundError(f"No clip metadata candidates found in {metadata_dir}")

    selected_clips = select_clips(raw_clips, min_score=min_score, limit=limit)
    if not selected_clips:
        logger.warning("No clips selected for project %s", project_dir.name)
        save_json(metadata_dir / "clips_metadata.json", [])
        save_json(metadata_dir / "collections_metadata.json", [])
        return {"project_id": project_dir.name, "clips_rendered": 0, "source": metadata_path.name}

    processor = VideoProcessor(clips_dir=str(clips_dir), collections_dir=str(collections_dir))
    clips_dir.mkdir(parents=True, exist_ok=True)
    collections_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    final_metadata: list[dict[str, Any]] = []

    for clip in selected_clips:
        safe_title = VideoProcessor.sanitize_filename(clip["generated_title"])
        output_path = clips_dir / f"{clip['id']}_{safe_title}.mp4"

        if output_path.exists() and not overwrite:
            logger.info("Reusing existing clip for project %s: %s", project_dir.name, output_path.name)
            rendered += 1
            final_metadata.append(clip)
            continue

        success = VideoProcessor.extract_clip(
            input_video=input_video,
            output_path=output_path,
            start_time=clip["start_time"],
            end_time=clip["end_time"],
        )
        if success:
            rendered += 1
            final_metadata.append(clip)

    save_json(metadata_dir / "clips_metadata.json", final_metadata)
    save_json(metadata_dir / "collections_metadata.json", [])

    return {
        "project_id": project_dir.name,
        "clips_rendered": rendered,
        "source": metadata_path.name,
        "clips_selected": len(selected_clips),
    }


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    uploads_dir = Path(args.uploads_dir).resolve()
    if not uploads_dir.exists():
        logger.error("Uploads directory does not exist: %s", uploads_dir)
        return 1

    results: list[dict[str, Any]] = []
    failures: list[tuple[str, str]] = []

    for project_dir in iter_projects(uploads_dir, args.project_id):
        try:
            result = render_project(
                project_dir=project_dir,
                min_score=args.min_score,
                limit=args.limit,
                overwrite=args.overwrite,
            )
            results.append(result)
            logger.info(
                "Project %s backfilled from %s: %s/%s clips ready",
                result["project_id"],
                result["source"],
                result["clips_rendered"],
                result.get("clips_selected", result["clips_rendered"]),
            )
        except Exception as exc:
            failures.append((project_dir.name, str(exc)))
            logger.error("Failed to backfill project %s: %s", project_dir.name, exc)

    logger.info("Processed %s project(s); %s failure(s).", len(results), len(failures))
    if failures:
        for project_id, error in failures:
            logger.error("  %s: %s", project_id, error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
