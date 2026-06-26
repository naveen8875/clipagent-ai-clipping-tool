"""
Step 4: Title generation for high-scoring clips.
"""
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from app.config import METADATA_DIR, PROMPT_FILES
from app.utils.llm.factory import LLMFactory
from app.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class TitleGenerator:
    """Generate titles for clips selected by the scoring stage."""

    def __init__(self, metadata_dir: Optional[Path] = None, prompt_files: Dict = None):
        # Use Grok specifically for title generation because it performs better in English.
        self.llm_client = LLMFactory.create_client(provider="grok")
        self.text_processor = TextProcessor()

        prompt_files_to_use = prompt_files if prompt_files is not None else PROMPT_FILES
        with open(prompt_files_to_use["title"], "r", encoding="utf-8") as f:
            self.title_prompt = f.read()

        self.metadata_dir = metadata_dir or METADATA_DIR
        self.llm_raw_output_dir = self.metadata_dir / "step4_llm_raw_output"

    def generate_titles(self, high_score_clips: List[Dict]) -> List[Dict]:
        """Generate titles in chunked batches and preserve clip data on failures."""
        if not high_score_clips:
            return []

        logger.info("Starting title generation for %s high-scoring clips...", len(high_score_clips))
        self.llm_raw_output_dir.mkdir(parents=True, exist_ok=True)

        clips_by_chunk = defaultdict(list)
        for clip in high_score_clips:
            clips_by_chunk[clip.get("chunk_index", 0)].append(clip)

        all_clips_with_titles = []
        for chunk_index, chunk_clips in clips_by_chunk.items():
            logger.info("Processing chunk %s with %s clips...", chunk_index, len(chunk_clips))

            try:
                logger.info("  > Requesting titles from the LLM...")
                input_for_llm = [
                    {
                        "id": clip.get("id"),
                        "title": clip.get("outline"),
                        "content": clip.get("content"),
                        "recommend_reason": clip.get("recommend_reason"),
                    }
                    for clip in chunk_clips
                ]

                raw_response = self.llm_client.call_with_retry(self.title_prompt, input_for_llm)

                if raw_response:
                    llm_cache_path = self.llm_raw_output_dir / f"chunk_{chunk_index}.txt"
                    with open(llm_cache_path, "w", encoding="utf-8") as f:
                        f.write(raw_response)
                    logger.info("  > Saved raw LLM response to %s", llm_cache_path)
                    titles_map = self.llm_client.parse_json_response(raw_response)
                else:
                    titles_map = {}

                if not isinstance(titles_map, dict):
                    logger.warning("  > LLM returned a non-dict title payload: %s. Skipping chunk.", titles_map)
                    all_clips_with_titles.extend(chunk_clips)
                    continue

                for clip in chunk_clips:
                    clip_id = clip.get("id")
                    generated_title = titles_map.get(clip_id)
                    if generated_title and isinstance(generated_title, str):
                        clip["generated_title"] = generated_title
                        logger.info(
                            "  > Generated title for clip %s ('%s...'): %s",
                            clip_id,
                            clip.get("outline", "")[:20],
                            generated_title,
                        )
                    else:
                        clip["generated_title"] = clip.get("outline", f"clip_{clip_id}")
                        logger.warning(
                            "  > Could not parse a title for clip %s; falling back to the outline.",
                            clip_id,
                        )

                all_clips_with_titles.extend(chunk_clips)
            except Exception as e:
                logger.error("  > Failed to generate titles for chunk %s: %s", chunk_index, e)
                all_clips_with_titles.extend(chunk_clips)

        logger.info("Finished generating titles for all high-scoring clips.")
        return all_clips_with_titles

    def save_clips_with_titles(self, clips_with_titles: List[Dict], output_path: Path):
        """Persist titled clips to disk."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clips_with_titles, f, ensure_ascii=False, indent=2)
        logger.info("Saved titled clips to: %s", output_path)


def run_step4_title(
    high_score_clips_path: Path,
    output_path: Optional[Path] = None,
    metadata_dir: Optional[str] = None,
    prompt_files: Dict = None,
) -> List[Dict]:
    """
    Run Step 4: title generation.

    Args:
        high_score_clips_path: Path to the scored clip file.
        output_path: Output path, defaults to step4_titles.json.
        metadata_dir: Metadata directory path.
        prompt_files: Optional prompt file overrides.

    Returns:
        A list of clips with generated titles.
    """
    with open(high_score_clips_path, "r", encoding="utf-8") as f:
        high_score_clips = json.load(f)

    resolved_metadata_dir = Path(metadata_dir) if metadata_dir is not None else METADATA_DIR
    title_generator = TitleGenerator(metadata_dir=resolved_metadata_dir, prompt_files=prompt_files)

    clips_with_titles = title_generator.generate_titles(high_score_clips)

    if output_path is None:
        output_path = resolved_metadata_dir / "step4_titles.json"

    title_generator.save_clips_with_titles(clips_with_titles, output_path)
    return clips_with_titles
