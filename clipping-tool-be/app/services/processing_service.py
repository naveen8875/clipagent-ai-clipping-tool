"""
Processing Service

Orchestrates the video processing pipeline and manages project state.
"""

import logging
import asyncio
import traceback
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks

from app.services import project_service
from app.models import ProjectStatus
from app.services.transcription_service import transcription_service
from app.pipeline.step1_outline import run_step1_outline
from app.pipeline.step2_timeline import run_step2_timeline
from app.pipeline.step2_5_snapper import run_step2_5_snapper
from app.pipeline.step3_scoring import run_step3_scoring
from app.pipeline.step4_title import run_step4_title
from app.pipeline.step5_clustering import run_step5_clustering
from app.pipeline.step6_video import run_step6_video
# from app.pipeline.step1_outline import run_step1_outline
# from app.pipeline.step2_timeline import run_step2_timeline
# from app.pipeline.step3_score import run_step3_score
# from app.pipeline.step4_title import run_step4_title
# from app.pipeline.step5_topic import run_step5_topic
# from app.pipeline.step6_video import run_step6_video

logger = logging.getLogger(__name__)

class ProcessingService:
    """Service for managing video processing pipeline"""
    
    def __init__(self):
        self.processing_lock = asyncio.Lock()
        self.max_concurrent_processing = 1
        self.current_processing_count = 0
    
    async def start_processing(self, project_id: str, background_tasks: BackgroundTasks):
        """
        Start processing a project in the background
        
        Args:
            project_id: Project ID
            background_tasks: FastAPI background tasks
        """
        # Update status immediately
        status = ProjectStatus(
            status="processing",
            current_step=0,
            total_steps=6,
            step_name="Initializing",
            progress=0.0
        )
        project_service.update_processing_status(project_id, status)
        project_service.update_project(project_id, status="processing")
        
        # Add to background tasks
        background_tasks.add_task(self._process_project_task, project_id)
        
    async def _process_project_task(self, project_id: str, start_step: int = 1):
        """
        Internal task to run the full pipeline
        """
        async with self.processing_lock:
            try:
                self.current_processing_count += 1
                logger.info(f"Starting pipeline for project {project_id} from step {start_step}")
                
                project = project_service.get_project(project_id)
                project_dir = Path(project.video_path).parent.parent
                input_dir = project_dir / "input"
                output_dir = project_dir / "output"
                metadata_dir = output_dir / "metadata"
                clips_dir = output_dir / "clips"
                collections_dir = output_dir / "collections"
                
                # Ensure directories exist
                metadata_dir.mkdir(parents=True, exist_ok=True)
                clips_dir.mkdir(parents=True, exist_ok=True)
                collections_dir.mkdir(parents=True, exist_ok=True)
                
                # Get input file paths
                video_files = list(input_dir.glob("*.mp4")) + list(input_dir.glob("*.mkv")) + list(input_dir.glob("*.mov"))
                if not video_files:
                    raise Exception("No video file found in input directory")
                video_file = video_files[0]
                
                srt_files = list(input_dir.glob("*.srt"))
                srt_file = srt_files[0] if srt_files else None
                
                # Step 0: Transcription (if SRT missing)
                if not srt_file:
                    self._update_status(project_id, 0, "Transcribing Audio", 5)
                    logger.info(f"No SRT found for project {project_id}. Starting automatic transcription...")
                    
                    # Define target path (e.g. input/input.srt or video_name.srt)
                    # using input.srt to be safe and consistent
                    target_srt_path = input_dir / f"{video_file.stem}.srt"
                    
                    await asyncio.to_thread(
                        transcription_service.ensure_srt,
                        video_path=video_file,
                        srt_path=target_srt_path
                    )
                    
                    srt_file = target_srt_path
                    if not srt_file.exists():
                         raise Exception("Automatic transcription failed to generate SRT file")
                
                if not srt_file:
                     raise Exception("No SRT file found in input directory")

                # Define step handlers
                # Note: We need to verify the exact function signatures for each step
                
                # Step 1: Outline
                if start_step <= 1:
                    self._update_status(project_id, 1, "Extracting Outline", 10)
                    step1_output = metadata_dir / "step1_outline.json"
                    await asyncio.to_thread(
                        run_step1_outline,
                        srt_path=srt_file,
                        metadata_dir=metadata_dir,
                        output_path=step1_output
                    )
                
                # Step 2: Timeline
                if start_step <= 2:
                    self._update_status(project_id, 2, "Mapping Timestamps", 30)
                    step2_output = metadata_dir / "step2_timeline.json"
                    step1_output = metadata_dir / "step1_outline.json"
                    await asyncio.to_thread(
                        run_step2_timeline,
                        outline_path=step1_output,
                        metadata_dir=metadata_dir,
                        output_path=step2_output
                    )
                
                # Step 2.5: Smart Snapper
                step2_5_output = metadata_dir / "step2_5_timeline.json"
                if start_step <= 2:
                    self._update_status(project_id, 2, "Refining Timestamps", 40)
                    step2_output = metadata_dir / "step2_timeline.json"
                    if step2_output.exists():
                        await asyncio.to_thread(
                            run_step2_5_snapper,
                            timeline_path=step2_output,
                            metadata_dir=metadata_dir,
                            output_path=step2_5_output,
                            project_id=project_id
                        )
                    else:
                        logger.warning("Step 2 output missing, skipping snapper")
                
                # Step 3: Scoring
                if start_step <= 3:
                    self._update_status(project_id, 3, "Scoring Content", 50)
                    step3_output = metadata_dir / "step3_scoring.json"
                    # Use Snapper output if available, else Step 2 output
                    step2_5_output = metadata_dir / "step2_5_timeline.json" 
                    step2_output = metadata_dir / "step2_timeline.json"
                    
                    input_for_step3 = step2_5_output if step2_5_output.exists() else step2_output
                    
                    await asyncio.to_thread(
                        run_step3_scoring,
                        timeline_path=input_for_step3,
                        metadata_dir=metadata_dir,
                        output_path=step3_output
                    )
                
                # Step 4: Title
                if start_step <= 4:
                    self._update_status(project_id, 4, "Generating Titles", 70)
                    step4_output = metadata_dir / "step4_titles.json"
                    step3_output = metadata_dir / "step3_scoring.json"
                    await asyncio.to_thread(
                        run_step4_title,
                        high_score_clips_path=step3_output,
                        output_path=step4_output,
                        metadata_dir=str(metadata_dir)
                    )
                
                # Step 5: Clustering
                if start_step <= 5:
                    self._update_status(project_id, 5, "Clustering Topics", 85)
                    step5_output = metadata_dir / "step5_clustering.json"
                    step4_output = metadata_dir / "step4_titles.json"
                    await asyncio.to_thread(
                        run_step5_clustering,
                        clips_with_titles_path=step4_output,
                        output_path=step5_output,
                        metadata_dir=str(metadata_dir)
                    )
                
                # Step 6: Video Generation
                if start_step <= 6:
                    self._update_status(project_id, 6, "Generating Videos", 90)
                    step4_output = metadata_dir / "step4_titles.json"
                    step5_output = metadata_dir / "step5_clustering.json"
                    await asyncio.to_thread(
                        run_step6_video,
                        clips_with_titles_path=step4_output,
                        collections_path=step5_output,
                        input_video=video_file,
                        output_dir=output_dir,
                        clips_dir=str(clips_dir),
                        collections_dir=str(collections_dir),
                        metadata_dir=str(metadata_dir)
                    )

                # Completion
                self._update_status(project_id, 6, "Completed", 100)
                project_service.update_project(project_id, status="completed")
                
                logger.info(f"Pipeline completed successfully for project {project_id}")
                
            except Exception as e:
                logger.error(f"Pipeline failed for project {project_id}: {e}")
                traceback.print_exc()
                
                status = ProjectStatus(
                    status="error",
                    current_step=0, # To be refined
                    total_steps=6,
                    step_name="Failed",
                    progress=0.0,
                    error_message=str(e)
                )
                project_service.update_processing_status(project_id, status)
                project_service.update_project(project_id, status="error", error_message=str(e))
                
            finally:
                self.current_processing_count -= 1

    def _update_status(self, project_id: str, step: int, step_name: str, progress: float):
        """Helper to update status"""
        status = ProjectStatus(
            status="processing",
            current_step=step,
            total_steps=6,
            step_name=step_name,
            progress=progress
        )
        project_service.update_processing_status(project_id, status)
        
        # Also update project level current step
        project_service.update_project(project_id, current_step=step)

# Global processing service instance
processing_service = ProcessingService()
