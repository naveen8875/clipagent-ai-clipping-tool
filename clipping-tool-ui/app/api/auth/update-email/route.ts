import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { z } from "zod";

// Validation schema for email update
const updateEmailSchema = z.object({
  newEmail: z.string().email("Please enter a valid email address"),
});

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();

    // Get authenticated user
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Unauthorized", message: "Please log in to update your email" },
        { status: 401 }
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const validatedData = updateEmailSchema.parse(body);

    // Check if the new email is different from current email
    if (validatedData.newEmail === user.email) {
      return NextResponse.json(
        { 
          error: "Same email", 
          message: "Please enter a different email address" 
        },
        { status: 400 }
      );
    }

    console.log("🔍 Updating email for user:", user.email, "to:", validatedData.newEmail);

    // Update email - this will send confirmation emails
    const { error: updateError } = await supabase.auth.updateUser({
      email: validatedData.newEmail,
    });

    if (updateError) {
      console.error("❌ Email update error:", updateError);
      return NextResponse.json(
        { 
          error: "Email update failed", 
          message: updateError.message 
        },
        { status: 400 }
      );
    }

    console.log("✅ Email update initiated successfully for user:", user.email);

    return NextResponse.json({
      success: true,
      message: "Confirmation email sent to your new email address",
    });
  } catch (error) {
    console.error("❌ API Error:", error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Validation failed",
          message: "Invalid email format",
          details: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { 
        error: "Internal server error", 
        message: "Failed to update email" 
      },
      { status: 500 }
    );
  }
}
