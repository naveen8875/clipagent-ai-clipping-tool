import { NextResponse } from "next/server";

const BACKEND_URL = process.env.MAIN_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/projects`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch projects from backend" },
        { status: response.status }
      );
    }

    const projects = await response.json();
    return NextResponse.json({ success: true, projects });
  } catch (error) {
    console.error("Projects list proxy error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const incomingFormData = await request.formData();
    const backendFormData = new FormData();

    const videoFile = incomingFormData.get("video_file");
    const srtFile = incomingFormData.get("srt_file");
    const projectName = incomingFormData.get("project_name");
    const videoCategory = incomingFormData.get("video_category");

    if (!(videoFile instanceof File) || !projectName) {
      return NextResponse.json(
        { error: "video_file and project_name are required" },
        { status: 400 }
      );
    }

    backendFormData.append("video_file", videoFile);
    if (srtFile instanceof File && srtFile.size > 0) {
      backendFormData.append("srt_file", srtFile);
    }
    backendFormData.append("project_name", String(projectName));
    backendFormData.append("video_category", String(videoCategory || "default"));

    const createResponse = await fetch(`${BACKEND_URL}/api/v1/projects`, {
      method: "POST",
      body: backendFormData,
    });

    const createBody = await createResponse.json();

    if (!createResponse.ok) {
      return NextResponse.json(
        { error: createBody.detail || "Failed to create project" },
        { status: createResponse.status }
      );
    }

    const processResponse = await fetch(`${BACKEND_URL}/api/v1/projects/${createBody.id}/process`, {
      method: "POST",
    });

    if (!processResponse.ok) {
      const processBody = await processResponse.text();
      return NextResponse.json(
        {
          error: "Project was created, but processing failed to start",
          project: createBody,
          details: processBody,
        },
        { status: 502 }
      );
    }

    return NextResponse.json({
      success: true,
      project: createBody,
      message: "Project uploaded and processing started",
    });
  } catch (error) {
    console.error("Project upload proxy error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
