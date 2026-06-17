# Billing System Integration Plan

## Executive Summary

This plan outlines the integration of the existing billing components from the `billing/` folder into our current Supabase-based ClipAgent system. The integration will connect the sophisticated billing UI with our real database schema and user management system.

## Current System Analysis

### Existing Billing Components (billing/ folder)

- **BillingDashboard.tsx**: Main dashboard with subscription overview, usage tracking, billing history
- **PlanCard.tsx**: Individual plan display component with upgrade/downgrade logic
- **PlanChangeModal.tsx**: Confirmation modal for plan changes with billing details
- **PricingPage.tsx**: Complete pricing page with FAQ and plan selection
- **Dependencies**: Uses static JSON files (`plans.json`, `user.json`) for data

### Current Database Schema (Supabase)

- **user_plans**: Plans table with credits, pricing, features
- **public.users**: User profiles with plan_id, credits_used, reset_date
- **user_credits**: Credit tracking with available/used credits
- **credit_transactions**: Transaction history for billing
- **videos**: Video processing records

### Current API Structure

- **GET /api/auth/user**: Returns user profile with credits data
- **GET /api/user/credits**: Returns current credit status
- **UserProfileContext**: React context for user data management

## Integration Strategy

### Phase 1: Data Layer Integration

**Goal**: Replace static JSON data with real database queries

#### 1.1 Create Billing API Routes

```
/api/billing/
├── plans/route.ts          # GET all available plans
├── current-plan/route.ts   # GET user's current plan details
├── usage/route.ts          # GET current usage statistics
├── history/route.ts        # GET billing/payment history
└── change-plan/route.ts    # POST plan change requests
```

#### 1.2 Data Transformation Layer

- **Plans API**: Transform `user_plans` table to match component expectations
- **Usage API**: Aggregate data from `user_credits`, `videos`, `credit_transactions`
- **History API**: Build billing history from `credit_transactions` and payment records
- **Plan Change API**: Handle plan upgrades/downgrades with proper validation

### Phase 2: Component Integration

**Goal**: Connect billing components with real data sources

#### 2.1 Replace Static Data Sources

- **BillingDashboard**: Replace `plansData` and `userData` imports with API calls
- **PricingPage**: Use real plans from database instead of JSON
- **PlanCard**: Connect with actual user plan data
- **PlanChangeModal**: Integrate with real billing system

#### 2.2 State Management Integration

- **React Query**: Add billing-related queries to existing QueryClient
- **UserProfileContext**: Extend to include billing data
- **Optimistic Updates**: Handle plan changes with proper loading states

### Phase 3: User Flow Enhancement

**Goal**: Create seamless user experience with proper error handling

#### 3.1 Navigation Integration

- **Header Integration**: Add billing link to navigation
- **Protected Routes**: Ensure billing pages are properly protected
- **Breadcrumbs**: Add proper navigation context

#### 3.2 Error Handling & Loading States

- **API Error Handling**: Proper error boundaries for billing operations
- **Loading Skeletons**: Consistent loading states across components
- **Toast Notifications**: Success/error feedback for user actions

### Phase 4: Payment Integration

**Goal**: Connect with real payment processing (future-ready)

#### 4.1 Payment Method Management

- **Stripe Integration**: Prepare for payment method storage
- **Card Management**: Secure payment method handling
- **Invoice Generation**: Automated billing and invoice creation

#### 4.2 Subscription Management

- **Plan Changes**: Handle prorated billing and immediate/delayed changes
- **Cancellation Flow**: Proper subscription cancellation with data retention
- **Refund Handling**: Support for refunds and chargebacks

## Detailed Implementation Plan

### 1. API Routes Structure

#### `/api/billing/plans/route.ts`

```typescript
// GET /api/billing/plans
// Returns all available plans with current user context
interface PlanResponse {
  plans: Plan[];
  currentPlan: string;
  canUpgrade: boolean;
  canDowngrade: boolean;
}
```

#### `/api/billing/current-plan/route.ts`

```typescript
// GET /api/billing/current-plan
// Returns detailed current plan with usage
interface CurrentPlanResponse {
  plan: Plan;
  usage: {
    credits: { used: number; available: number; resetDate: string };
    storage: { used: number; limit: number };
    videos: { processed: number; limit: number };
  };
  billing: {
    nextBillingDate: string;
    amount: number;
    status: "active" | "past_due" | "canceled";
  };
}
```

#### `/api/billing/usage/route.ts`

```typescript
// GET /api/billing/usage
// Returns detailed usage statistics
interface UsageResponse {
  credits: CreditUsage;
  storage: StorageUsage;
  videos: VideoUsage;
  apiRequests: ApiUsage;
  period: { start: string; end: string };
}
```

#### `/api/billing/history/route.ts`

```typescript
// GET /api/billing/history
// Returns billing and payment history
interface HistoryResponse {
  transactions: Transaction[];
  invoices: Invoice[];
  pagination: { page: number; total: number; limit: number };
}
```

#### `/api/billing/change-plan/route.ts`

```typescript
// POST /api/billing/change-plan
// Handles plan changes with validation
interface ChangePlanRequest {
  planId: string;
  effectiveDate: "immediate" | "next_cycle";
  paymentMethodId?: string;
}
```

### 2. Component Integration Points

#### BillingDashboard.tsx Integration

```typescript
// Replace static data with React Query
const { data: billingData, isLoading } = useQuery({
  queryKey: ["billing-dashboard"],
  queryFn: () => fetchBillingDashboard(),
  staleTime: 5 * 60 * 1000, // 5 minutes
});

// Usage data integration
const { data: usageData } = useQuery({
  queryKey: ["billing-usage"],
  queryFn: () => fetchBillingUsage(),
  refetchInterval: 30 * 1000, // 30 seconds
});
```

#### PricingPage.tsx Integration

```typescript
// Dynamic plan loading
const { data: plansData } = useQuery({
  queryKey: ["billing-plans"],
  queryFn: () => fetchAvailablePlans(),
});

// Plan change handling
const changePlanMutation = useMutation({
  mutationFn: changeUserPlan,
  onSuccess: () => {
    queryClient.invalidateQueries(["billing-dashboard"]);
    toast.success("Plan changed successfully!");
  },
});
```

### 3. User Flow Design

#### Primary User Flows

**Flow 1: View Billing Dashboard**

1. User navigates to `/billing` from header
2. System loads current plan, usage, and billing history
3. User sees overview with upgrade prompts if needed
4. User can navigate to pricing page or manage payment methods

**Flow 2: Upgrade/Downgrade Plan**

1. User clicks "Upgrade" or "Change Plan" button
2. System navigates to pricing page with current plan highlighted
3. User selects new plan and clicks "Select Plan"
4. System shows PlanChangeModal with billing details
5. User confirms change with payment method
6. System processes change and updates user's plan
7. User sees success message and updated dashboard

**Flow 3: View Usage Details**

1. User views usage summary on billing dashboard
2. User can click on specific usage metrics for details
3. System shows detailed breakdown with progress bars
4. User can see reset dates and limits

**Flow 4: Manage Payment Methods**

1. User views current payment method on dashboard
2. User can add new payment method or update existing
3. System integrates with payment processor (Stripe)
4. User sees updated payment method information

#### Error Handling Flows

**Error Flow 1: Payment Failure**

1. System detects payment failure during plan change
2. User sees error message with retry options
3. User can update payment method and retry
4. System processes payment with new method

**Error Flow 2: Plan Change Restrictions**

1. User attempts invalid plan change (e.g., downgrade with overage)
2. System shows warning with options to resolve
3. User can either upgrade further or clean up usage
4. System allows plan change once restrictions are met

### 4. Database Schema Extensions

#### Additional Tables Needed

```sql
-- Add Stripe customer ID to users table
ALTER TABLE users ADD COLUMN stripe_customer_id TEXT;

-- Billing history table
CREATE TABLE billing_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id UUID REFERENCES user_plans(id),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) NOT NULL, -- 'paid', 'pending', 'failed', 'refunded'
  stripe_invoice_id TEXT,
  stripe_payment_intent_id TEXT,
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Plan change requests table
CREATE TABLE plan_change_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  from_plan_id UUID REFERENCES user_plans(id),
  to_plan_id UUID REFERENCES user_plans(id),
  effective_date TIMESTAMP NOT NULL,
  status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
  stripe_subscription_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Security Considerations

#### Authentication & Authorization

- All billing routes require authentication
- Users can only access their own billing data
- Plan changes require additional verification
- Payment method updates require re-authentication

#### Data Protection

- Sensitive payment data stored securely (Stripe)
- API keys and secrets in environment variables
- Rate limiting on billing operations
- Audit logging for all billing actions

### 6. Testing Strategy

#### Unit Tests

- API route testing with mock data
- Component testing with different user states
- Database function testing
- Payment integration testing (with Stripe test mode)

#### Integration Tests

- End-to-end billing flows
- Plan change scenarios
- Payment failure handling
- Error state recovery

#### User Acceptance Testing

- Billing dashboard usability
- Plan change flow clarity
- Payment method management
- Error message clarity

## Implementation Timeline

### Week 1: API Foundation

- Create billing API routes
- Implement database queries
- Set up data transformation layer
- Basic error handling

### Week 2: Component Integration

- Integrate BillingDashboard with real data
- Connect PricingPage to API
- Update PlanCard and PlanChangeModal
- Add loading states and error handling

### Week 3: User Flow Enhancement

- Implement navigation integration
- Add proper breadcrumbs and routing
- Enhance error handling and user feedback
- Add toast notifications and success states

### Week 4: Payment Integration

- Integrate Stripe payment processing
- Implement payment method management
- Add invoice generation
- Handle subscription management

### Week 5: Testing & Polish

- Comprehensive testing
- Performance optimization
- UI/UX polish
- Documentation updates

## Success Metrics

### Technical Metrics

- API response times < 500ms
- 99.9% uptime for billing operations
- Zero payment data leaks
- < 1% plan change failure rate

### User Experience Metrics

- < 3 clicks to complete plan change
- Clear error messages for all failure scenarios
- Intuitive billing dashboard navigation
- Positive user feedback on billing flow

### Business Metrics

- Increased plan upgrade conversion
- Reduced billing support tickets
- Improved user retention
- Faster payment processing

## Risk Mitigation

### Technical Risks

- **Database Performance**: Index optimization and query caching
- **Payment Failures**: Comprehensive error handling and retry logic
- **Data Consistency**: Transaction management and rollback procedures

### Business Risks

- **User Confusion**: Clear UI/UX and comprehensive help documentation
- **Payment Disputes**: Proper audit trails and dispute resolution processes
- **Compliance**: PCI DSS compliance and data protection regulations

## Future Enhancements

### Phase 2 Features

- Advanced usage analytics
- Custom billing cycles
- Team/organization billing
- Usage-based pricing models

### Phase 3 Features

- Multi-currency support
- Tax calculation and compliance
- Advanced reporting and analytics
- API billing for third-party integrations

---

This integration plan provides a comprehensive roadmap for connecting the sophisticated billing components with our real Supabase-based system, ensuring a seamless user experience while maintaining security and performance standards.
