"use client";

import { useState } from "react";
import {
  Calendar,
  Clapperboard,
  FileWarning,
  Loader2,
  MoreVertical,
  Play,
  Sparkles,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent } from "@/components/ui/card";
import { VideoDetailsPopup } from "./VideoDetailsPopup";
import { Project } from "@/lib/project-types";
import { PlasticButton } from "@/components/ui/plastic-button";

interface VideoCardProps {
  video: Project;
  onProjectDeleted?: () => void;
}

export function VideoCard({ video, onProjectDeleted }: VideoCardProps) {
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

  const getStatusStyles = (status: string) => {
    switch (status) {
      case "completed":
        return {
          badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
          icon: <Sparkles className="h-8 w-8 text-emerald-500" />,
          message: "Completed and ready to review",
        };
      case "processing":
        return {
          badge: "bg-sky-50 text-sky-700 border-sky-200",
          icon: <Loader2 className="h-8 w-8 animate-spin text-sky-500" />,
          message: "Currently moving through the pipeline",
        };
      case "error":
        return {
          badge: "bg-rose-50 text-rose-700 border-rose-200",
          icon: <FileWarning className="h-8 w-8 text-rose-500" />,
          message: "Run failed and may need another attempt",
        };
      default:
        return {
          badge: "bg-slate-100 text-slate-700 border-slate-200",
          icon: <Clapperboard className="h-8 w-8 text-slate-500" />,
          message: "Uploaded and waiting for processing",
        };
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "Completed";
      case "processing":
        return "Processing";
      case "error":
        return "Failed";
      default:
        return "Uploaded";
    }
  };

  const progressWidth =
    video.status === "completed"
      ? 100
      : video.status === "error"
      ? 28
      : Math.max(12, Math.round(((video.current_step || 1) / (video.total_steps || 6)) * 100));

  const handleDelete = async () => {
    const confirmed = window.confirm(`Delete project "${video.name}"?`);
    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/projects/${video.id}`, { method: "DELETE" });
      if (!response.ok) {
        throw new Error("Failed to delete project");
      }
      onProjectDeleted?.();
    } catch (error) {
      console.error("Delete project error:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const statusStyles = getStatusStyles(video.status);

  return (
    <>
      <Card className="product-project-card overflow-hidden border-slate-200 bg-white shadow-sm">
        <div className="product-project-stage">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <Badge
                variant="outline"
                className={`rounded-full px-3 py-1 text-xs font-medium ${statusStyles.badge}`}
              >
                {getStatusText(video.status)}
              </Badge>
              <div className="space-y-2">
                <h3 className="line-clamp-1 text-lg font-semibold text-slate-950">{video.name}</h3>
                <p className="text-sm text-slate-600">{statusStyles.message}</p>
              </div>
            </div>
            <div className="product-icon-chip shrink-0">{statusStyles.icon}</div>
          </div>

          {video.video_category ? (
            <div className="mt-4">
              <Badge
                variant="secondary"
                className="rounded-full border border-slate-200 bg-white capitalize text-slate-700"
              >
                {video.video_category.replace("_", " ")}
              </Badge>
            </div>
          ) : null}
        </div>

        <CardContent className="space-y-5 p-5">
          <p className="line-clamp-2 text-sm text-slate-600">
            {video.status === "completed"
              ? "Open this project to review the generated clips and download the strongest candidates."
              : video.status === "processing"
              ? "The backend is currently analyzing this source video and generating clip metadata."
              : video.error_message || "This upload is queued and will start when the backend is free."}
          </p>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="product-meta-chip">
              <Calendar className="h-3.5 w-3.5" />
              <span>{formatDate(video.created_at)}</span>
            </div>
            <div className="product-meta-chip">
              <Clapperboard className="h-3.5 w-3.5" />
              <span>{video.clips?.length || 0} clips tracked</span>
            </div>
            {video.current_step ? (
              <div className="product-meta-chip sm:col-span-2">
                <Play className="h-3.5 w-3.5" />
                <span>Step {video.current_step} of {video.total_steps || 6}</span>
              </div>
            ) : null}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.22em] text-slate-500">
              <span>Progress</span>
              <span>{progressWidth}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-[linear-gradient(90deg,#60a5fa_0%,#2563eb_60%,#1d4ed8_100%)]"
                style={{ width: `${progressWidth}%` }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between gap-3">
            <PlasticButton text="Open Project" onClick={() => setIsPopupOpen(true)} />

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-10 w-10 rounded-full border border-slate-200 p-0 text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                >
                  {isDeleting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <MoreVertical className="h-4 w-4" />
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="border-slate-200 bg-white text-slate-900">
                <DropdownMenuItem onClick={() => setIsPopupOpen(true)}>
                  <Play className="mr-2 h-4 w-4" />
                  Open Project
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDelete} className="text-rose-600 focus:text-rose-700">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardContent>
      </Card>

      <VideoDetailsPopup
        isOpen={isPopupOpen}
        onClose={() => setIsPopupOpen(false)}
        projectId={video.id}
        projectName={video.name}
      />
    </>
  );
}
