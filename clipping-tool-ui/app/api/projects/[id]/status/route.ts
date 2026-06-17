import { NextResponse } from "next/server";

const BACKEND_URL = process.env.MAIN_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const response = await fetch(`${BACKEND_URL}/api/v1/projects/${id}/status`, {
      cache: "no-store",
    });

    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error("Project status proxy error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
