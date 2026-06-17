"use client";

import { useState, useEffect, useMemo } from "react";
import { Project } from "@/lib/project-types";

type ProcessingAwareProject = Pick<Project, "id" | "status" | "created_at" | "updated_at">;

interface UseVideoProcessingStateProps {
  videos: ProcessingAwareProject[] | null;
  isLoading: boolean;
}

export function useVideoProcessingState({ videos, isLoading }: UseVideoProcessingStateProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingCount, setProcessingCount] = useState(0);

  // Memoize the processing state calculation
  const processingState = useMemo(() => {
    if (!videos || isLoading) {
      return {
        isProcessing: false,
        processingCount: 0,
        canUpload: false,
        processingVideos: []
      };
    }

    const processingVideos = videos.filter(
      (video) => video.status === "processing" || video.status === "uploading"
    );
    const hasProcessing = processingVideos.length > 0;

    return {
      isProcessing: hasProcessing,
      processingCount: processingVideos.length,
      canUpload: !hasProcessing,
      processingVideos
    };
  }, [videos, isLoading]);

  // Update state when processing state changes
  useEffect(() => {
    setIsProcessing(processingState.isProcessing);
    setProcessingCount(processingState.processingCount);
  }, [processingState]);

  return {
    isProcessing,
    processingCount,
    canUpload: processingState.canUpload,
    processingVideos: processingState.processingVideos,
    isLoading
  };
}
