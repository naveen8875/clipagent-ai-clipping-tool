import { createClient } from "@/lib/supabase/server";
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

// Validation schema for signup request
const signupSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log("Signup request body:", body);

    // Validate request body
    const validatedData = signupSchema.parse(body);
    const { name, email, password } = validatedData;

    // Check environment variables
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL;
    console.log("NEXT_PUBLIC_SITE_URL:", siteUrl);

    if (!siteUrl) {
      console.error("NEXT_PUBLIC_SITE_URL is not set!");
      return NextResponse.json(
        {
          error: "Server configuration error",
          message: "Site URL not configured",
        },
        { status: 500 }
      );
    }

    // Create Supabase client
    const supabase = await createClient();

    const signupOptions = {
      emailRedirectTo: `${siteUrl}/auth/confirm`,
      data: {
        full_name: name,
      },
    };

    console.log("Signup options:", signupOptions);

    // Attempt to sign up
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: signupOptions,
    });

    console.log("Supabase signup response:", { data, error });

    if (error) {
      console.error("Signup error details:", {
        message: error.message,
        status: error.status,
        name: error.name,
        cause: error.cause,
      });
      return NextResponse.json(
        {
          error: "Signup failed",
          message: error.message,
          details: error,
        },
        { status: 400 }
      );
    }

    if (!data.user) {
      return NextResponse.json(
        { error: "User creation failed" },
        { status: 400 }
      );
    }

    // Return success response
    return NextResponse.json({
      success: true,
      message:
        "Account created successfully! Please check your email to confirm your account.",
      user: {
        id: data.user.id,
        email: data.user.email,
        created_at: data.user.created_at,
        email_confirmed_at: data.user.email_confirmed_at,
      },
    });
  } catch (error) {
    console.error("Signup API error:", {
      error: error,
      message: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
    });

    if (error instanceof z.ZodError) {
      console.error("Validation errors:", error.errors);
      return NextResponse.json(
        {
          error: "Validation failed",
          details: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
