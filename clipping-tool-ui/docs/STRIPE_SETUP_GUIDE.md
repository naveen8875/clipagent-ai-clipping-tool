# 🎯 Stripe Setup Guide - Complete Billing Integration

This guide covers the complete setup process for integrating Stripe billing with your ClipAgent application.

## 📋 Prerequisites

- Stripe account (create at [stripe.com](https://stripe.com))
- Supabase project with completed migrations
- Next.js application with environment variables configured

## 🔧 Part 1: Stripe Dashboard Configuration

### 1.1 Create Stripe Products & Prices

Navigate to **Products** in your Stripe dashboard and create the following:

#### Free Plan

- **Product Name**: Free Forever Plan
- **Description**: 3 videos per month, basic features
- **Price**: $0.00/month
- **Billing**: One-time (or recurring with $0 amount)

#### Pro Plan

- **Product Name**: Pro Plan
- **Description**: 50 videos per month, advanced features
- **Monthly Price**: $29.00/month (USD) / ₹2,499.00/month (INR)
- **Yearly Price**: $290.00/year (USD) / ₹24,990.00/year (INR)

#### Team Plan

- **Product Name**: Team Plan
- **Description**: Unlimited videos, team features
- **Monthly Price**: $99.00/month (USD) / ₹8,499.00/month (INR)
- **Yearly Price**: $990.00/year (USD) / ₹84,990.00/year (INR)

### 1.2 Copy Price IDs

After creating each price, copy the **Price ID** (starts with `price_`) for each:

```
Free Plan:
- Monthly USD: price_XXXXXXXXXXXXXX
- Monthly INR: price_XXXXXXXXXXXXXX
- Yearly USD: price_XXXXXXXXXXXXXX
- Yearly INR: price_XXXXXXXXXXXXXX

Pro Plan:
- Monthly USD: price_XXXXXXXXXXXXXX
- Monthly INR: price_XXXXXXXXXXXXXX
- Yearly USD: price_XXXXXXXXXXXXXX
- Yearly INR: price_XXXXXXXXXXXXXX

Team Plan:
- Monthly USD: price_XXXXXXXXXXXXXX
- Monthly INR: price_XXXXXXXXXXXXXX
- Yearly USD: price_XXXXXXXXXXXXXX
- Yearly INR: price_XXXXXXXXXXXXXX
```

### 1.3 Configure Webhooks

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. **Endpoint URL**: `https://3accfdaa1492.ngrok-free.app/api/webhooks/stripe`
4. **Events to send**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Webhook Secret** (starts with `whsec_`)

## 🔐 Part 2: Environment Variables Setup

Add these to your `.env.local` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXXX
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXX

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_OR_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Backend URL
MAIN_BACKEND_URL=http://localhost:8000

# Site URL (for redirects)
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Free Plan Prices
STRIPE_FREE_MONTHLY_USD=price_XXXXXXXXXXXXXX
STRIPE_FREE_MONTHLY_INR=price_XXXXXXXXXXXXXX
STRIPE_FREE_YEARLY_USD=price_XXXXXXXXXXXXXX
STRIPE_FREE_YEARLY_INR=price_XXXXXXXXXXXXXX

# Pro Plan Prices
STRIPE_PRO_MONTHLY_USD=price_XXXXXXXXXXXXXX
STRIPE_PRO_MONTHLY_INR=price_XXXXXXXXXXXXXX
STRIPE_PRO_YEARLY_USD=price_XXXXXXXXXXXXXX
STRIPE_PRO_YEARLY_INR=price_XXXXXXXXXXXXXX

# Team Plan Prices
STRIPE_TEAM_MONTHLY_USD=price_XXXXXXXXXXXXXX
STRIPE_TEAM_MONTHLY_INR=price_XXXXXXXXXXXXXX
STRIPE_TEAM_YEARLY_USD=price_XXXXXXXXXXXXXX
STRIPE_TEAM_YEARLY_INR=price_XXXXXXXXXXXXXX
```

## 🗄️ Part 3: Database Configuration

### 3.1 Run Database Migrations

Execute these migrations in order:

```bash
# Run all migrations
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/001_credits_system.sql
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/002_secure_billing_schema.sql
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/003_update_user_trigger_for_billing.sql
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/004_pricing_system_upgrade.sql
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/007_update_user_credits_and_functions.sql
psql -h your-db-host -p 5432 -d postgres -U postgres -f supabase/migrations/009_update_remaining_functions.sql
```

### 3.2 Update Database with Stripe Price IDs

Run this SQL to update your plans with actual Stripe price IDs:

```sql
-- Update Free Plan
UPDATE user_plans SET
  stripe_price_id_monthly_usd = 'price_FREE_MONTHLY_USD_ID',
  stripe_price_id_monthly_inr = 'price_FREE_MONTHLY_INR_ID',
  stripe_price_id_yearly_usd = 'price_FREE_YEARLY_USD_ID',
  stripe_price_id_yearly_inr = 'price_FREE_YEARLY_INR_ID'
WHERE name = 'free';

-- Update Pro Plan
UPDATE user_plans SET
  stripe_price_id_monthly_usd = 'price_PRO_MONTHLY_USD_ID',
  stripe_price_id_monthly_inr = 'price_PRO_MONTHLY_INR_ID',
  stripe_price_id_yearly_usd = 'price_PRO_YEARLY_USD_ID',
  stripe_price_id_yearly_inr = 'price_PRO_YEARLY_INR_ID'
WHERE name = 'pro';

-- Update Team Plan
UPDATE user_plans SET
  stripe_price_id_monthly_usd = 'price_TEAM_MONTHLY_USD_ID',
  stripe_price_id_monthly_inr = 'price_TEAM_MONTHLY_INR_ID',
  stripe_price_id_yearly_usd = 'price_TEAM_YEARLY_USD_ID',
  stripe_price_id_yearly_inr = 'price_TEAM_YEARLY_INR_ID'
WHERE name = 'team';
```

## 🧪 Part 4: Testing Setup

### 4.1 Test Cards (Stripe Test Mode)

Use these test card numbers:

```
# Successful payments
4242 4242 4242 4242 - Visa
4000 0566 5566 5556 - Visa (debit)
5555 5555 5555 4444 - Mastercard

# Failed payments
4000 0000 0000 0002 - Card declined
4000 0000 0000 9995 - Insufficient funds

# 3D Secure authentication
4000 0025 0000 3155 - Requires authentication
```

### 4.2 Test User Flow

1. **Sign up** with a new account
2. **Verify** free plan assignment (3 credits)
3. **Upload a video** to test credit deduction
4. **Navigate to billing** page
5. **Test plan upgrade** with test card
6. **Verify** credit limit increase
7. **Test customer portal** access

### 4.3 Webhook Testing

Use Stripe CLI for local webhook testing:

```bash
# Install Stripe CLI
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Test webhook events
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
```

## 🚀 Part 5: Production Deployment

### 5.1 Switch to Live Mode

1. **Update Environment Variables**:

   - Change `sk_test_` to `sk_live_`
   - Change `pk_test_` to `pk_live_`
   - Update webhook secret to live mode

2. **Update Webhook Endpoint**:

   - Change webhook URL to production domain
   - Verify webhook events are firing

3. **Update Database**:
   - Replace test price IDs with live price IDs
   - Run the SQL update queries with live price IDs

### 5.2 Domain Configuration

Update these URLs in your environment:

```bash
# Production URLs
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
MAIN_BACKEND_URL=https://your-backend-domain.com
```

## 🔍 Part 6: Monitoring & Maintenance

### 6.1 Stripe Dashboard Monitoring

Monitor these regularly:

- **Payments** → Check for failed payments
- **Customers** → Monitor subscription status
- **Webhooks** → Ensure all events are processed
- **Logs** → Check for any errors

### 6.2 Application Monitoring

Check these endpoints:

- `/api/billing/status` - User subscription status
- `/api/billing/history` - Payment history
- `/api/webhooks/stripe` - Webhook processing

### 6.3 Common Issues & Solutions

#### Issue: "Price not found" error

**Solution**: Verify price IDs in database match Stripe dashboard

#### Issue: Webhook not receiving events

**Solution**: Check webhook URL and secret in Stripe dashboard

#### Issue: Credit deduction not working

**Solution**: Verify database triggers are active and functions are working

#### Issue: Customer portal not loading

**Solution**: Check Stripe customer ID is properly stored in database

## 📊 Part 7: Analytics & Reporting

### 7.1 Stripe Reporting

Use Stripe's built-in reporting:

- **Revenue** → Track monthly recurring revenue
- **Customers** → Monitor growth and churn
- **Products** → Analyze plan performance

### 7.2 Custom Analytics

Track these metrics in your application:

- Conversion rates (free → paid)
- Plan upgrade/downgrade patterns
- Credit usage patterns
- Customer lifetime value

## ✅ Part 8: Checklist

Before going live, verify:

- [ ] All Stripe products and prices created
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Price IDs updated in database
- [ ] Webhooks configured and tested
- [ ] Test payments working
- [ ] Customer portal accessible
- [ ] Credit system functioning
- [ ] Error handling in place
- [ ] Monitoring setup complete

## 🆘 Support & Troubleshooting

### Stripe Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)
- [Stripe Status Page](https://status.stripe.com)

### Application Issues

- Check browser console for frontend errors
- Check server logs for backend errors
- Verify database connection and migrations
- Test with Stripe CLI for webhook debugging

---

## 🎉 You're All Set!

Your ClipAgent application now has a fully integrated Stripe billing system with:

- ✅ Multi-currency support (USD/INR)
- ✅ Multiple billing periods (monthly/yearly)
- ✅ Automatic credit management
- ✅ Customer portal integration
- ✅ Webhook-based subscription updates
- ✅ Comprehensive error handling

Happy billing! 💳✨
