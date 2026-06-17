import { createClient } from "@/lib/supabase/server";
import { NextRequest, NextResponse } from "next/server";
import { generateAvatar } from "@/lib/avatar-utils";

export async function GET(_request: NextRequest) {
  try {
    // Create Supabase client
    const supabase = await createClient();

    // Get the current user
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser();

    if (error) {
      console.error("Get user error:", error.message);
      return NextResponse.json(
        {
          error: "Authentication failed",
          message: error.message,
        },
        { status: 401 }
      );
    }

    if (!user) {
      return NextResponse.json(
        { error: "No authenticated user" },
        { status: 401 }
      );
    }

    // Get user profile data directly from users table
    const { data: profileData, error: profileError } = await supabase
      .from("users")
      .select("*")
      .eq("id", user.id)
      .single();

    if (profileError) {
      console.error("Profile data error:", profileError);
      return NextResponse.json(
        {
          error: "Failed to fetch profile data",
          message: profileError.message,
        },
        { status: 500 }
      );
    }

    // Get video statistics separately
    const { data: videoStats, error: videoStatsError } = await supabase
      .from("videos")
      .select("status, file_size")
      .eq("user_id", user.id);

    if (videoStatsError) {
      console.error("Video stats error:", videoStatsError);
    }

    // Calculate video statistics
    const totalVideos = videoStats?.length || 0;
    const completedVideos =
      videoStats?.filter((v) => v.status === "completed").length || 0;
    const processingVideos =
      videoStats?.filter((v) => v.status === "processing").length || 0;
    const failedVideos =
      videoStats?.filter((v) => v.status === "failed").length || 0;
    const totalStorageBytes =
      videoStats?.reduce((sum, v) => sum + (v.file_size || 0), 0) || 0;

    // Get subscription data to determine current plan (match billing API approach)
    const { data: subscriptionData, error: subscriptionError } = await supabase
      .from("user_subscriptions")
      .select(`
        plan_id,
        subscription_status,
        current_period_start,
        current_period_end,
        cancel_at_period_end,
        cancel_at,
        user_plans!user_subscriptions_plan_id_fkey (
          name,
          display_name,
          monthly_credits,
          features
        )
      `)
      .eq("user_id", user.id)
      .single();

    // Get credits and plan information
    const { data: creditsData, error: creditsError } = await supabase.rpc(
      "check_user_credits",
      { auth_user_id: user.id }
    );

    // Get plan data separately if subscription exists
    let planData = null;
    if (subscriptionData?.plan_id) {
      const { data: planInfo } = await supabase
        .from("user_plans")
        .select("name, display_name, monthly_credits, features")
        .eq("id", subscriptionData.plan_id)
        .single();
      planData = planInfo;
    }

    // If subscription query failed but we have credits data with plan info, use that
    if (!planData && creditsData?.plan_display_name && creditsData.plan_display_name !== "Free Plan") {
      planData = {
        name: creditsData.plan_name || "free",
        display_name: creditsData.plan_display_name,
        monthly_credits: creditsData.monthly_credits || 2,
        features: creditsData.plan_features || {}
      };
    }

    if (creditsError) {
      console.error("Credits data error:", creditsError);
      return NextResponse.json(
        {
          error: "Failed to fetch credits data",
          message: creditsError.message,
        },
        { status: 500 }
      );
    }

    // Determine the current plan - use subscription data if available, otherwise fall back to credits data
    const currentPlan = planData || {
      name: "free",
      display_name: "Free Plan",
      monthly_credits: 2,
      features: {}
    };

    // Debug logging
    console.log(`🔍 User ${user.id} plan detection:`, {
      hasSubscription: !!subscriptionData,
      subscriptionStatus: subscriptionData?.subscription_status,
      subscriptionError: subscriptionError?.message,
      planFromSubscription: planData?.display_name,
      planFromCredits: creditsData?.plan_display_name,
      finalPlan: currentPlan.display_name
    });

    // Calculate account age
    const accountAgeDays = Math.floor(
      (Date.now() - new Date(user.created_at!).getTime()) /
        (1000 * 60 * 60 * 24)
    );

    // Check if user signed up with OAuth
    const isOAuthUser = user.app_metadata?.provider === 'google' || user.app_metadata?.provider === 'github';
    const oauthProvider = user.app_metadata?.provider;

    // Return comprehensive profile data
    return NextResponse.json({
      success: true,
      profile: {
        // Basic Info
        id: user.id,
        name: profileData?.name || "User",
        email: user.email,
        avatar_url: generateAvatar(user.email!),
        created_at: user.created_at,
        is_email_confirmed: !!user.email_confirmed_at,
        last_sign_in_at: user.last_sign_in_at,
        account_age_days: accountAgeDays,
        
        // OAuth Info
        is_oauth_user: isOAuthUser,
        oauth_provider: oauthProvider,

        // API Key
        api_key: profileData?.api_key,

        // Subscription Renewal Info
        subscription_renewal: {
          current_period_end: subscriptionData?.current_period_end,
          days_until_renewal: subscriptionData?.current_period_end 
            ? Math.ceil((new Date(subscriptionData.current_period_end).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
            : null,
          needs_renewal: subscriptionData?.current_period_end 
            ? new Date(subscriptionData.current_period_end).getTime() <= Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days
            : false,
          is_cancelled: subscriptionData?.cancel_at_period_end || false,
          cancel_at: subscriptionData?.cancel_at,
        },

        // Plan Info - Use subscription data for accurate plan information
        plan: {
          name: currentPlan.name,
          display_name: currentPlan.display_name,
          monthly_credits: currentPlan.monthly_credits,
          features: currentPlan.features,
        },

        // Credits Info
        credits: {
          used: creditsData?.credits_used || 0,
          available: creditsData?.credits_available || 2,
          reset_date: creditsData?.reset_date,
          can_upload: creditsData?.can_upload || false,
        },

        // Usage Stats
        usage: {
          videos_processed: totalVideos,
          videos_completed: completedVideos,
          videos_processing: processingVideos,
          videos_failed: failedVideos,
          storage_used_bytes: totalStorageBytes,
          storage_used_mb:
            Math.round((totalStorageBytes / (1024 * 1024)) * 100) / 100,
          usage_limit: profileData?.usage_limit || 10,
          current_usage: profileData?.current_usage || 0,
        },

        // Legacy subscription info (from original schema)
        subscription_plan: profileData?.subscription_plan || "free",
        last_activity: profileData?.last_activity,
      },
    });
  } catch (error) {
    console.error("Get user API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
