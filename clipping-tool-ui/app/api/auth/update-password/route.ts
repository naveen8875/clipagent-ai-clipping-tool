import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { z } from "zod";

// Validation schema for forgot password update (no current password required)
const forgotPasswordSchema = z.object({
  newPassword: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      "Password must contain uppercase, lowercase, and number"
    ),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// Validation schema for normal password update (with current password)
const normalPasswordSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      "Password must contain uppercase, lowercase, and number"
    ),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
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
        { error: "Unauthorized", message: "Please log in to update your password" },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json();
    console.log("🔍 Received password update request:", { hasCurrentPassword: !!body.currentPassword });

    // Determine if this is a normal password update (with current password) or forgot password update
    const isNormalUpdate = body.currentPassword !== undefined;
    
    let validatedData;
    if (isNormalUpdate) {
      // Normal password update - verify current password first
      validatedData = normalPasswordSchema.parse(body);
      
      console.log("🔍 Verifying current password for user:", user.email);
      
      // Verify current password by attempting to sign in
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: user.email!,
        password: validatedData.currentPassword,
      });

      if (signInError) {
        console.error("❌ Current password verification failed:", signInError.message);
        return NextResponse.json(
          { 
            error: "Current password is incorrect", 
            message: "The current password you entered is incorrect" 
          },
          { status: 400 }
        );
      }
    } else {
      // Forgot password update - no current password verification needed
      validatedData = forgotPasswordSchema.parse(body);
    }

    console.log("🔍 Updating password for user:", user.email);

    // Update password
    const { error: updateError } = await supabase.auth.updateUser({
      password: validatedData.newPassword,
    });

    if (updateError) {
      console.error("❌ Password update error:", updateError);
      return NextResponse.json(
        { 
          error: "Password update failed", 
          message: updateError.message 
        },
        { status: 400 }
      );
    }

    console.log("✅ Password updated successfully for user:", user.email);

    return NextResponse.json({
      success: true,
      message: "Password updated successfully",
    });
  } catch (error) {
    console.error("❌ API Error:", error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Validation failed",
          message: "Invalid password format",
          details: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { 
        error: "Internal server error", 
        message: "Failed to update password" 
      },
      { status: 500 }
    );
  }
}
