"use client";

import { useState } from "react";
import { FileText, FileVideo, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { PlasticButton } from "@/components/ui/plastic-button";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess?: () => void;
  isProcessing?: boolean;
  processingCount?: number;
}

export function UploadModal({
  isOpen,
  onClose,
  onUploadSuccess,
  isProcessing = false,
  processingCount = 0,
}: UploadModalProps) {
  const [projectName, setProjectName] = useState("");
  const [videoCategory, setVideoCategory] = useState("default");
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [srtFile, setSrtFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const resetState = () => {
    setProjectName("");
    setVideoCategory("default");
    setVideoFile(null);
    setSrtFile(null);
    setIsSubmitting(false);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleSubmit = async () => {
    if (!projectName.trim() || !videoFile) {
      toast({
        title: "Missing required fields",
        description: "Please provide a project name and a video file.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("project_name", projectName.trim());
      formData.append("video_category", videoCategory);
      formData.append("video_file", videoFile);
      if (srtFile) {
        formData.append("srt_file", srtFile);
      }

      const response = await fetch("/api/projects", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to upload project");
      }

      if (onUploadSuccess) {
        onUploadSuccess();
      } else {
        handleClose();
      }
    } catch (error) {
      console.error("Project upload error:", error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="max-w-2xl border-slate-200 bg-white p-0 text-slate-900 shadow-2xl">
        <DialogHeader className="border-b border-slate-200 px-6 py-5">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <span className="product-eyebrow">Create project</span>
              <DialogTitle className="text-2xl font-semibold text-slate-950">
                Upload a new video
              </DialogTitle>
              <p className="max-w-xl text-sm text-slate-600">
                Add your source video, choose the most relevant category, and optionally
                attach subtitles to improve the backend pass.
              </p>
            </div>
            <div className="product-icon-chip">
              <Sparkles className="h-5 w-5" />
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 px-6 py-6">
          {isProcessing && (
            <div className="rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-800">
              {processingCount} project{processingCount > 1 ? "s are" : " is"} currently processing.
              New uploads can still be created, but they may wait for the active queue.
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="project-name">Project Name</Label>
            <Input
              id="project-name"
              placeholder="Founder interview clips"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              maxLength={100}
              className="border-slate-200 bg-white"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="video-category">Video Category</Label>
            <Select value={videoCategory} onValueChange={setVideoCategory}>
              <SelectTrigger id="video-category" className="border-slate-200 bg-white">
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent className="border-slate-200 bg-white text-slate-900">
                <SelectItem value="default">Default</SelectItem>
                <SelectItem value="knowledge">Knowledge</SelectItem>
                <SelectItem value="business">Business</SelectItem>
                <SelectItem value="opinion">Opinion</SelectItem>
                <SelectItem value="experience">Experience</SelectItem>
                <SelectItem value="speech">Speech</SelectItem>
                <SelectItem value="content_review">Content Review</SelectItem>
                <SelectItem value="entertainment">Entertainment</SelectItem>
                <SelectItem value="podcast">Podcast</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="video-file">Video File</Label>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-3 flex items-center gap-3">
                  <div className="product-icon-chip h-10 w-10">
                    <FileVideo className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-950">Primary source</p>
                    <p className="text-xs text-slate-500">MP4, AVI, MOV, or MKV</p>
                  </div>
                </div>
                <Input
                  id="video-file"
                  type="file"
                  accept=".mp4,.avi,.mov,.mkv"
                  onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                  className="border-slate-200 bg-white file:text-slate-700"
                />
                {videoFile ? <p className="mt-3 text-xs text-sky-700">{videoFile.name}</p> : null}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="srt-file">Subtitle File</Label>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-3 flex items-center gap-3">
                  <div className="product-icon-chip h-10 w-10">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-950">Optional transcript</p>
                    <p className="text-xs text-slate-500">Attach an `.srt` file if you have one</p>
                  </div>
                </div>
                <Input
                  id="srt-file"
                  type="file"
                  accept=".srt"
                  onChange={(e) => setSrtFile(e.target.files?.[0] || null)}
                  className="border-slate-200 bg-white file:text-slate-700"
                />
                {srtFile ? <p className="mt-3 text-xs text-sky-700">{srtFile.name}</p> : null}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="rounded-full border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </Button>
            <PlasticButton
              text={isSubmitting ? "Uploading..." : "Create Project"}
              onClick={handleSubmit}
              disabled={isSubmitting || !projectName.trim() || !videoFile}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
