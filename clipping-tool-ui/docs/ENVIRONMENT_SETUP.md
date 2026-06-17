# Environment Variables Setup Guide

## Required Environment Variables

Create a `.env.local` file in your project root with the following variables:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Free Plan Prices
STRIPE_FREE_MONTHLY_USD=price_1SAfYXJXrDYPUFOT6XS8lP1Q
STRIPE_FREE_MONTHLY_INR=price_1SAfYWJXrDYPUFOT2usaFreQ
STRIPE_FREE_YEARLY_USD=price_1SAfYVJXrDYPUFOTKaYzZY1q
STRIPE_FREE_YEARLY_INR=price_1SAfYWJXrDYPUFOTYOflOTLt

# Pro Plan Prices
STRIPE_PRO_MONTHLY_USD=price_1SAfYVJXrDYPUFOTuVESaiF7
STRIPE_PRO_MONTHLY_INR=price_1SAfYUJXrDYPUFOTo7g6kG0m
STRIPE_PRO_YEARLY_USD=price_1SAfYUJXrDYPUFOTVVhXukD5
STRIPE_PRO_YEARLY_INR=price_1SAfYTJXrDYPUFOTyYHtJ440

# Team Plan Prices
STRIPE_TEAM_MONTHLY_USD=price_1SAfYTJXrDYPUFOTPJhJL2v0
STRIPE_TEAM_MONTHLY_INR=price_1SAfYSJXrDYPUFOTk2pC2L0b
STRIPE_TEAM_YEARLY_USD=price_1SAfYSJXrDYPUFOTuh4i0vbw
STRIPE_TEAM_YEARLY_INR=price_1SAfYSJXrDYPUFOTasRUrQBB

# Backend API Configuration
BACKEND_URL=your_backend_api_url_here
MAIN_BACKEND_URL=your_main_backend_url_here

# Application Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NODE_ENV=development
```

## Stripe Price ID Mapping

### Free Plan
- **Monthly USD**: `price_1SAfYXJXrDYPUFOT6XS8lP1Q` (Free Forever Plan - 0.00 usd/month)
- **Monthly INR**: `price_1SAfYWJXrDYPUFOT2usaFreQ` (Free Forever Plan - 0.00 inr/month)
- **Yearly USD**: `price_1SAfYVJXrDYPUFOTKaYzZY1q` (Free Forever Plan - 0.00 usd/year)
- **Yearly INR**: `price_1SAfYWJXrDYPUFOTYOflOTLt` (Free Forever Plan - 0.00 inr/year)

### Pro Plan
- **Monthly USD**: `price_1SAfYVJXrDYPUFOTuVESaiF7` (Pro Plan - 29.00 usd/month)
- **Monthly INR**: `price_1SAfYUJXrDYPUFOTo7g6kG0m` (Pro Plan - 2407.00 inr/month)
- **Yearly USD**: `price_1SAfYUJXrDYPUFOTVVhXukD5` (Pro Plan - 279.00 usd/year)
- **Yearly INR**: `price_1SAfYTJXrDYPUFOTyYHtJ440` (Pro Plan - 24500.00 inr/year)

### Team Plan
- **Monthly USD**: `price_1SAfYTJXrDYPUFOTPJhJL2v0` (Team Plan - 89.00 usd/month)
- **Monthly INR**: `price_1SAfYSJXrDYPUFOTk2pC2L0b` (Team Plan - 7000.00 inr/month)
- **Yearly USD**: `price_1SAfYSJXrDYPUFOTuh4i0vbw` (Team Plan - 715.00 usd/year)
- **Yearly INR**: `price_1SAfYSJXrDYPUFOTasRUrQBB` (Team Plan - 62000.00 inr/year)

## Setup Instructions

1. **Copy the environment variables** above into a `.env.local` file
2. **Replace placeholder values** with your actual API keys and URLs
3. **Restart your development server** after adding environment variables
4. **Verify the setup** by checking that billing functionality works correctly

## Security Notes

- Never commit `.env.local` to version control
- Use different keys for development and production
- Keep your Stripe secret keys secure
- Rotate keys regularly for security

## Troubleshooting

If you encounter issues:

1. **Check environment variables** are loaded correctly
2. **Verify Stripe price IDs** match your Stripe dashboard
3. **Ensure Supabase keys** are correct and have proper permissions
4. **Check backend API URLs** are accessible
5. **Restart the development server** after making changes
