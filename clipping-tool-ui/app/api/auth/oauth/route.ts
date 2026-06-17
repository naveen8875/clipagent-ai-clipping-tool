import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { provider } = await request.json();

    if (!provider || !['google', 'github'].includes(provider)) {
      return NextResponse.json(
        { error: "Invalid provider" },
        { status: 400 }
      );
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: provider as 'google' | 'github',
      options: {
        redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/auth/confirm`
      }
    });

    if (error) {
      console.error("OAuth error:", error);
      return NextResponse.json(
        { error: "OAuth authentication failed", message: error.message },
        { status: 400 }
      );
    }

    if (data.url) {
      return NextResponse.json({ url: data.url });
    }

    return NextResponse.json(
      { error: "No redirect URL received" },
      { status: 400 }
    );
  } catch (error) {
    console.error("OAuth API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
