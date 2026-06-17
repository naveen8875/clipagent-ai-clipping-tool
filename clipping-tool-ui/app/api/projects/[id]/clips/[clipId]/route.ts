import { NextResponse } from "next/server";

const BACKEND_URL = process.env.MAIN_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string; clipId: string }> }
) {
  try {
    const { id, clipId } = await params;
    const response = await fetch(`${BACKEND_URL}/api/v1/projects/${id}/clips/${clipId}`);

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to fetch clip video" }, { status: response.status });
    }

    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "video/mp4",
        "Cache-Control": response.headers.get("Cache-Control") || "no-cache",
      },
    });
  } catch (error) {
    console.error("Clip proxy error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
