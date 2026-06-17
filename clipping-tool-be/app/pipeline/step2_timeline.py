"""
Step 2: Extract precise clip timelines from outlines and chunked SRT input.
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


class TimelineExtractor:
    """Extract precise timeline ranges from outlines and SRT subtitles."""

    def __init__(self, metadata_dir: Path = None, prompt_files: Dict = None):
        # Use Grok specifically for timeline extraction and clip localization.
        self.llm_client = LLMFactory.create_client(provider="grok")
        self.text_processor = TextProcessor()

        self.metadata_dir = metadata_dir or METADATA_DIR

        prompt_files_to_use = prompt_files if prompt_files is not None else PROMPT_FILES
        with open(prompt_files_to_use["timeline"], "r", encoding="utf-8") as f:
            self.timeline_prompt = f.read()

        self.srt_chunks_dir = self.metadata_dir / "step1_srt_chunks"
        self.timeline_chunks_dir = self.metadata_dir / "step2_timeline_chunks"
        self.llm_raw_output_dir = self.metadata_dir / "step2_llm_raw_output"

    def extract_timeline(self, outlines: List[Dict]) -> List[Dict]:
        """
        Extract topic-aligned time ranges.

        This implementation:
        - works against pre-chunked SRT data
        - processes multiple outlines per chunk
        - caches raw LLM responses for debugging
        - stores intermediate chunk JSON for resilience
        """
        logger.info("Starting timeline extraction...")

        if not outlines:
            logger.warning("Outline data is empty; cannot extract timeline.")
            return []

        if not self.srt_chunks_dir.exists():
            logger.error("SRT chunk directory does not exist: %s. Run Step 1 first.", self.srt_chunks_dir)
            return []

        self.timeline_chunks_dir.mkdir(parents=True, exist_ok=True)
        self.llm_raw_output_dir.mkdir(parents=True, exist_ok=True)

        outlines_by_chunk = defaultdict(list)
        for outline in outlines:
            chunk_index = outline.get("chunk_index")
            if chunk_index is not None:
                outlines_by_chunk[chunk_index].append(outline)
            else:
                logger.warning(
                    "  > Outline '%s' is missing chunk_index and will be skipped.",
                    outline.get("title", "unknown"),
                )

        for chunk_index, chunk_outlines in outlines_by_chunk.items():
            logger.info("Processing chunk %s with %s topics...", chunk_index, len(chunk_outlines))
            chunk_output_path = self.timeline_chunks_dir / f"chunk_{chunk_index}.json"

            try:
                srt_chunk_path = self.srt_chunks_dir / f"chunk_{chunk_index}.json"
                if not srt_chunk_path.exists():
                    logger.warning("  > Missing SRT chunk file: %s. Skipping chunk.", srt_chunk_path)
                    continue

                with open(srt_chunk_path, "r", encoding="utf-8") as f:
                    srt_chunk_data = json.load(f)

                if not srt_chunk_data:
                    logger.warning("  > SRT chunk file is empty: %s. Skipping chunk.", srt_chunk_path)
                    continue

                chunk_start_time = srt_chunk_data[0]["start_time"]
                chunk_end_time = srt_chunk_data[-1]["end_time"]

                raw_response = ""
                llm_cache_path = self.llm_raw_output_dir / f"chunk_{chunk_index}.txt"

                if llm_cache_path.exists():
                    logger.info("  > Found cached LLM response for chunk %s. Reusing it.", chunk_index)
                    with open(llm_cache_path, "r", encoding="utf-8") as f:
                        raw_response = f.read()
                else:
                    logger.info("  > No LLM cache for chunk %s. Calling the API...", chunk_index)

                    srt_text_for_prompt = ""
                    for sub in srt_chunk_data:
                        srt_text_for_prompt += (
                            f"{sub['index']}\n{sub['start_time']} --> {sub['end_time']}\n{sub['text']}\n\n"
                        )

                    llm_input_outlines = [
                        {"title": outline.get("title"), "subtopics": outline.get("subtopics")}
                        for outline in chunk_outlines
                    ]

                    input_data = {"outline": llm_input_outlines, "srt_text": srt_text_for_prompt}
                    parsed_items = None
                    max_parse_retries = 2

                    for retry_count in range(max_parse_retries + 1):
                        try:
                            raw_response = self.llm_client.call_with_retry(self.timeline_prompt, input_data)

                            if not raw_response:
                                logger.warning("  > Chunk %s returned an empty LLM response. Skipping.", chunk_index)
                                break

                            cache_file = self.llm_raw_output_dir / f"chunk_{chunk_index}_attempt_{retry_count}.txt"
                            with open(cache_file, "w", encoding="utf-8") as f:
                                f.write(raw_response)

                            parsed_items = self._parse_and_validate_response(
                                raw_response,
                                chunk_start_time,
                                chunk_end_time,
                                chunk_index,
                            )

                            if parsed_items:
                                with open(chunk_output_path, "w", encoding="utf-8") as f:
                                    json.dump(parsed_items, f, ensure_ascii=False, indent=2)

                                with open(llm_cache_path, "w", encoding="utf-8") as f:
                                    f.write(raw_response)

                                logger.info(
                                    "  > Successfully parsed %s timeline items for chunk %s.",
                                    len(parsed_items),
                                    chunk_index,
                                )
                                break

                            if retry_count < max_parse_retries:
                                logger.warning(
                                    "  > Chunk %s parse failed; retrying (%s/%s).",
                                    chunk_index,
                                    retry_count + 1,
                                    max_parse_retries + 1,
                                )
                                input_data["additional_instruction"] = (
                                    "\n\nImportant output requirements:\n"
                                    "1. Return a JSON array starting with [ and ending with ].\n"
                                    '2. Use standard ASCII double quotes only.\n'
                                    '3. Escape quotes inside strings as \\".\n'
                                    "4. Do not add explanations or Markdown code fences.\n"
                                    "5. Ensure the JSON is fully valid."
                                )
                            else:
                                logger.error(
                                    "  > Chunk %s still failed after %s attempts.",
                                    chunk_index,
                                    max_parse_retries + 1,
                                )
                                self._save_debug_response(raw_response, chunk_index, "final_parse_failure")
                        except Exception as parse_error:
                            logger.error(
                                "  > Exception while parsing chunk %s on attempt %s: %s",
                                chunk_index,
                                retry_count + 1,
                                parse_error,
                            )
                            if retry_count == max_parse_retries:
                                self._save_debug_response(
                                    raw_response if raw_response else "No response",
                                    chunk_index,
                                    "parse_exception",
                                )
                            continue

                    if not parsed_items:
                        logger.warning("  > Chunk %s could not be parsed and will be skipped.", chunk_index)
                        continue
                    continue

                parsed_items = self._parse_and_validate_response(
                    raw_response,
                    chunk_start_time,
                    chunk_end_time,
                    chunk_index,
                )
                if parsed_items:
                    with open(chunk_output_path, "w", encoding="utf-8") as f:
                        json.dump(parsed_items, f, ensure_ascii=False, indent=2)
                else:
                    logger.warning("  > Cached response for chunk %s could not be parsed.", chunk_index)
            except Exception as e:
                logger.error("  > Failed while processing chunk %s: %s", chunk_index, e)
                continue

        logger.info("Finished processing all chunks. Combining intermediate timeline files...")
        all_timeline_data = []
        chunk_files = sorted(self.timeline_chunks_dir.glob("*.json"))
        for chunk_file in chunk_files:
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)
                all_timeline_data.extend(chunk_data)

        logger.info(
            "Loaded %s topics from %s chunk files.",
            len(all_timeline_data),
            len(chunk_files),
        )

        if all_timeline_data:
            logger.info("Sorting all topics by start time...")
            try:
                all_timeline_data.sort(key=lambda item: self.text_processor.time_to_seconds(item["start_time"]))
                logger.info("Sorting complete.")

                logger.info("Assigning stable IDs in chronological order...")
                for i, timeline_item in enumerate(all_timeline_data):
                    timeline_item["id"] = str(i + 1)
                logger.info("Assigned stable IDs to %s items.", len(all_timeline_data))
            except Exception as e:
                logger.error("Failed to sort final timeline output: %s. Returning unsorted results.", e)

        return all_timeline_data

    def _parse_and_validate_response(
        self, response: str, chunk_start: str, chunk_end: str, chunk_index: int
    ) -> List[Dict]:
        """Parse and validate an LLM response for a single SRT chunk."""
        validated_items = []
        self._save_debug_response(response, chunk_index, "original_response")

        try:
            parsed_response = self.llm_client.parse_json_response(response)

            if not self.llm_client._validate_json_structure(parsed_response):
                logger.error("  > Chunk %s failed JSON structure validation.", chunk_index)
                self._save_debug_response(str(parsed_response), chunk_index, "invalid_structure")
                return []

            if not isinstance(parsed_response, list):
                logger.warning("  > Chunk %s returned a non-list payload.", chunk_index)
                self._save_debug_response(
                    f"Type: {type(parsed_response)}, Content: {parsed_response}",
                    chunk_index,
                    "not_list",
                )
                return []

            for timeline_item in parsed_response:
                if "outline" not in timeline_item or "start_time" not in timeline_item or "end_time" not in timeline_item:
                    logger.warning("  > Invalid timeline item returned by the LLM: %s", timeline_item)
                    continue

                timeline_item["chunk_index"] = chunk_index

                try:
                    if not self._validate_time_format(timeline_item["start_time"]):
                        logger.warning(
                            "  > Outline '%s' has invalid start time: %s",
                            timeline_item["outline"],
                            timeline_item["start_time"],
                        )
                        continue

                    if not self._validate_time_format(timeline_item["end_time"]):
                        logger.warning(
                            "  > Outline '%s' has invalid end time: %s",
                            timeline_item["outline"],
                            timeline_item["end_time"],
                        )
                        continue

                    start_time = self._convert_time_format(timeline_item["start_time"])
                    end_time = self._convert_time_format(timeline_item["end_time"])

                    start_sec = self.text_processor.time_to_seconds(start_time)
                    end_sec = self.text_processor.time_to_seconds(end_time)
                    chunk_start_sec = self.text_processor.time_to_seconds(chunk_start)
                    chunk_end_sec = self.text_processor.time_to_seconds(chunk_end)

                    if start_sec < chunk_start_sec:
                        logger.warning(
                            "  > Adjusting outline '%s' start time from %s to %s",
                            timeline_item["outline"],
                            start_time,
                            chunk_start,
                        )
                        timeline_item["start_time"] = chunk_start

                    if end_sec > chunk_end_sec:
                        logger.warning(
                            "  > Adjusting outline '%s' end time from %s to %s",
                            timeline_item["outline"],
                            end_time,
                            chunk_end,
                        )
                        timeline_item["end_time"] = chunk_end

                    logger.info(
                        "  > Located '%s' at %s -> %s",
                        timeline_item["outline"],
                        timeline_item["start_time"],
                        timeline_item["end_time"],
                    )
                    validated_items.append(timeline_item)
                except Exception as e:
                    logger.error("  > Failed to validate timeline item %s: %s", timeline_item, e)
                    continue

            return validated_items
        except Exception as e:
            logger.error("  > Failed to parse LLM response for chunk %s: %s", chunk_index, e)
            error_info = {
                "error": str(e),
                "error_type": type(e).__name__,
                "response_length": len(response),
                "response_preview": response[:200],
                "chunk_index": chunk_index,
                "chunk_start": chunk_start,
                "chunk_end": chunk_end,
            }
            self._save_debug_response(json.dumps(error_info, indent=2, ensure_ascii=False), chunk_index, "parse_error")
            return []

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate `HH:MM:SS,mmm` time strings."""
        import re

        pattern = r"^\d{2}:\d{2}:\d{2},\d{3}$"
        return bool(re.match(pattern, time_str))

    def _convert_time_format(self, time_str: str) -> str:
        """Convert SRT time strings to FFmpeg-compatible time strings."""
        if not time_str or time_str == "end":
            return time_str
        return time_str.replace(",", ".")

    def _save_debug_response(self, response: str, chunk_index: int, error_type: str) -> None:
        """Save raw or diagnostic LLM output for debugging."""
        try:
            debug_dir = self.metadata_dir / "debug_responses"
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_file = debug_dir / f"chunk_{chunk_index}_{error_type}.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(response)
            logger.info("Saved debug response to: %s", debug_file)
        except Exception as e:
            logger.error("Failed to save debug response: %s", e)

    def save_timeline(self, timeline_data: List[Dict], output_path: Optional[Path] = None) -> Path:
        """Persist timeline data to disk."""
        if output_path is None:
            output_path = METADATA_DIR / "step2_timeline.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(timeline_data, f, ensure_ascii=False, indent=2)

        logger.info("Saved timeline data to: %s", output_path)
        return output_path

    def load_timeline(self, input_path: Path) -> List[Dict]:
        """Load timeline data from disk."""
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)


def run_step2_timeline(
    outline_path: Path,
    metadata_dir: Path = None,
    output_path: Optional[Path] = None,
    prompt_files: Dict = None,
) -> List[Dict]:
    """Run Step 2: timeline extraction."""
    resolved_metadata_dir = metadata_dir or METADATA_DIR
    extractor = TimelineExtractor(resolved_metadata_dir, prompt_files)

    with open(outline_path, "r", encoding="utf-8") as f:
        outlines = json.load(f)

    timeline_data = extractor.extract_timeline(outlines)

    if output_path is None:
        output_path = resolved_metadata_dir / "step2_timeline.json"

    extractor.save_timeline(timeline_data, output_path)
    return timeline_data
