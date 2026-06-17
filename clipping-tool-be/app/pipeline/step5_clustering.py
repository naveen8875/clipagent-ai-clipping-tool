"""
Step 5: Cluster related clips into collections.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.config import MAX_CLIPS_PER_COLLECTION, METADATA_DIR, PROMPT_FILES
from app.utils.llm.factory import LLMFactory

logger = logging.getLogger(__name__)


class ClusteringEngine:
    """Cluster clips into multi-clip collections."""

    def __init__(self, metadata_dir: Optional[Path] = None, prompt_files: Dict = None):
        self.llm_client = LLMFactory.get_default_client()

        prompt_files_to_use = prompt_files if prompt_files is not None else PROMPT_FILES
        with open(prompt_files_to_use["clustering"], "r", encoding="utf-8") as f:
            self.clustering_prompt = f.read()

        self.metadata_dir = metadata_dir or METADATA_DIR

    def cluster_clips(self, clips_with_titles: List[Dict]) -> List[Dict]:
        """Cluster clips with LLM assistance and keyword-based fallback grouping."""
        logger.info("Starting thematic clustering...")

        clips_for_clustering = []
        for clip in clips_with_titles:
            clips_for_clustering.append(
                {
                    "id": clip["id"],
                    "title": clip.get("generated_title", clip["outline"]),
                    "summary": clip.get("recommend_reason", ""),
                    "score": clip.get("final_score", 0),
                }
            )

        pre_clusters = self._pre_cluster_by_keywords(clips_for_clustering)

        full_prompt = self.clustering_prompt + "\n\nHere is the list of candidate clips:\n"
        for i, clip in enumerate(clips_for_clustering, 1):
            full_prompt += (
                f"{i}. Title: {clip['title']}\n"
                f"   Summary: {clip['summary']}\n"
                f"   Score: {clip['score']:.2f}\n\n"
            )

        if pre_clusters:
            full_prompt += "\n\nKeyword-based pre-clustering results (reference only):\n"
            for theme, clip_ids in pre_clusters.items():
                full_prompt += f"{theme}: {', '.join(clip_ids)}\n"

        try:
            response = self.llm_client.call_with_retry(full_prompt)
            collections_data = self.llm_client.parse_json_response(response)
            validated_collections = self._validate_collections(collections_data, clips_with_titles)

            if len(validated_collections) < 3:
                logger.warning("LLM clustering produced too few valid collections; using keyword fallback.")
                validated_collections = self._create_collections_from_pre_clusters(pre_clusters, clips_with_titles)

            logger.info("Completed thematic clustering with %s collections.", len(validated_collections))
            return validated_collections
        except Exception as e:
            logger.error("Thematic clustering failed: %s", e)
            if pre_clusters:
                logger.info("Using keyword-based fallback collections.")
                return self._create_collections_from_pre_clusters(pre_clusters, clips_with_titles)
            return self._create_default_collections(clips_with_titles)

    def _pre_cluster_by_keywords(self, clips: List[Dict]) -> Dict[str, List[str]]:
        """Build rough fallback clusters from broad English themes."""
        theme_keywords = {
            "Investing and finance": [
                "invest",
                "finance",
                "stock",
                "fund",
                "money",
                "profit",
                "market",
                "trading",
                "wealth",
                "returns",
            ],
            "Career growth": [
                "career",
                "work",
                "job",
                "skill",
                "learning",
                "education",
                "student",
                "professional",
                "promotion",
                "resume",
            ],
            "Social commentary": [
                "society",
                "social",
                "internet",
                "platform",
                "system",
                "industry",
                "trend",
                "public",
                "community",
                "culture",
            ],
            "Cross-cultural topics": [
                "culture",
                "difference",
                "travel",
                "language",
                "food",
                "country",
                "global",
                "japan",
                "korea",
                "western",
            ],
            "Live content and audience": [
                "live",
                "stream",
                "audience",
                "fan",
                "chat",
                "comment",
                "host",
                "reaction",
                "show",
                "broadcast",
            ],
            "Relationships and emotions": [
                "relationship",
                "dating",
                "emotion",
                "social",
                "psychology",
                "connection",
                "love",
                "feeling",
                "communication",
                "friendship",
            ],
            "Health and lifestyle": [
                "health",
                "exercise",
                "running",
                "diet",
                "lifestyle",
                "wellness",
                "sleep",
                "habit",
                "fitness",
                "stress",
            ],
            "Creators and platforms": [
                "creator",
                "content",
                "platform",
                "media",
                "video",
                "channel",
                "algorithm",
                "distribution",
                "publishing",
                "audience",
            ],
        }

        pre_clusters = {theme: [] for theme in theme_keywords.keys()}

        for clip in clips:
            text = f"{clip['title']} {clip['summary']}".lower()
            theme_scores = {}
            for theme, keywords in theme_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    theme_scores[theme] = score

            if theme_scores:
                best_theme = max(theme_scores.keys(), key=lambda k: theme_scores[k])
                pre_clusters[best_theme].append(clip["id"])

        return {theme: clip_ids for theme, clip_ids in pre_clusters.items() if len(clip_ids) >= 2}

    def _create_collections_from_pre_clusters(
        self, pre_clusters: Dict[str, List[str]], clips_with_titles: List[Dict]
    ) -> List[Dict]:
        """Create collections from keyword fallback clusters."""
        collections = []
        collection_id = 1

        theme_titles = {
            "Investing and finance": "Investing and Finance Insights",
            "Career growth": "Career Growth Notes",
            "Social commentary": "Social Commentary Highlights",
            "Cross-cultural topics": "Cross-Cultural Perspectives",
            "Live content and audience": "Live Audience Moments",
            "Relationships and emotions": "Relationships and Emotions",
            "Health and lifestyle": "Health and Lifestyle Tips",
            "Creators and platforms": "Creators and Platform Dynamics",
        }

        theme_summaries = {
            "Investing and finance": "Practical investing and finance moments grouped into one collection.",
            "Career growth": "Clips about skill building, career decisions, and professional growth.",
            "Social commentary": "Observations and opinions about culture, systems, and public behavior.",
            "Cross-cultural topics": "Interesting conversations about language, travel, and cultural differences.",
            "Live content and audience": "Moments focused on hosts, audiences, and live interaction dynamics.",
            "Relationships and emotions": "Clips exploring emotions, communication, and relationships.",
            "Health and lifestyle": "A collection centered on habits, exercise, and sustainable living.",
            "Creators and platforms": "Insights for creators navigating content production and distribution.",
        }

        for theme, clip_ids in pre_clusters.items():
            if len(clip_ids) > MAX_CLIPS_PER_COLLECTION:
                clip_ids = clip_ids[:MAX_CLIPS_PER_COLLECTION]

            collections.append(
                {
                    "id": str(collection_id),
                    "collection_title": theme_titles.get(theme, theme),
                    "collection_summary": theme_summaries.get(
                        theme, f"A curated collection of standout clips related to {theme}."
                    ),
                    "clip_ids": clip_ids,
                }
            )
            collection_id += 1

        return collections

    def _validate_collections(self, collections_data: List[Dict], clips_with_titles: List[Dict]) -> List[Dict]:
        """Validate LLM output and map returned titles back to clip ids."""
        validated_collections = []

        for i, collection in enumerate(collections_data):
            try:
                if not all(key in collection for key in ["collection_title", "collection_summary", "clips"]):
                    logger.warning("Collection %s is missing required fields; skipping.", i)
                    continue

                clip_titles = collection["clips"]
                valid_clip_ids = []

                for clip_title in clip_titles:
                    for clip in clips_with_titles:
                        if clip.get("generated_title", clip["outline"]) == clip_title or clip["outline"] == clip_title:
                            valid_clip_ids.append(clip["id"])
                            break

                if len(valid_clip_ids) < 2:
                    logger.warning("Collection %s has fewer than 2 valid clips; skipping.", i)
                    continue

                if len(valid_clip_ids) > MAX_CLIPS_PER_COLLECTION:
                    valid_clip_ids = valid_clip_ids[:MAX_CLIPS_PER_COLLECTION]

                validated_collections.append(
                    {
                        "id": str(i + 1),
                        "collection_title": collection["collection_title"],
                        "collection_summary": collection["collection_summary"],
                        "clip_ids": valid_clip_ids,
                    }
                )
            except Exception as e:
                logger.error("Failed to validate collection %s: %s", i, e)

        return validated_collections

    def _create_default_collections(self, clips_with_titles: List[Dict]) -> List[Dict]:
        """Create simple score-based collections when clustering fails entirely."""
        logger.info("Creating default fallback collections...")

        high_score = []
        medium_score = []

        for clip in clips_with_titles:
            score = clip.get("final_score", 0)
            if score >= 0.8:
                high_score.append(clip)
            elif score >= 0.6:
                medium_score.append(clip)

        collections = []

        if len(high_score) >= 2:
            collections.append(
                {
                    "id": "1",
                    "collection_title": "Top Scoring Clips",
                    "collection_summary": "A collection of the highest scoring standout clips.",
                    "clip_ids": [clip["id"] for clip in high_score[:MAX_CLIPS_PER_COLLECTION]],
                }
            )

        if len(medium_score) >= 2:
            collections.append(
                {
                    "id": "2",
                    "collection_title": "Strong Recommended Clips",
                    "collection_summary": "A curated set of solid clips that scored well overall.",
                    "clip_ids": [clip["id"] for clip in medium_score[:MAX_CLIPS_PER_COLLECTION]],
                }
            )

        return collections

    def save_collections(self, collections_data: List[Dict], output_path: Optional[Path] = None) -> Path:
        """Persist collection metadata to disk."""
        if output_path is None:
            output_path = self.metadata_dir / "collections.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(collections_data, f, ensure_ascii=False, indent=2)

        logger.info("Saved collection data to: %s", output_path)
        return output_path

    def load_collections(self, input_path: Path) -> List[Dict]:
        """Load collection metadata from disk."""
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)


def run_step5_clustering(
    clips_with_titles_path: Path,
    output_path: Optional[Path] = None,
    metadata_dir: Optional[str] = None,
    prompt_files: Dict = None,
) -> List[Dict]:
    """
    Run Step 5: clustering.

    Args:
        clips_with_titles_path: Path to the titled clips file.
        output_path: Output path.
        metadata_dir: Metadata directory path.
        prompt_files: Optional prompt file overrides.

    Returns:
        Collection metadata.
    """
    with open(clips_with_titles_path, "r", encoding="utf-8") as f:
        clips_with_titles = json.load(f)

    resolved_metadata_dir = Path(metadata_dir) if metadata_dir is not None else METADATA_DIR
    clusterer = ClusteringEngine(metadata_dir=resolved_metadata_dir, prompt_files=prompt_files)

    collections_data = clusterer.cluster_clips(clips_with_titles)

    if output_path is None:
        output_path = resolved_metadata_dir / "step5_collections.json"

    clusterer.save_collections(collections_data, output_path)
    return collections_data
