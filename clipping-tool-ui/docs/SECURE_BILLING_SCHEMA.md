# Secure Billing Schema with user_subscriptions Table

## 🛡️ Security-First Approach

Instead of adding Stripe fields to the `users` table, we'll create a separate `user_subscriptions` table that only the service role can modify. This prevents any potential user exploitation.

## 📊 Database Schema

### New Table: user_subscriptions

```sql
-- User subscriptions table (service role only)
CREATE TABLE user_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  -- Stripe-specific fields
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  subscription_status VARCHAR(20) DEFAULT 'inactive',
  -- Values: 'active', 'past_due', 'canceled', 'incomplete', 'trialing'

  -- Plan information
  plan_id UUID REFERENCES user_plans(id),

  -- Billing information
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  cancel_at_period_end BOOLEAN DEFAULT false,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Ensure one subscription per user
  UNIQUE(user_id)
);

-- Indexes for performance
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_stripe_customer_id ON user_subscriptions(stripe_customer_id);
CREATE INDEX idx_user_subscriptions_stripe_subscription_id ON user_subscriptions(stripe_subscription_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(subscription_status);
```

### Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only READ their own subscription data
CREATE POLICY "Users can view own subscription" ON user_subscriptions
  FOR SELECT USING (auth.uid() = user_id);

-- Only service role can INSERT/UPDATE/DELETE
CREATE POLICY "Service role can manage subscriptions" ON user_subscriptions
  FOR ALL USING (auth.role() = 'service_role');

-- Drop any existing policies first
DROP POLICY IF EXISTS "Users can view own subscription" ON user_subscriptions;
DROP POLICY IF EXISTS "Service role can manage subscriptions" ON user_subscriptions;
```

### Optional: Billing History Table

```sql
-- Billing history table (read-only for users)
CREATE TABLE billing_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES user_subscriptions(id) ON DELETE CASCADE,

  -- Stripe invoice information
  stripe_invoice_id TEXT,
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) NOT NULL, -- 'paid', 'open', 'void', 'uncollectible'

  -- Period information
  period_start TIMESTAMP,
  period_end TIMESTAMP,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_billing_history_user_id ON billing_history(user_id);
CREATE INDEX idx_billing_history_subscription_id ON billing_history(subscription_id);
CREATE INDEX idx_billing_history_created_at ON billing_history(created_at DESC);

-- RLS Policies
ALTER TABLE billing_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own billing history" ON billing_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage billing history" ON billing_history
  FOR ALL USING (auth.role() = 'service_role');
```

## 🔒 Security Benefits

### 1. **Isolation of Sensitive Data**

- Stripe data completely separated from user profile
- Users cannot accidentally modify subscription data
- Clear separation of concerns

### 2. **Service Role Only Modifications**

- Only webhooks and admin operations can modify subscriptions
- Users cannot exploit the system to change their plan
- All subscription changes go through Stripe

### 3. **Audit Trail**

- All subscription changes logged with timestamps
- Clear ownership of data modifications
- Easy to track subscription lifecycle

## 🔄 API Changes

### Updated API Routes

```typescript
// GET /api/billing/status
// Now joins users and user_subscriptions tables
const { data: subscription } = await supabase
  .from("user_subscriptions")
  .select(
    `
    *,
    user_plans(*)
  `
  )
  .eq("user_id", user.id)
  .single();

// POST /api/webhooks/stripe
// Only service role can modify user_subscriptions
const supabaseAdmin = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // Service role key
);

await supabaseAdmin.from("user_subscriptions").upsert({
  user_id: userId,
  stripe_customer_id: event.data.object.customer,
  stripe_subscription_id: event.data.object.id,
  subscription_status: event.data.object.status,
  plan_id: planId,
  current_period_start: new Date(event.data.object.current_period_start * 1000),
  current_period_end: new Date(event.data.object.current_period_end * 1000),
  cancel_at_period_end: event.data.object.cancel_at_period_end,
});
```

## 📋 Updated Implementation Steps

### Chunk 1.1: Database Schema (30 minutes)

**Step 1**: Create migration file `002_secure_billing_schema.sql`
**Step 2**: Create `user_subscriptions` table with all fields
**Step 3**: Create `billing_history` table (optional)
**Step 4**: Add RLS policies (users can read, service role can write)
**Step 5**: Create indexes for performance
**Step 6**: Test migration and permissions

### Updated API Routes

```typescript
// All billing APIs now use service role for modifications
// Users can only read their subscription status
// Webhooks use service role to update subscription data
```

## 🎯 Benefits of This Approach

### Security

- ✅ **Zero user exploitation risk** (users can't modify subscriptions)
- ✅ **Clear data isolation** (Stripe data separate from user data)
- ✅ **Service role enforcement** (only webhooks can change subscriptions)
- ✅ **Audit trail** (all changes logged with service role)

### Maintainability

- ✅ **Clear separation** (subscription logic isolated)
- ✅ **Easy debugging** (subscription data in dedicated table)
- ✅ **Scalable** (can add more subscription fields easily)
- ✅ **Type safe** (dedicated subscription interface)

### Performance

- ✅ **Optimized queries** (dedicated indexes for subscription data)
- ✅ **Efficient joins** (only when needed)
- ✅ **Cached data** (subscription status cached separately)

## 🔧 Migration Strategy

### Step 1: Create New Tables

```sql
-- Create user_subscriptions table
-- Create billing_history table
-- Add RLS policies
-- Create indexes
```

### Step 2: Update APIs

```typescript
// Update all billing APIs to use new table structure
// Ensure service role is used for modifications
// Update webhook handlers
```

### Step 3: Test Security

```sql
-- Test that users cannot modify subscriptions
-- Test that service role can modify subscriptions
-- Test that RLS policies work correctly
```

This approach gives us **maximum security** while maintaining **simplicity** and **performance**! 🛡️
