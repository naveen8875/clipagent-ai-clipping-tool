"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock3,
  FolderKanban,
  Plus,
  RefreshCw,
  Sparkles,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { UploadModal } from "@/components/dashboard/UploadModal";
import { VideoCard } from "@/components/dashboard/VideoCard";
import { useVideoProcessingState } from "@/hooks/use-video-processing-state";
import { Project } from "@/lib/project-types";
import { PlasticButton } from "@/components/ui/plastic-button";

const buildStats = (projects: Project[]) => {
  const processing = projects.filter(
    (project) => project.status === "processing" || project.status === "uploading"
  ).length;
  const completed = projects.filter((project) => project.status === "completed").length;
  const failed = projects.filter((project) => project.status === "error").length;

  return [
    {
      label: "Total Projects",
      value: projects.length,
      icon: FolderKanban,
      note: "All uploaded video jobs",
    },
    {
      label: "In Progress",
      value: processing,
      icon: Clock3,
      note: processing > 0 ? "Actively moving through the pipeline" : "Queue is currently clear",
    },
    {
      label: "Completed",
      value: completed,
      icon: CheckCircle2,
      note: "Ready to review and download",
    },
    {
      label: "Failed",
      value: failed,
      icon: XCircle,
      note: failed > 0 ? "Needs a retry or inspection" : "No failed runs",
    },
  ];
};

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const { toast } = useToast();

  const { canUpload, isProcessing, processingCount } = useVideoProcessingState({
    videos: projects,
    isLoading: loading,
  });

  const fetchProjects = useCallback(
    async (showErrorToast = true) => {
      setLoading(true);
      try {
        const response = await fetch("/api/projects");
        const result = await response.json();

        if (response.ok && result.success) {
          const sortedProjects = [...(result.projects || [])].sort(
            (a: Project, b: Project) =>
              new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
          );
          setProjects(sortedProjects);
        } else if (showErrorToast) {
          toast({
            title: "Error",
            description: result.error || "Failed to load projects",
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error("Error fetching projects:", error);
        if (showErrorToast) {
          toast({
            title: "Error",
            description: "Failed to load projects",
            variant: "destructive",
          });
        }
      } finally {
        setLoading(false);
      }
    },
    [toast]
  );

  useEffect(() => {
    fetchProjects(false);
  }, [fetchProjects]);

  useEffect(() => {
    if (!isProcessing) {
      return;
    }

    const interval = setInterval(() => {
      fetchProjects(false);
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchProjects, isProcessing]);

  const handleRefresh = async () => {
    await fetchProjects();
    toast({
      title: "Refreshed",
      description: "Project list updated successfully.",
    });
  };

  const handleUploadSuccess = async () => {
    setIsUploadModalOpen(false);
    toast({
      title: "Project created",
      description: "Your video was uploaded and processing has started.",
    });
    await fetchProjects(false);
  };

  const stats = buildStats(projects);

  return (
    <div className="dashboard-shell min-h-screen">
      <main className="container py-8 md:py-10" id="projects">
        <div className="space-y-8">
          <section className="product-hero-card">
            <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
              <div className="space-y-5">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="product-eyebrow">AI clipping workspace</span>
                  <span className="product-inline-pill">
                    <Activity className="h-3.5 w-3.5" />
                    Self-hosted and project-based
                  </span>
                </div>

                <div className="space-y-3">
                  <h1 className="product-title">
                    Turn long-form video into polished short clips from one clean dashboard.
                  </h1>
                  <p className="product-subtitle max-w-2xl">
                    Upload a source video, optionally attach subtitles, track progress across
                    the pipeline, and open completed runs to download the strongest clips.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <PlasticButton
                    text={isProcessing ? `Processing (${processingCount})` : "Create Project"}
                    onClick={() => setIsUploadModalOpen(true)}
                    disabled={!canUpload}
                  />
                  <Button
                    variant="outline"
                    onClick={handleRefresh}
                    disabled={loading}
                    className="rounded-full border-slate-300/70 bg-white text-slate-700 hover:bg-slate-50"
                  >
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                  </Button>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="product-info-card sm:col-span-2">
                  <div>
                    <p className="product-card-label">Pipeline status</p>
                    <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                      {isProcessing ? "Processing in progress" : "Ready for a new upload"}
                    </h2>
                    <p className="mt-2 text-sm text-slate-600">
                      {isProcessing
                        ? `${processingCount} project${processingCount > 1 ? "s are" : " is"} currently active. Completed runs stay available while the queue finishes.`
                        : "No active processing jobs. You can start a new project immediately."}
                    </p>
                  </div>
                </div>

                <div className="product-mini-card">
                  <p className="product-card-label">Best next action</p>
                  <p className="mt-2 text-base font-medium text-slate-900">
                    {canUpload ? "Upload a new source video" : "Wait for the current queue"}
                  </p>
                </div>
                <div className="product-mini-card">
                  <p className="product-card-label">Workflow</p>
                  <p className="mt-2 text-base font-medium text-slate-900">
                    Upload, process, review, download
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {stats.map((stat) => {
              const Icon = stat.icon;

              return (
                <article key={stat.label} className="product-stat-card">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="product-card-label">{stat.label}</p>
                      <p className="mt-3 text-3xl font-semibold text-slate-950">{stat.value}</p>
                    </div>
                    <div className="product-icon-chip">
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-slate-600">{stat.note}</p>
                </article>
              );
            })}
          </section>

          <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
            <div className="product-action-card">
              <div className="space-y-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="product-card-label">Create project</p>
                    <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                      Start a new clipping run
                    </h2>
                  </div>
                  <div className="product-icon-chip">
                    <Sparkles className="h-5 w-5" />
                  </div>
                </div>

                <p className="text-sm leading-6 text-slate-600">
                  Use the upload flow to send a local video to the backend, assign a content
                  category, and optionally attach subtitles to improve the first pass.
                </p>

                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="product-step-chip">1. Add source video</div>
                  <div className="product-step-chip">2. Choose category</div>
                  <div className="product-step-chip">3. Review generated clips</div>
                </div>

                <div className="flex flex-wrap gap-3">
                  <PlasticButton
                    text="Open Upload Flow"
                    onClick={() => setIsUploadModalOpen(true)}
                    disabled={!canUpload}
                  />
                </div>
              </div>
            </div>

            <div className="product-action-card">
              <div className="space-y-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="product-card-label">Queue overview</p>
                    <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                      {isProcessing ? "Live project activity" : "Everything is clear"}
                    </h2>
                  </div>
                  <div className="product-icon-chip">
                    <Clock3 className={`h-5 w-5 ${isProcessing ? "animate-pulse" : ""}`} />
                  </div>
                </div>

                <div className="product-queue-banner">
                  <div className="flex items-start gap-3">
                    <div className="product-status-dot" />
                    <div>
                      <p className="font-medium text-slate-950">
                        {processingCount} active project{processingCount === 1 ? "" : "s"}
                      </p>
                      <p className="mt-1 text-sm text-slate-600">
                        The backend currently processes one project at a time, which keeps
                        local runs predictable and easier to inspect.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="product-mini-card">
                    <p className="product-card-label">Current mode</p>
                    <p className="mt-2 text-base font-medium text-slate-900">
                      {isProcessing ? "Running queue" : "Idle and ready"}
                    </p>
                  </div>
                  <div className="product-mini-card">
                    <p className="product-card-label">Review behavior</p>
                    <p className="mt-2 text-base font-medium text-slate-900">
                      Completed projects stay accessible
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="product-eyebrow">Projects</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-950">Recent activity</h2>
              </div>
              <p className="max-w-xl text-sm text-slate-600">
                Open any completed project to review generated clips, or monitor runs that are
                still moving through the backend pipeline.
              </p>
            </div>

            {projects.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 2xl:grid-cols-3">
                {projects.map((project) => (
                  <VideoCard
                    key={project.id}
                    video={project}
                    onProjectDeleted={() => fetchProjects(false)}
                  />
                ))}
              </div>
            ) : (
              <div className="product-empty-state">
                <div className="product-icon-chip h-16 w-16">
                  <Plus className="h-8 w-8" />
                </div>
                <div className="space-y-3 text-center">
                  <h3 className="text-2xl font-semibold text-slate-950">No projects yet</h3>
                  <p className="mx-auto max-w-xl text-slate-600">
                    Create your first project to start the clipping workflow and build a library
                    of reviewable, download-ready short-form clips.
                  </p>
                </div>
                <PlasticButton
                  text="Create Your First Project"
                  onClick={() => setIsUploadModalOpen(true)}
                  disabled={!canUpload}
                />
              </div>
            )}
          </section>
        </div>
      </main>

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        isProcessing={isProcessing}
        processingCount={processingCount}
      />
    </div>
  );
}
