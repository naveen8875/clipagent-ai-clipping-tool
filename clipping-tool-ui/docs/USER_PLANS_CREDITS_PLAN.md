# User Plans & Credits Management System Plan

## 🎯 Overview

Implement a comprehensive user plan and credit management system with Supabase database integration, automatic plan assignment, and usage tracking for video uploads.

## 📋 Core Requirements

### 1. **Plan Structure**

- **Free Plan**: 2 upload credits per month
- **Pro Plan**: Unlimited uploads
- **Manual Plan Switching**: Admin-controlled plan changes
- **Default Assignment**: New users automatically get Free plan

### 2. **Database Integration**

- **Supabase SQL Functions**: Automatic user and plan record creation
- **Email Confirmation**: Required before dashboard access
- **Credit Tracking**: Real-time usage monitoring

### 3. **Access Control**

- **Dashboard Protection**: Blocked until email confirmed
- **Credit Validation**: Check limits before uploads
- **Plan Enforcement**: Automatic usage restrictions

## 🗄️ Database Schema Design

### **Public Users Table** (Separate from auth.users)

```sql
CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  plan_id UUID REFERENCES user_plans(id),
  credits_used INTEGER DEFAULT 0,
  credits_reset_date TIMESTAMP,
  is_email_confirmed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_users_auth_user_id ON public.users(auth_user_id);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_plan_id ON public.users(plan_id);
```

### **User Plans Table**

```sql
CREATE TABLE user_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) NOT NULL UNIQUE, -- 'free', 'pro'
  display_name VARCHAR(100) NOT NULL, -- 'Free Plan', 'Pro Plan'
  monthly_credits INTEGER NOT NULL, -- 2 for free, -1 for unlimited
  price_monthly DECIMAL(10,2) DEFAULT 0.00,
  features JSONB DEFAULT '{}', -- Additional plan features
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default plans
INSERT INTO user_plans (name, display_name, monthly_credits, price_monthly, features) VALUES
('free', 'Free Plan', 2, 0.00, '{"max_video_size": "100MB", "support": "community"}'),
('pro', 'Pro Plan', -1, 29.00, '{"max_video_size": "1GB", "support": "priority", "api_access": true}');
```

### **User Credits Table**

```sql
CREATE TABLE user_credits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  plan_id UUID REFERENCES user_plans(id),
  credits_used INTEGER DEFAULT 0,
  credits_available INTEGER NOT NULL,
  reset_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(user_id, reset_date)
);

-- Index for performance
CREATE INDEX idx_user_credits_user_id ON user_credits(user_id);
CREATE INDEX idx_user_credits_reset_date ON user_credits(reset_date);
```

### **Credit Transactions Table**

```sql
CREATE TABLE credit_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  transaction_type VARCHAR(20) NOT NULL, -- 'upload', 'reset', 'admin_add', 'admin_remove'
  credits_change INTEGER NOT NULL, -- Positive for additions, negative for usage
  description TEXT,
  metadata JSONB DEFAULT '{}', -- Additional transaction data
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);
```

### **Videos Table** (For Trigger Integration)

```sql
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- Links to auth.users for trigger
  title VARCHAR(255) NOT NULL,
  description TEXT,
  file_url TEXT,
  thumbnail_url TEXT,
  status VARCHAR(20) DEFAULT 'processing', -- 'processing', 'completed', 'failed'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at);
```

## 🔧 Supabase SQL Functions & Triggers

### **1. Create User with Default Plan Function**

```sql
CREATE OR REPLACE FUNCTION create_user_with_plan(
  auth_user_id UUID,
  user_email TEXT
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  new_user_id UUID;
  free_plan_id UUID;
  current_date TIMESTAMP;
BEGIN
  -- Get free plan ID
  SELECT id INTO free_plan_id FROM user_plans WHERE name = 'free' LIMIT 1;

  -- Set current date for credit reset
  current_date := NOW();

  -- Create user record in public.users
  INSERT INTO public.users (auth_user_id, email, plan_id, credits_used, credits_reset_date, is_email_confirmed)
  VALUES (auth_user_id, user_email, free_plan_id, 0, current_date + INTERVAL '1 month', false)
  RETURNING id INTO new_user_id;

  -- Create initial credit record
  INSERT INTO user_credits (user_id, plan_id, credits_used, credits_available, reset_date)
  VALUES (new_user_id, free_plan_id, 0, 2, current_date + INTERVAL '1 month');

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (new_user_id, 'reset', 2, 'Initial free plan credits');

  RETURN json_build_object(
    'success', true,
    'user_id', new_user_id,
    'auth_user_id', auth_user_id,
    'plan_id', free_plan_id,
    'credits_available', 2
  );
END;
$$;
```

### **2. Auto-Create User Trigger Function**

```sql
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  free_plan_id UUID;
  new_user_id UUID;
  current_date TIMESTAMP;
BEGIN
  -- Get free plan ID
  SELECT id INTO free_plan_id FROM user_plans WHERE name = 'free' LIMIT 1;

  -- Set current date for credit reset
  current_date := NOW();

  -- Create user record in public.users
  INSERT INTO public.users (auth_user_id, email, plan_id, credits_used, credits_reset_date, is_email_confirmed)
  VALUES (NEW.id, NEW.email, free_plan_id, 0, current_date + INTERVAL '1 month', false)
  RETURNING id INTO new_user_id;

  -- Create initial credit record
  INSERT INTO user_credits (user_id, plan_id, credits_used, credits_available, reset_date)
  VALUES (new_user_id, free_plan_id, 0, 2, current_date + INTERVAL '1 month');

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (new_user_id, 'reset', 2, 'Initial free plan credits');

  RETURN NEW;
END;
$$;
```

### **3. Auto-Deduct Credits Trigger Function**

```sql
CREATE OR REPLACE FUNCTION handle_video_upload()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  user_record RECORD;
  current_credits RECORD;
  new_credits_used INTEGER;
  new_credits_available INTEGER;
BEGIN
  -- Get user's plan and current credits
  SELECT
    u.id as public_user_id,
    up.monthly_credits,
    uc.credits_used,
    uc.credits_available,
    uc.reset_date
  INTO user_record
  FROM public.users u
  JOIN user_plans up ON u.plan_id = up.id
  LEFT JOIN user_credits uc ON u.id = uc.user_id
    AND uc.reset_date = (
      SELECT MAX(reset_date)
      FROM user_credits
      WHERE user_id = u.id
    )
  WHERE u.auth_user_id = NEW.user_id; -- Assuming video table has user_id field

  -- Check if credits need reset first
  IF user_record.reset_date < NOW() THEN
    PERFORM reset_user_credits(user_record.public_user_id);
    -- Refetch updated credits
    SELECT credits_used, credits_available
    INTO current_credits
    FROM user_credits
    WHERE user_id = user_record.public_user_id
      AND reset_date = (
        SELECT MAX(reset_date)
        FROM user_credits
        WHERE user_id = user_record.public_user_id
      );
  ELSE
    current_credits.credits_used := user_record.credits_used;
    current_credits.credits_available := user_record.credits_available;
  END IF;

  -- Check if user has unlimited credits (Pro plan)
  IF user_record.monthly_credits = -1 THEN
    -- Pro plan - no credit deduction needed
    INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
    VALUES (user_record.public_user_id, 'upload', 0, 'Pro plan upload - no credits deducted');
    RETURN NEW;
  END IF;

  -- Check if user has enough credits
  IF current_credits.credits_available < 1 THEN
    -- Insufficient credits - you might want to handle this differently
    -- For now, we'll log it and continue (you could also RAISE an exception)
    INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
    VALUES (user_record.public_user_id, 'upload', 0, 'Upload attempted with insufficient credits');
    RETURN NEW;
  END IF;

  -- Calculate new values
  new_credits_used := current_credits.credits_used + 1;
  new_credits_available := current_credits.credits_available - 1;

  -- Update credits
  UPDATE user_credits
  SET
    credits_used = new_credits_used,
    credits_available = new_credits_available,
    updated_at = NOW()
  WHERE user_id = user_record.public_user_id
    AND reset_date = (
      SELECT MAX(reset_date)
      FROM user_credits
      WHERE user_id = user_record.public_user_id
    );

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (user_record.public_user_id, 'upload', -1, 'Video upload');

  RETURN NEW;
END;
$$;
```

### **4. Database Triggers**

```sql
-- Trigger to auto-create user when auth.users record is created
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Trigger to auto-deduct credits when video is uploaded
-- (Assuming you have a videos table with user_id field)
CREATE TRIGGER on_video_uploaded
  AFTER INSERT ON videos
  FOR EACH ROW
  EXECUTE FUNCTION handle_video_upload();
```

### **5. Check User Credits**

```sql
CREATE OR REPLACE FUNCTION check_user_credits(auth_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  user_plan RECORD;
  current_credits INTEGER;
  reset_date TIMESTAMP;
BEGIN
  -- Get user's current plan and credits
  SELECT
    up.name as plan_name,
    up.display_name,
    up.monthly_credits,
    uc.credits_used,
    uc.credits_available,
    uc.reset_date,
    u.id as public_user_id
  INTO user_plan
  FROM public.users u
  JOIN user_plans up ON u.plan_id = up.id
  LEFT JOIN user_credits uc ON u.id = uc.user_id
    AND uc.reset_date = (
      SELECT MAX(reset_date)
      FROM user_credits
      WHERE user_id = u.id
    )
  WHERE u.auth_user_id = auth_user_id;

  -- Check if credits need reset
  IF user_plan.reset_date < NOW() THEN
    PERFORM reset_user_credits(user_plan.public_user_id);
    -- Refetch updated credits
    SELECT
      up.name as plan_name,
      up.display_name,
      up.monthly_credits,
      uc.credits_used,
      uc.credits_available,
      uc.reset_date,
      u.id as public_user_id
    INTO user_plan
    FROM public.users u
    JOIN user_plans up ON u.plan_id = up.id
    LEFT JOIN user_credits uc ON u.id = uc.user_id
      AND uc.reset_date = (
        SELECT MAX(reset_date)
        FROM user_credits
        WHERE user_id = u.id
      )
    WHERE u.auth_user_id = auth_user_id;
  END IF;

  RETURN json_build_object(
    'plan_name', user_plan.plan_name,
    'plan_display_name', user_plan.display_name,
    'monthly_credits', user_plan.monthly_credits,
    'credits_used', COALESCE(user_plan.credits_used, 0),
    'credits_available', COALESCE(user_plan.credits_available, 0),
    'reset_date', user_plan.reset_date,
    'is_unlimited', user_plan.monthly_credits = -1,
    'can_upload', CASE
      WHEN user_plan.monthly_credits = -1 THEN true
      ELSE COALESCE(user_plan.credits_available, 0) > 0
    END
  );
END;
$$;
```

### **3. Reset User Credits**

```sql
CREATE OR REPLACE FUNCTION reset_user_credits(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  user_plan RECORD;
  new_reset_date TIMESTAMP;
  credits_to_give INTEGER;
BEGIN
  -- Get user's plan
  SELECT up.monthly_credits, up.id as plan_id
  INTO user_plan
  FROM auth.users u
  JOIN user_plans up ON u.plan_id = up.id
  WHERE u.id = user_id;

  -- Calculate new reset date (next month)
  new_reset_date := NOW() + INTERVAL '1 month';

  -- Determine credits to give
  credits_to_give := user_plan.monthly_credits;

  -- Create new credit record
  INSERT INTO user_credits (user_id, plan_id, credits_used, credits_available, reset_date)
  VALUES (user_id, user_plan.plan_id, 0, credits_to_give, new_reset_date);

  -- Update user's reset date
  UPDATE auth.users
  SET credits_reset_date = new_reset_date
  WHERE id = user_id;

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (user_id, 'reset', credits_to_give, 'Monthly credit reset');

  RETURN json_build_object(
    'success', true,
    'credits_added', credits_to_give,
    'new_reset_date', new_reset_date
  );
END;
$$;
```

### **4. Use Credits**

```sql
CREATE OR REPLACE FUNCTION use_credits(user_id UUID, credits_to_use INTEGER, description TEXT DEFAULT 'Video upload')
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_credits RECORD;
  new_credits_used INTEGER;
  new_credits_available INTEGER;
BEGIN
  -- Check current credits
  SELECT credits_used, credits_available
  INTO current_credits
  FROM user_credits
  WHERE user_id = user_id
    AND reset_date = (
      SELECT MAX(reset_date)
      FROM user_credits
      WHERE user_id = user_id
    );

  -- Check if user has enough credits
  IF current_credits.credits_available < credits_to_use THEN
    RETURN json_build_object(
      'success', false,
      'error', 'Insufficient credits',
      'credits_available', current_credits.credits_available,
      'credits_requested', credits_to_use
    );
  END IF;

  -- Calculate new values
  new_credits_used := current_credits.credits_used + credits_to_use;
  new_credits_available := current_credits.credits_available - credits_to_use;

  -- Update credits
  UPDATE user_credits
  SET
    credits_used = new_credits_used,
    credits_available = new_credits_available,
    updated_at = NOW()
  WHERE user_id = user_id
    AND reset_date = (
      SELECT MAX(reset_date)
      FROM user_credits
      WHERE user_id = user_id
    );

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (user_id, 'upload', -credits_to_use, description);

  RETURN json_build_object(
    'success', true,
    'credits_used', credits_to_use,
    'credits_remaining', new_credits_available,
    'total_used', new_credits_used
  );
END;
$$;
```

### **5. Change User Plan**

```sql
CREATE OR REPLACE FUNCTION change_user_plan(user_id UUID, new_plan_name TEXT)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  new_plan_id UUID;
  new_plan_credits INTEGER;
  current_date TIMESTAMP;
BEGIN
  -- Get new plan details
  SELECT id, monthly_credits
  INTO new_plan_id, new_plan_credits
  FROM user_plans
  WHERE name = new_plan_name AND is_active = true;

  IF new_plan_id IS NULL THEN
    RETURN json_build_object(
      'success', false,
      'error', 'Plan not found or inactive'
    );
  END IF;

  current_date := NOW();

  -- Update user's plan
  UPDATE auth.users
  SET
    plan_id = new_plan_id,
    credits_reset_date = current_date + INTERVAL '1 month'
  WHERE id = user_id;

  -- Create new credit record with immediate reset
  INSERT INTO user_credits (user_id, plan_id, credits_used, credits_available, reset_date)
  VALUES (user_id, new_plan_id, 0, new_plan_credits, current_date + INTERVAL '1 month');

  -- Log transaction
  INSERT INTO credit_transactions (user_id, transaction_type, credits_change, description)
  VALUES (user_id, 'admin_add', new_plan_credits, 'Plan changed to ' || new_plan_name);

  RETURN json_build_object(
    'success', true,
    'new_plan', new_plan_name,
    'credits_available', new_plan_credits,
    'reset_date', current_date + INTERVAL '1 month'
  );
END;
$$;
```

## 🔐 Row Level Security (RLS) Policies

### **Public Users Table RLS**

```sql
-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = auth_user_id);

-- Users can update their own data (except plan_id)
CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = auth_user_id);

-- Only service role can insert new users
CREATE POLICY "Service role can create users" ON public.users
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Only service role can change plans
CREATE POLICY "Service role can change plans" ON public.users
  FOR UPDATE USING (auth.role() = 'service_role');
```

### **User Credits Table RLS**

```sql
-- Enable RLS
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;

-- Users can only see their own credits (via public.users relationship)
CREATE POLICY "Users can view own credits" ON user_credits
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.users u
      WHERE u.id = user_credits.user_id
      AND u.auth_user_id = auth.uid()
    )
  );

-- Only service role can insert/update credits
CREATE POLICY "Service role can manage credits" ON user_credits
  FOR ALL USING (auth.role() = 'service_role');
```

### **Credit Transactions Table RLS**

```sql
-- Enable RLS
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own transactions (via public.users relationship)
CREATE POLICY "Users can view own transactions" ON credit_transactions
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.users u
      WHERE u.id = credit_transactions.user_id
      AND u.auth_user_id = auth.uid()
    )
  );

-- Only service role can insert transactions
CREATE POLICY "Service role can insert transactions" ON credit_transactions
  FOR INSERT WITH CHECK (auth.role() = 'service_role');
```

## 🚀 API Routes Implementation (Minimal with Triggers)

### **1. User Credits API** (`/api/user/credits`)

```typescript
// GET /api/user/credits - Get current user's credit status
// GET /api/user/credits/history - Get credit transaction history
// Note: No POST endpoint needed - credits are auto-managed by triggers
```

### **2. Video Upload API** (`/api/videos`) - **AUTH LAYER**

```typescript
// POST /api/videos - Auth layer over existing backend (triggers credit deduction)
// GET /api/videos - Auth layer over existing backend
// PUT /api/videos/[id] - Auth layer over existing backend
// DELETE /api/videos/[id] - Auth layer over existing backend
// Note: These are just auth layers - main backend handles all video operations
// Credit deduction happens automatically via database trigger
```

### **3. Plan Management API** (`/api/admin/plans`) - **FUTURE**

```typescript
// GET /api/admin/plans - Get all available plans
// POST /api/admin/plans/change - Change user's plan (admin only)
// GET /api/admin/plans/users - Get all users with their plans
// Note: Admin APIs will be implemented separately later
```

**Note**: Dashboard access is handled by middleware checking `is_email_confirmed` in `public.users` table. No separate API needed.

## 📤 Video API Implementation - **AUTH LAYER**

### **POST /api/videos - Upload Video (Auth Layer)**

```typescript
// app/api/videos/route.ts - AUTH LAYER IMPLEMENTATION
import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();

    // Get authenticated user
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Parse request body
    const videoData = await request.json();

    // Create video record in database to trigger credit deduction
    const { data: video, error: insertError } = await supabase
      .from("videos")
      .insert({
        user_id: user.id, // This triggers the credit deduction
        title: videoData.title,
        description: videoData.description,
        file_url: videoData.file_url,
        thumbnail_url: videoData.thumbnail_url,
        status: "processing",
      })
      .select()
      .single();

    if (insertError) {
      return NextResponse.json({ error: insertError.message }, { status: 400 });
    }

    // The trigger automatically handles credit deduction
    // Now forward to main backend for actual processing
    const backendResponse = await fetch(
      `${process.env.MAIN_BACKEND_URL}/api/videos`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-ID": user.id, // Pass user ID to backend
        },
        body: JSON.stringify(videoData),
      }
    );

    const backendData = await backendResponse.json();

    return NextResponse.json({
      success: true,
      video,
      backend_response: backendData,
      message: "Video uploaded successfully",
    });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

### **GET /api/videos - Get User's Videos (Auth Layer)**

```typescript
export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();

    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Forward to main backend for video data
    const backendResponse = await fetch(
      `${process.env.MAIN_BACKEND_URL}/api/videos`,
      {
        method: "GET",
        headers: {
          "X-User-ID": user.id, // Pass user ID to backend
        },
      }
    );

    const backendData = await backendResponse.json();

    return NextResponse.json(backendData);
  } catch (error) {
    console.error("Get videos error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

### **🎯 Focus: Credits System Implementation**

**Priority Order:**

1. **✅ Database Setup**: Create tables, triggers, and functions
2. **✅ Credits API**: Implement credit checking and history
3. **⏳ Video APIs**: Simple auth layer over existing backend
4. **⏳ Admin APIs**: Will be implemented separately later

**Key Point**: Video APIs are just auth layers - main backend handles all video operations automatically.

### **Key Benefits of This Approach:**

1. **🚀 Automatic Credit Management**: Trigger handles credit deduction
2. **🔒 Secure**: User can only upload to their own account
3. **📊 Audit Trail**: All uploads are logged in credit_transactions
4. **⚡ Simple**: No complex credit logic in API
5. **🛡️ Bulletproof**: Credit logic can't be bypassed
6. **🔄 Backend Ready**: Easy integration with existing video processing backend

## ⚡ Benefits of Database Triggers

### **🚀 Automatic Operations**

- **User Creation**: No manual API calls needed - users are automatically created with Free plan
- **Credit Deduction**: Credits are automatically deducted when videos are uploaded
- **Transaction Logging**: All credit changes are automatically logged
- **Monthly Resets**: Credits are automatically reset when needed

### **🔒 Data Consistency**

- **Atomic Operations**: All credit operations happen in single database transaction
- **No Race Conditions**: Database handles concurrency automatically
- **Guaranteed Execution**: Triggers fire regardless of application state
- **Rollback Safety**: Failed operations automatically rollback

### **📈 Performance Benefits**

- **Reduced API Calls**: No need for separate credit management endpoints
- **Database-Level Logic**: Faster than application-level credit checks
- **Bulk Operations**: Triggers handle multiple operations efficiently
- **Optimized Queries**: Database optimizes trigger execution

### **🛡️ Security Benefits**

- **Server-Side Logic**: Credit logic can't be bypassed by client
- **Audit Trail**: All operations are automatically logged
- **Data Integrity**: Triggers enforce business rules at database level
- **No Manual Intervention**: Eliminates human error in credit management

## 🎨 Frontend Integration (Simplified)

### **1. Dashboard Access Control (Middleware)**

```typescript
// Middleware automatically checks is_email_confirmed in public.users
// Redirects unconfirmed users to auth page
// No additional API calls needed
```

### **2. Credit Display Components**

```typescript
// CreditCounter - Shows current credits/plan via check_user_credits()
// PlanUpgradePrompt - Suggests pro plan when credits low
// UsageHistory - Shows credit transaction history
```

### **3. Upload Flow Integration (Automatic)**

```typescript
// Pre-upload credit check via check_user_credits()
// Upload creates video record → triggers automatic credit deduction
// No manual credit management needed
```

## 📱 User Experience Flows

### **Flow 1: New User Registration**

1. User signs up → Account created
2. Supabase trigger calls `create_user_with_plan()`
3. User gets Free plan with 2 credits
4. Email confirmation required
5. After confirmation → Dashboard access granted

### **Flow 2: Free User Upload**

1. User tries to upload video
2. System checks credits via `check_user_credits()`
3. If credits available → Upload proceeds
4. `use_credits()` called on successful upload
5. Credit counter updates in UI

### **Flow 3: Credit Limit Reached**

1. User tries to upload with 0 credits
2. System shows upgrade prompt
3. User can wait for monthly reset or upgrade
4. Admin can manually change plan

### **Flow 4: Monthly Credit Reset**

1. System checks reset date on credit access
2. If past reset date → `reset_user_credits()` called
3. User gets fresh credits for the month
4. Transaction logged for audit

## 🔒 Security Considerations

### **1. Database Security**

- **RLS Policies**: Users can only access their own data
- **Service Role**: Only service role can modify credits
- **SQL Injection**: All functions use parameterized queries
- **Audit Trail**: All credit changes are logged

### **2. API Security**

- **Authentication**: All routes require valid session
- **Authorization**: Admin routes require admin role
- **Rate Limiting**: Prevent credit manipulation abuse
- **Input Validation**: Validate all user inputs

### **3. Business Logic Security**

- **Credit Validation**: Server-side credit checks only
- **Plan Enforcement**: Automatic usage restrictions
- **Fraud Prevention**: Transaction logging and monitoring

## 📊 Monitoring & Analytics

### **1. Credit Usage Metrics**

- Monthly credit consumption per plan
- User engagement vs credit usage
- Upgrade conversion rates
- Credit reset frequency

### **2. Plan Performance**

- Free vs Pro user behavior
- Credit limit impact on usage
- Plan change patterns
- Revenue per user

### **3. System Health**

- Database function performance
- Credit check response times
- Error rates in credit operations
- Transaction processing success

## 🧪 Testing Strategy

### **1. Database Function Tests**

- Unit tests for each SQL function
- Edge case testing (unlimited plans, expired credits)
- Concurrency testing (multiple users)
- Data integrity validation

### **2. API Integration Tests**

- Credit check endpoints
- Upload flow with credit deduction
- Plan change functionality
- Error handling scenarios

### **3. End-to-End Tests**

- Complete user registration flow
- Credit usage and reset cycles
- Plan upgrade/downgrade flows
- Dashboard access control

## 📅 Implementation Timeline

### **Phase 1: Database Setup (Week 1)**

- Create database tables and relationships
- Implement SQL functions and triggers
- Set up RLS policies
- Test database operations
- **Focus**: Credits system foundation

### **Phase 2: Credits API Development (Week 2)**

- Create credit management APIs
- Add dashboard access control
- Test API integrations
- **Focus**: Credits system functionality

### **Phase 3: Frontend Integration (Week 3)**

- Add credit display components
- Implement dashboard access control
- Add plan upgrade prompts
- Create placeholder video upload UI
- **Focus**: Credits system UI

### **Phase 4: Video Integration (Week 4)**

- Integrate with existing video processing backend
- Replace placeholder video APIs
- Test complete upload flow
- Performance optimization
- **Focus**: Backend integration

## 🎯 Success Metrics

### **User Experience Metrics**

- Dashboard access success rate: >99%
- Credit check response time: <200ms
- Upload success rate: >95%
- Plan upgrade conversion: >10%

### **System Performance Metrics**

- Database function execution time: <100ms
- API response time: <300ms
- Credit accuracy: 100%
- System uptime: >99.9%

### **Business Metrics**

- Free to Pro conversion rate
- Monthly credit utilization
- User retention by plan
- Revenue per user

---

## 🔄 Complete System Flow Mapping

### **📊 Database Architecture Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   auth.users    │    │  public.users   │    │  user_plans    │
│                 │    │                 │    │                 │
│ • id (UUID)     │◄───┤ • auth_user_id  │    │ • id (UUID)     │
│ • email         │    │ • email         │    │ • name          │
│ • password_hash │    │ • plan_id       │◄───┤ • monthly_credits│
│ • created_at    │    │ • is_confirmed  │    │ • price         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  user_credits   │
                       │                 │
                       │ • user_id       │
                       │ • credits_used  │
                       │ • credits_avail │
                       │ • reset_date    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │credit_transactions│
                       │                 │
                       │ • user_id       │
                       │ • transaction_type│
                       │ • credits_change │
                       │ • description   │
                       └─────────────────┘
```

### **🔄 User Registration Flow (Automatic)**

```
1. User Signs Up
   ↓
2. Supabase Auth creates auth.users record
   ↓
3. 🚀 AUTOMATIC TRIGGER: on_auth_user_created fires
   ↓
4. Trigger calls handle_new_user() function
   ↓
5. Function automatically creates public.users record with:
   - auth_user_id → links to auth.users
   - email → copied from auth.users
   - plan_id → defaults to 'free' plan
   - is_email_confirmed → false
   ↓
6. Function automatically creates user_credits record with:
   - 2 credits available
   - Reset date = 1 month from now
   ↓
7. Function automatically logs initial transaction
   ↓
8. User receives confirmation email
   ↓
9. User clicks email link → email_confirmed = true
   ↓
10. User can now access dashboard
```

### **🎯 Dashboard Access Control Flow (Middleware)**

```
1. User tries to access /dashboard
   ↓
2. Middleware checks authentication
   ↓
3. If not authenticated → redirect to /auth
   ↓
4. If authenticated → middleware queries public.users WHERE auth_user_id = auth.uid()
   ↓
5. Middleware checks is_email_confirmed field
   ↓
6. If false → redirect to /auth with message
   ↓
7. If true → allow dashboard access
   ↓
8. Frontend loads user credits via check_user_credits(auth_user_id)
   ↓
9. Display credit counter and plan info
```

### **📤 Upload Flow with Automatic Credit Management**

```
1. User clicks "Upload Video"
   ↓
2. Frontend calls check_user_credits(auth_user_id) for validation
   ↓
3. Function returns:
   - plan_name: 'free' or 'pro'
   - credits_available: 2 or -1 (unlimited)
   - can_upload: true/false
   ↓
4. If can_upload = false:
   - Show upgrade prompt
   - Block upload
   ↓
5. If can_upload = true:
   - Allow upload to proceed
   ↓
6. Frontend calls POST /api/videos with video data
   ↓
7. API creates video record in videos table
   ↓
8. 🚀 AUTOMATIC TRIGGER: on_video_uploaded fires
   ↓
9. Trigger calls handle_video_upload() function
   ↓
10. Function automatically:
    - Checks user's plan and credits
    - Handles monthly reset if needed
    - Deducts 1 credit (if Free plan)
    - Logs transaction
    - Updates credit counters
    ↓
11. API returns success response to frontend
   ↓
12. Frontend refreshes credit display
   ↓
13. If credits = 0 → show upgrade prompt
```

### **🔄 Monthly Credit Reset Flow**

```
1. User accesses dashboard
   ↓
2. check_user_credits() is called
   ↓
3. Function checks reset_date < NOW()
   ↓
4. If true → calls reset_user_credits(user_id)
   ↓
5. Reset function:
   - Gets user's plan (free = 2, pro = unlimited)
   - Creates new user_credits record
   - Sets reset_date = NOW() + 1 month
   - Logs reset transaction
   ↓
6. Function returns updated credits
   ↓
7. Frontend displays fresh credits
```

### **👑 Plan Change Flow (Admin)**

```
1. Admin wants to change user's plan
   ↓
2. Admin calls change_user_plan(user_id, 'pro')
   ↓
3. Function:
   - Validates new plan exists
   - Updates public.users.plan_id
   - Creates new user_credits record
   - Sets credits based on new plan
   - Logs plan change transaction
   ↓
4. User's next dashboard visit shows new plan
   ↓
5. Credit limits updated automatically
```

### **🔐 Security Flow**

```
1. User makes API request
   ↓
2. Middleware validates JWT token
   ↓
3. Extract auth_user_id from token
   ↓
4. Query public.users WHERE auth_user_id = ?
   ↓
5. RLS policies check:
   - User can only see own data
   - Service role can modify credits
   - Users cannot change their own plan
   ↓
6. If authorized → proceed with operation
   ↓
7. If not authorized → return 403
```

### **📊 Credit Check Flow (Frontend)**

```
Frontend calls check_user_credits(auth_user_id)
   ↓
1. Function extracts auth_user_id from JWT
   ↓
2. Function:
   - Joins public.users + user_plans + user_credits
   - Checks if reset needed
   - Returns current status
   ↓
3. Returns:
   {
     "plan_name": "free",
     "credits_used": 1,
     "credits_available": 1,
     "can_upload": true,
     "reset_date": "2024-02-01T00:00:00Z"
   }
```

### **🚨 Error Handling Flow**

```
1. User tries to upload with 0 credits
   ↓
2. Frontend calls check_user_credits() for validation
   ↓
3. Function returns can_upload: false
   ↓
4. Frontend blocks upload and shows upgrade prompt
   ↓
5. User can wait for monthly reset or upgrade plan
```

### **🔄 Complete Upload Flow with Error Handling**

```
1. User clicks "Upload Video"
   ↓
2. Frontend calls check_user_credits(auth_user_id)
   ↓
3. If can_upload = false:
   - Show "Upgrade to Pro" or "Wait for reset" message
   - Block upload completely
   ↓
4. If can_upload = true:
   - Show upload form
   - User fills in title, description, file
   ↓
5. Frontend calls POST /api/videos
   ↓
6. API validates user authentication
   ↓
7. API creates video record in videos table
   ↓
8. 🚀 TRIGGER: on_video_uploaded fires automatically
   ↓
9. Trigger calls handle_video_upload()
   ↓
10. Function checks credits and deducts if available
   ↓
11. If insufficient credits (edge case):
    - Logs transaction with 0 credits deducted
    - Video still created but marked as "failed"
   ↓
12. API returns success/failure response
   ↓
13. Frontend updates UI accordingly
```

### **🔄 Complete User Journey**

```
Registration → Email Confirmation → Dashboard Access →
Credit Check → Upload (if credits available) →
Credit Deduction → Monthly Reset → Repeat
```

This comprehensive flow mapping ensures:

- **Separation of Concerns**: auth.users handles authentication, public.users handles business logic
- **Security**: RLS policies prevent unauthorized access
- **Scalability**: Proper indexing and efficient queries
- **Auditability**: All credit changes are logged
- **User Experience**: Clear feedback and upgrade paths

---

This comprehensive plan provides a robust foundation for implementing user plans and credit management while maintaining security, performance, and user experience standards.
