"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Download, Loader2, Scissors, Clock, Star } from "lucide-react";
import { Clip, Project } from "@/lib/project-types";

interface VideoDetailsPopupProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  projectName: string;
}

export function VideoDetailsPopup({
  isOpen,
  onClose,
  projectId,
  projectName,
}: VideoDetailsPopupProps) {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const fetchProject = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/projects/${projectId}`);
        if (!response.ok) {
          throw new Error("Failed to fetch project details");
        }
        const data = await response.json();
        setProject(data);
      } catch (error) {
        console.error("Project details error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [isOpen, projectId]);

  const downloadClip = (clipId: string) => {
    const link = document.createElement("a");
    link.href = `/api/projects/${projectId}/clips/${clipId}`;
    link.download = `${projectName}-${clipId}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const clipTitle = (clip: Clip) => clip.generated_title || clip.title || clip.outline;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{projectName}</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="py-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">Loading project details...</p>
          </div>
        ) : !project ? (
          <div className="py-12 text-center text-muted-foreground">
            Project details could not be loaded.
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant="secondary" className="capitalize">
                {project.status}
              </Badge>
              {project.video_category ? (
                <Badge variant="outline" className="capitalize">
                  {project.video_category.replace("_", " ")}
                </Badge>
              ) : null}
              {project.current_step ? (
                <Badge variant="outline">
                  Step {project.current_step} / {project.total_steps || 6}
                </Badge>
              ) : null}
            </div>

            {project.status !== "completed" ? (
              <Card>
                <CardContent className="p-5">
                  <p className="text-sm text-muted-foreground">
                    {project.status === "processing"
                      ? "This project is still running. Refresh later to review the generated clips."
                      : project.error_message || "This project has not finished processing yet."}
                  </p>
                </CardContent>
              </Card>
            ) : null}

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Generated Clips</h3>
                <span className="text-sm text-muted-foreground">
                  {project.clips?.length || 0} clips
                </span>
              </div>

              {project.clips && project.clips.length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                  {project.clips.map((clip) => (
                    <Card key={clip.id}>
                      <CardContent className="p-5 space-y-3">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h4 className="font-semibold">{clipTitle(clip)}</h4>
                            <p className="text-sm text-muted-foreground mt-1">{clip.outline}</p>
                          </div>
                          <Button size="sm" variant="outline" onClick={() => downloadClip(clip.id)}>
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        </div>

                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Scissors className="w-4 h-4" />
                            <span>{clip.start_time} - {clip.end_time}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4" />
                            <span>Score {clip.final_score.toFixed(2)}</span>
                          </div>
                          {clip.content?.length ? (
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              <span>{clip.content.length} transcript lines</span>
                            </div>
                          ) : null}
                        </div>

                        <p className="text-sm">{clip.recommend_reason}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="p-5 text-sm text-muted-foreground">
                    No clip metadata is available for this project yet.
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
