import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const { code } = await request.json();

    if (!code) {
      return NextResponse.json(
        { error: "Code is required" },
        { status: 400 }
      );
    }

    const supabase = await createClient();

    // Exchange code for session
    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (error) {
      console.error("Code exchange error:", error);
      return NextResponse.json(
        { 
          error: "Invalid or expired code", 
          message: error.message 
        },
        { status: 400 }
      );
    }

    // Get user data after successful exchange
    const { data: { user }, error: userError } = await supabase.auth.getUser();

    if (userError || !user) {
      console.error("Get user after exchange error:", userError);
      return NextResponse.json(
        { 
          error: "Failed to get user data", 
          message: userError?.message || "Unknown error" 
        },
        { status: 500 }
      );
    }

    console.log("✅ Code exchanged successfully for user:", user.email);

    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        email_confirmed_at: user.email_confirmed_at,
        created_at: user.created_at,
        last_sign_in_at: user.last_sign_in_at,
      },
    });
  } catch (error) {
    console.error("❌ Code exchange API error:", error);
    return NextResponse.json(
      { 
        error: "Internal server error", 
        message: "Failed to exchange code" 
      },
      { status: 500 }
    );
  }
}
