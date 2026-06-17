# Stripe Integration Approach - Updated Plan

## Overview

Based on the decision to use Stripe-managed payments, we've updated the billing integration plan to leverage Stripe's infrastructure for payment processing and subscription management.

## Key Changes Made

### 1. Payment Processing Approach

**Before**: Custom payment method management
**After**: Stripe Checkout + Webhooks

- **Stripe Checkout**: Users complete payments through Stripe's hosted checkout
- **Webhooks**: Stripe notifies us of subscription events (created, updated, cancelled)
- **Customer Portal**: Users manage their billing through Stripe's customer portal
- **No Payment Data Storage**: We don't store any sensitive payment information

### 2. Database Schema Simplification

**Removed**:

- `payment_methods` table (Stripe handles this)
- Payment method management APIs
- Custom payment processing logic

**Added**:

- `stripe_customer_id` field in users table
- Simplified webhook handling
- Subscription status tracking

### 3. API Routes Updated

**New Routes**:

- `POST /api/billing/create-checkout` - Create Stripe Checkout session
- `POST /api/billing/customer-portal` - Generate customer portal session
- `POST /api/webhooks/stripe` - Handle Stripe webhooks

**Removed Routes**:

- Payment method management endpoints
- Custom payment processing endpoints

### 4. Component Integration Simplified

**BillingDashboard.tsx**:

- Display subscription status from Stripe
- Link to customer portal for billing management
- Show billing history from Stripe data

**PricingPage.tsx**:

- Redirect to Stripe Checkout for plan purchases
- No custom payment forms needed

**PlanChangeModal.tsx**:

- Simplified to show plan comparison
- Redirect to customer portal for plan changes

## Implementation Benefits

### Security

- ✅ No PCI compliance requirements (Stripe handles it)
- ✅ No sensitive payment data in our database
- ✅ Stripe's security best practices
- ✅ Automatic fraud detection

### Development Speed

- ✅ Faster implementation (no custom payment forms)
- ✅ Less code to maintain
- ✅ Stripe handles edge cases
- ✅ Built-in mobile optimization

### User Experience

- ✅ Familiar Stripe checkout experience
- ✅ Multiple payment methods supported
- ✅ Automatic retry logic for failed payments
- ✅ Customer portal for self-service

### Maintenance

- ✅ Stripe handles payment processing updates
- ✅ Automatic tax calculation (if enabled)
- ✅ Built-in invoice generation
- ✅ Compliance updates handled by Stripe

## Updated Implementation Timeline

### Phase 4: Stripe Integration (Week 4)

**Chunk 4.1: Stripe Integration Setup (6-8 hours)**

- Configure Stripe SDK
- Create checkout session API
- Set up webhook handling
- Test mode configuration

**Chunk 4.2: Subscription Management (8-10 hours)**

- Sync subscription status via webhooks
- Handle plan changes
- Customer portal integration
- Cancellation flow

**Chunk 4.3: Checkout Integration UI (6-8 hours)**

- Integrate checkout in components
- Add customer portal access
- Display subscription status
- Show billing history

## Webhook Events to Handle

```typescript
// Key Stripe webhook events
const WEBHOOK_EVENTS = {
  "customer.subscription.created": "Handle new subscription",
  "customer.subscription.updated": "Handle plan changes",
  "customer.subscription.deleted": "Handle cancellations",
  "invoice.payment_succeeded": "Handle successful payments",
  "invoice.payment_failed": "Handle failed payments",
  "customer.subscription.trial_will_end": "Handle trial endings",
};
```

## Database Schema Changes

```sql
-- Add Stripe customer ID to users table
ALTER TABLE users ADD COLUMN stripe_customer_id TEXT;

-- Billing history table (simplified)
CREATE TABLE billing_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT,
  stripe_invoice_id TEXT,
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) NOT NULL,
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Plan change requests table
CREATE TABLE plan_change_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT,
  from_plan_id UUID REFERENCES user_plans(id),
  to_plan_id UUID REFERENCES user_plans(id),
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Considerations

### Webhook Security

- Verify webhook signatures from Stripe
- Use HTTPS endpoints only
- Implement idempotency for webhook processing
- Rate limiting on webhook endpoints

### Data Protection

- No sensitive payment data stored locally
- Stripe customer IDs are not sensitive
- All payment data encrypted by Stripe
- GDPR compliance through Stripe

## Testing Strategy

### Stripe Test Mode

- Use Stripe test keys for development
- Test webhook events using Stripe CLI
- Test all payment scenarios
- Verify subscription lifecycle

### Webhook Testing

- Test all subscription events
- Verify database updates
- Test error handling
- Ensure idempotency

## Environment Variables

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Checkout
STRIPE_SUCCESS_URL=https://yourapp.com/billing/success
STRIPE_CANCEL_URL=https://yourapp.com/billing/cancel
```

## User Flow with Stripe

### Plan Purchase Flow

1. User selects plan on pricing page
2. Click "Subscribe" → Redirect to Stripe Checkout
3. Complete payment on Stripe
4. Redirect back to success page
5. Webhook updates user's plan in database
6. User sees updated plan on dashboard

### Plan Change Flow

1. User clicks "Change Plan" on dashboard
2. Redirect to Stripe Customer Portal
3. Make changes in Stripe portal
4. Webhook updates database
5. User sees updated plan

### Cancellation Flow

1. User clicks "Cancel Subscription"
2. Redirect to Stripe Customer Portal
3. Cancel in Stripe portal
4. Webhook marks subscription as cancelled
5. User retains access until period end

This approach significantly simplifies our implementation while providing a more secure and maintainable billing system.
