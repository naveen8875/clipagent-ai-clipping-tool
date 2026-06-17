# 📋 **COMPREHENSIVE PRICING SYSTEM UPGRADE PLAN**

## **🎯 Overview**

This document outlines the complete implementation plan for upgrading ClipAgent's pricing system to support:

- ✅ **3 Pricing Plans**: Free Forever, Pro Plan, Team Plan
- ✅ **Multi-Currency Support**: USD and INR
- ✅ **Dual Billing Periods**: Monthly and Yearly
- ✅ **Updated Free Plan**: Increase from 2 to 3 credits
- ✅ **Enhanced Features**: Better plan descriptions and feature lists

---

## **🔍 CURRENT STATE ANALYSIS**

### **Existing Structure**

- `user_plans` table with basic fields: `name`, `display_name`, `monthly_credits`, `price_monthly`, `features`
- **Free plan**: 2 credits, $0/month
- **Pro plan**: Unlimited credits (-1), $29/month
- Stripe price IDs stored in environment variables
- Single currency support (USD only in practice)
- No yearly billing support

### **Current Limitations**

- ❌ No yearly pricing support
- ❌ No multi-currency pricing in database
- ❌ No Team plan
- ❌ Free plan limited to 2 credits (needs to be 3)
- ❌ No structured pricing tiers in database
- ❌ Limited feature descriptions

---

## **📊 NEW PRICING STRUCTURE**

### **Plan Definitions**

```javascript
const plans = [
  {
    name: "Free Forever",
    price: "$0",
    period: "",
    description:
      "Start creating viral shorts for free and see how our AI transforms your videos into shareable hits—perfect for testing the waters!",
    episodes: "3 videos per month", // Updated from 5
    popular: false,
    features: [
      "Upload 3 videos every month to try it out",
      "Get 10-15 attention-grabbing short clips per video",
      "AI finds the best moments that could blow up online",
      "No watermarks, so your clips look pro from day one",
      "Join our community for tips and friendly support",
    ],
  },
  {
    name: "Pro Plan",
    price: "$29",
    period: "/month or $19/month billed yearly (save 35%)",
    description:
      "Supercharge your content game with tools to create viral clips faster—perfect for creators ready to grow their audience and save time!",
    episodes: "20 videos per month",
    popular: true,
    features: [
      "Process 20 videos each month for endless content",
      "Get 10-20 premium clips per video, handpicked by smart AI",
      "Customize clips with your own prompts for perfect results",
      "No watermarks for clean, professional-looking shorts",
      "Fast-track support to answer your questions ASAP",
    ],
  },
  {
    name: "Team Plan",
    price: "$99",
    period: "/month or $79/month billed yearly (save 20%)",
    description:
      "Unleash unlimited video creation for agencies and teams, with powerful tools to collaborate and keep your brand on point!",
    episodes: "Unlimited video uploads + team tools",
    popular: false,
    features: [
      "Upload unlimited videos with no restrictions",
      "Track what works with a simple analytics dashboard",
      "Process tons of videos at once for max efficiency",
      "Get your feature requests prioritized for faster updates",
      "Train AI to match your brand's unique style",
    ],
  },
];
```

---

## **🏗️ IMPLEMENTATION BREAKDOWN**

## **Phase 1: Database Schema Restructuring**

### **1.1 Update user_plans Table Structure**

**New Fields Required:**

```sql
-- Pricing fields
price_monthly_usd DECIMAL(10,2) DEFAULT 0.00,
price_monthly_inr DECIMAL(10,2) DEFAULT 0.00,
price_yearly_usd DECIMAL(10,2) DEFAULT 0.00,
price_yearly_inr DECIMAL(10,2) DEFAULT 0.00,

-- Stripe integration
stripe_price_id_monthly_usd TEXT,
stripe_price_id_monthly_inr TEXT,
stripe_price_id_yearly_usd TEXT,
stripe_price_id_yearly_inr TEXT,

-- Plan details
description TEXT,
episodes_limit VARCHAR(50), -- "3 videos per month", "Unlimited", etc.
popular BOOLEAN DEFAULT false,
billing_period VARCHAR(10) DEFAULT 'monthly', -- 'monthly', 'yearly', 'both'
```

### **1.2 Migration Strategy**

- **Backup existing data** before changes
- **Add new columns** with default values
- **Migrate existing data** to new structure
- **Drop old columns** after migration
- **Update all functions** that reference old columns

---

## **Phase 2: Data Migration & Cleanup**

### **2.1 Clean Up Existing Plans**

```sql
-- Delete existing plans
DELETE FROM user_plans WHERE name IN ('free', 'pro');

-- Insert new plan structure
INSERT INTO user_plans (
  name, display_name, monthly_credits,
  price_monthly_usd, price_monthly_inr, price_yearly_usd, price_yearly_inr,
  stripe_price_id_monthly_usd, stripe_price_id_monthly_inr,
  stripe_price_id_yearly_usd, stripe_price_id_yearly_inr,
  description, episodes_limit, popular, features
) VALUES
-- Free Plan
('free', 'Free Forever', 3, 0.00, 0.00, 0.00, 0.00,
 'price_free_monthly_usd', 'price_free_monthly_inr',
 'price_free_yearly_usd', 'price_free_yearly_inr',
 'Start creating viral shorts for free...', '3 videos per month', false,
 '{"max_video_size": "100MB", "support": "community"}'),

-- Pro Plan
('pro', 'Pro Plan', 20, 29.00, 2499.00, 228.00, 19599.00,
 'price_pro_monthly_usd', 'price_pro_monthly_inr',
 'price_pro_yearly_usd', 'price_pro_yearly_inr',
 'Supercharge your content game...', '20 videos per month', true,
 '{"max_video_size": "Unlimited", "support": "priority", "api_access": true}'),

-- Team Plan
('team', 'Team Plan', -1, 99.00, 8499.00, 948.00, 81599.00,
 'price_team_monthly_usd', 'price_team_monthly_inr',
 'price_team_yearly_usd', 'price_team_yearly_inr',
 'Unleash unlimited video creation...', 'Unlimited', false,
 '{"max_video_size": "Unlimited", "support": "priority", "api_access": true, "analytics": true, "team_collaboration": true}');
```

### **2.2 Update Default Credits**

- Change free plan from 2 to 3 credits
- Update all related functions and triggers
- Update existing user credit records

---

## **Phase 3: Stripe Integration Updates**

### **3.1 Environment Variables**

```env
# Free Plan
STRIPE_FREE_MONTHLY_USD=price_xxx
STRIPE_FREE_MONTHLY_INR=price_xxx
STRIPE_FREE_YEARLY_USD=price_xxx
STRIPE_FREE_YEARLY_INR=price_xxx

# Pro Plan
STRIPE_PRO_MONTHLY_USD=price_xxx
STRIPE_PRO_MONTHLY_INR=price_xxx
STRIPE_PRO_YEARLY_USD=price_xxx
STRIPE_PRO_YEARLY_INR=price_xxx

# Team Plan
STRIPE_TEAM_MONTHLY_USD=price_xxx
STRIPE_TEAM_MONTHLY_INR=price_xxx
STRIPE_TEAM_YEARLY_USD=price_xxx
STRIPE_TEAM_YEARLY_INR=price_xxx
```

### **3.2 Stripe Configuration Updates**

- Update `lib/stripe.ts` to handle 3 plans × 2 currencies × 2 billing periods
- Update `getPlanPriceId()` function for new structure
- Update `getPlanNameFromPriceId()` function

---

## **Phase 4: API Route Updates**

### **4.1 Billing API Routes**

- **`/api/billing/status`**: Update to handle new plan structure
- **`/api/billing/create-checkout`**: Add billing period parameter
- **`/api/billing/history`**: Update to show correct plan names
- **Webhook handler**: Update to handle new price IDs

### **4.2 New API Endpoint**

- **`/api/plans`**: GET endpoint to fetch all plans with pricing

---

## **Phase 5: Frontend Component Updates**

### **5.1 PricingPage Component**

- Add billing period toggle (Monthly/Yearly)
- Update currency selector
- Display 3 plans instead of 2
- Show yearly savings
- Update plan comparison

### **5.2 BillingDashboard Component**

- Update plan display logic
- Handle yearly billing display
- Update usage tracking for Team plan

### **5.3 PlanCard Component**

- Add billing period parameter
- Display yearly savings
- Update pricing logic
- Handle unlimited credits display

---

## **Phase 6: Database Functions Updates**

### **6.1 Update All SQL Functions**

- `handle_new_user()`: Update to use 3 credits for free plan
- `check_user_credits()`: Handle Team plan unlimited credits
- `reset_user_credits()`: Handle new plan structure
- `handle_video_upload()`: Handle Team plan unlimited credits

### **6.2 New Functions**

- `get_plan_pricing()`: Get pricing for specific plan/currency/period
- `validate_plan_upgrade()`: Validate plan changes

---

## **Phase 7: Edge Cases & Validation**

### **7.1 Data Validation**

- ✅ Ensure all existing users maintain their current plan
- ✅ Validate Stripe price IDs exist for all combinations
- ✅ Handle currency conversion rates
- ✅ Validate billing period changes
- ✅ Handle plan downgrades/upgrades

### **7.2 Migration Safety**

- ✅ Backup existing data before migration
- ✅ Test migration on staging environment
- ✅ Rollback plan if migration fails
- ✅ Validate all functions work after migration

### **7.3 User Experience**

- ✅ Existing users see their current plan correctly
- ✅ New users get 3 credits on free plan
- ✅ Pricing display is consistent across all components
- ✅ Currency conversion is accurate
- ✅ Yearly savings are clearly displayed

---

## **Phase 8: Testing & Validation**

### **8.1 Database Testing**

- Test all SQL functions with new data structure
- Validate RLS policies work with new columns
- Test credit allocation for all plan types
- Validate billing history accuracy

### **8.2 API Testing**

- Test all billing API endpoints
- Validate Stripe integration works
- Test webhook handling for new price IDs
- Validate error handling

### **8.3 Frontend Testing**

- Test pricing page with all combinations
- Validate billing dashboard displays correctly
- Test plan selection and checkout flow
- Validate currency switching

---

## **📊 IMPLEMENTATION PHASES SUMMARY**

| Phase       | Focus              | Duration  | Risk Level | Dependencies        |
| ----------- | ------------------ | --------- | ---------- | ------------------- |
| **Phase 1** | Database Schema    | 2-3 hours | 🔴 High    | Service role access |
| **Phase 2** | Data Migration     | 1-2 hours | 🔴 High    | Phase 1 complete    |
| **Phase 3** | Stripe Integration | 2-3 hours | 🟡 Medium  | Stripe price IDs    |
| **Phase 4** | API Updates        | 2-3 hours | 🟡 Medium  | Phase 1-2 complete  |
| **Phase 5** | Frontend Updates   | 3-4 hours | 🟡 Medium  | Phase 4 complete    |
| **Phase 6** | Database Functions | 2-3 hours | 🔴 High    | Phase 1-2 complete  |
| **Phase 7** | Edge Cases         | 2-3 hours | 🟡 Medium  | All phases complete |
| **Phase 8** | Testing            | 2-3 hours | 🟢 Low     | All phases complete |

**Total Estimated Time: 16-24 hours**

---

## **🚨 CRITICAL CONSIDERATIONS**

### **High-Risk Areas**

1. **Database Migration**: Changing core table structure
2. **Existing User Data**: Ensuring no data loss
3. **Stripe Integration**: Multiple price IDs per plan
4. **Credit System**: Updating from 2 to 3 credits

### **Mitigation Strategies**

1. **Comprehensive Backups**: Before any database changes
2. **Staging Environment**: Test all changes first
3. **Gradual Rollout**: Deploy in phases
4. **Rollback Plan**: Quick revert if issues arise

### **Dependencies**

1. **Stripe Price IDs**: Must be created in Stripe dashboard first
2. **Environment Variables**: All new variables must be set
3. **Database Access**: Service role permissions required
4. **Testing Environment**: Staging environment for validation

---

## **✅ SUCCESS CRITERIA**

### **Technical Success**

- [ ] All 3 plans display correctly with proper pricing
- [ ] Multi-currency support works (USD/INR)
- [ ] Yearly billing with savings calculation works
- [ ] Free plan users get 3 credits instead of 2
- [ ] All existing users maintain their current plans
- [ ] Stripe integration handles all price ID combinations

### **User Experience Success**

- [ ] Pricing page shows all plans with clear comparisons
- [ ] Billing dashboard displays correct plan information
- [ ] Currency switching works seamlessly
- [ ] Yearly savings are clearly highlighted
- [ ] Plan upgrade/downgrade flows work correctly

### **Business Success**

- [ ] New pricing structure is live and functional
- [ ] Revenue tracking works for all plan combinations
- [ ] Billing history shows correct plan names and amounts
- [ ] Webhook processing handles all new price IDs
- [ ] Customer portal integration works for all plans

---

## **📝 IMPLEMENTATION CHECKLIST**

### **Pre-Implementation**

- [ ] Create Stripe price IDs for all plan/currency/period combinations
- [ ] Set up all environment variables
- [ ] Backup production database
- [ ] Set up staging environment for testing

### **Database Changes**

- [ ] Create migration script for user_plans table
- [ ] Update all SQL functions
- [ ] Test migration on staging
- [ ] Run migration on production

### **Backend Updates**

- [ ] Update Stripe configuration
- [ ] Update all API routes
- [ ] Update webhook handlers
- [ ] Test all API endpoints

### **Frontend Updates**

- [ ] Update PricingPage component
- [ ] Update BillingDashboard component
- [ ] Update PlanCard component
- [ ] Test all user flows

### **Post-Implementation**

- [ ] Validate all functionality works
- [ ] Monitor for any errors
- [ ] Update documentation
- [ ] Notify team of changes

---

This comprehensive plan ensures a safe, thorough migration to the new pricing structure while maintaining all existing functionality and user data integrity.
