# Simplified Billing Flow with Stripe

## Core Principle

**Stripe handles ALL payment/subscription logic. We only track the current state.**

## User Flows

### 1. Plan Purchase/Upgrade/Downgrade

```
User clicks "Subscribe" or "Upgrade"
→ Redirect to Stripe Checkout
→ Complete payment in Stripe
→ Stripe webhook updates our database
→ User sees updated plan on dashboard
```

### 2. Plan Management (Cancel/Change)

```
User clicks "Manage Subscription"
→ Redirect to Stripe Customer Portal
→ Make changes in Stripe
→ Stripe webhook updates our database
→ User sees updated plan on dashboard
```

## Database Schema - Simplified

### What We Actually Need

```sql
-- Add Stripe fields to existing users table
ALTER TABLE users ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'inactive';
-- Values: 'active', 'past_due', 'canceled', 'incomplete', 'trialing'

-- Billing history (optional - for display purposes)
CREATE TABLE billing_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  stripe_invoice_id TEXT,
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) NOT NULL, -- 'paid', 'open', 'void', 'uncollectible'
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### What We DON'T Need

- ❌ `payment_methods` table (Stripe handles this)
- ❌ `plan_change_requests` table (Stripe handles this)
- ❌ Custom payment processing
- ❌ Manual plan change logic

## API Routes - Minimal Set

### Essential Routes Only

```typescript
// 1. Create Stripe Checkout Session
POST / api / billing / create - checkout;
// Body: { planId: string }
// Response: { checkoutUrl: string }

// 2. Create Customer Portal Session
POST / api / billing / customer - portal;
// Response: { portalUrl: string }

// 3. Handle Stripe Webhooks
POST / api / webhooks / stripe;
// Handles all subscription events

// 4. Get Current Subscription Status
GET / api / billing / status;
// Response: { plan, status, nextBillingDate, etc. }
```

## Webhook Events We Handle

```typescript
const WEBHOOK_EVENTS = {
  // New subscription created
  "customer.subscription.created": (event) => {
    // Update user's plan_id, subscription_status, stripe_subscription_id
  },

  // Plan changed
  "customer.subscription.updated": (event) => {
    // Update user's plan_id, subscription_status
  },

  // Subscription cancelled
  "customer.subscription.deleted": (event) => {
    // Update subscription_status to 'canceled'
  },

  // Payment succeeded
  "invoice.payment_succeeded": (event) => {
    // Update subscription_status to 'active'
    // Optionally add to billing_history
  },

  // Payment failed
  "invoice.payment_failed": (event) => {
    // Update subscription_status to 'past_due'
  },
};
```

## Component Integration - Ultra Simple

### BillingDashboard.tsx

```typescript
// Show current plan and status
const { data: subscriptionStatus } = useQuery(
  ["billing-status"],
  fetchSubscriptionStatus
);

// Two main buttons:
// 1. "Upgrade Plan" → Redirect to Stripe Checkout
// 2. "Manage Subscription" → Redirect to Customer Portal
```

### PricingPage.tsx

```typescript
// Each plan card has:
// 1. "Subscribe" button → Redirect to Stripe Checkout
// 2. Show current plan if user is already subscribed
```

### PlanChangeModal.tsx

```typescript
// Simplified to just show:
// "Redirecting to Stripe Checkout..." or "Redirecting to Customer Portal..."
// No complex billing calculations needed!
```

## Implementation Steps

### Step 1: Database Changes (30 minutes)

```sql
-- Add Stripe fields to users table
ALTER TABLE users ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT;
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'inactive';
```

### Step 2: Basic API Routes (2-3 hours)

```typescript
// app/api/billing/create-checkout/route.ts
// app/api/billing/customer-portal/route.ts
// app/api/billing/status/route.ts
// app/api/webhooks/stripe/route.ts
```

### Step 3: Webhook Handler (2-3 hours)

```typescript
// Handle all subscription events
// Update user's plan and status in database
// No complex logic needed
```

### Step 4: Component Updates (2-3 hours)

```typescript
// Update billing components to use Stripe redirects
// Remove complex billing logic
// Add simple status display
```

## Benefits of This Approach

### For Development

- ✅ **Much faster implementation** (8-10 hours total vs 100+ hours)
- ✅ **Less code to maintain** (no custom payment logic)
- ✅ **No PCI compliance** (Stripe handles everything)
- ✅ **No edge cases** (Stripe handles all payment scenarios)

### For Users

- ✅ **Familiar experience** (Stripe's UI is trusted)
- ✅ **All payment methods** (cards, bank accounts, etc.)
- ✅ **Mobile optimized** (Stripe handles responsive design)
- ✅ **Automatic retries** (Stripe handles failed payments)

### For Business

- ✅ **Lower support burden** (users manage billing themselves)
- ✅ **Better conversion** (Stripe's checkout is optimized)
- ✅ **Automatic compliance** (taxes, regulations, etc.)
- ✅ **Fraud protection** (Stripe's built-in protection)

## Updated Implementation Timeline

### Day 1: Database & Basic APIs (4-6 hours)

- Add Stripe fields to users table
- Create basic API routes
- Set up Stripe SDK

### Day 2: Webhook Handler (4-6 hours)

- Implement webhook endpoint
- Handle subscription events
- Test webhook processing

### Day 3: Component Integration (4-6 hours)

- Update billing components
- Add Stripe redirects
- Test complete flow

**Total Time: 12-18 hours (vs 100+ hours with custom approach)**

## Key Insight

**We're not building a billing system. We're building a billing status display system that integrates with Stripe's billing system.**

This approach is:

- **10x faster to implement**
- **10x less code to maintain**
- **10x more reliable** (Stripe handles edge cases)
- **10x better UX** (users trust Stripe)

The only "billing logic" we need is:

1. Show current plan status
2. Redirect to Stripe for changes
3. Update our database when Stripe tells us something changed

That's it! 🎯
