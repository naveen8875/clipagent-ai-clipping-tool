# Credits System Setup Guide

## 🚀 Quick Start

### 1. **Database Setup**

Run the SQL migration to create all tables, functions, and triggers:

```sql
-- Run this in your Supabase SQL editor
-- File: supabase/migrations/001_credits_system.sql
```

### 2. **Environment Variables**

Add these to your `.env.local`:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Site Configuration
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Main Backend Configuration
MAIN_BACKEND_URL=http://localhost:8000
```

### 3. **Test the System**

1. **Start your development server:**

   ```bash
   npm run dev
   ```

2. **Create a test user:**

   - Go to `/auth`
   - Sign up with a new email
   - Check your email for confirmation

3. **Verify credits system:**
   - Go to `/dashboard/credits`
   - Check credit counter on home page
   - Try uploading a video

## 🔧 API Endpoints

### **Credits API**

- `GET /api/user/credits` - Get current credit status
- `GET /api/user/credits/history` - Get transaction history

### **Video API (Auth Layer)**

- `POST /api/videos` - Upload video (triggers credit deduction)
- `GET /api/videos` - Get user's videos

## 🎯 How It Works

### **User Registration Flow:**

1. User signs up → `auth.users` record created
2. Trigger `on_auth_user_created` fires automatically
3. Function `handle_new_user()` creates `public.users` record
4. User gets Free plan with 2 credits
5. Email confirmation required for dashboard access

### **Video Upload Flow:**

1. User uploads video → `videos` record created
2. Trigger `on_video_uploaded` fires automatically
3. Function `handle_video_upload()` deducts 1 credit
4. Transaction logged in `credit_transactions`
5. Request forwarded to main backend

### **Credit Management:**

- **Free Plan**: 2 credits per month
- **Pro Plan**: Unlimited credits
- **Monthly Reset**: Automatic credit reset
- **Audit Trail**: All transactions logged

## 🧪 Testing Scenarios

### **Test 1: New User Registration**

```bash
# 1. Sign up with new email
# 2. Check database for:
#    - auth.users record
#    - public.users record
#    - user_credits record
#    - credit_transactions record
```

### **Test 2: Credit Deduction**

```bash
# 1. Upload a video
# 2. Check database for:
#    - videos record
#    - updated user_credits
#    - new credit_transactions record
```

### **Test 3: Credit Limit**

```bash
# 1. Upload 2 videos (exhaust free credits)
# 2. Try to upload 3rd video
# 3. Should get "Insufficient credits" error
```

### **Test 4: Monthly Reset**

```bash
# 1. Manually update reset_date to past date
# 2. Call check_user_credits function
# 3. Should automatically reset credits
```

## 🔍 Database Queries for Testing

### **Check User Credits**

```sql
SELECT * FROM check_user_credits('user-uuid-here');
```

### **View Credit Transactions**

```sql
SELECT * FROM credit_transactions
WHERE user_id = (
  SELECT id FROM public.users
  WHERE auth_user_id = 'user-uuid-here'
)
ORDER BY created_at DESC;
```

### **Check User Plan**

```sql
SELECT u.*, up.name as plan_name, up.monthly_credits
FROM public.users u
JOIN user_plans up ON u.plan_id = up.id
WHERE u.auth_user_id = 'user-uuid-here';
```

## 🚨 Troubleshooting

### **Common Issues:**

1. **"User not found" error:**

   - Check if `public.users` record exists
   - Verify trigger fired on user creation

2. **"Insufficient credits" error:**

   - Check `user_credits` table
   - Verify plan assignment

3. **Credit counter not updating:**
   - Check API endpoint responses
   - Verify frontend state management

### **Debug Queries:**

```sql
-- Check if user exists in public.users
SELECT * FROM public.users WHERE auth_user_id = 'user-uuid';

-- Check credit records
SELECT * FROM user_credits WHERE user_id = 'public-user-id';

-- Check recent transactions
SELECT * FROM credit_transactions
WHERE user_id = 'public-user-id'
ORDER BY created_at DESC LIMIT 10;
```

## 📊 Monitoring

### **Key Metrics to Track:**

- Credit usage per user
- Plan upgrade conversions
- Monthly reset frequency
- Upload success rates

### **Database Monitoring:**

- Trigger execution times
- Function performance
- RLS policy effectiveness
- Transaction log growth

## 🎯 Next Steps

1. **Deploy to Production:**

   - Run migration on production database
   - Update environment variables
   - Test with real users

2. **Admin Features:**

   - Plan management interface
   - User credit adjustments
   - Analytics dashboard

3. **Integration:**
   - Connect with main backend
   - Set up webhooks
   - Add payment processing

---

## 🎉 Success!

Your credits system is now fully implemented with:

- ✅ Database schema and triggers
- ✅ API endpoints
- ✅ Frontend components
- ✅ Automatic credit management
- ✅ Audit trail
- ✅ Security policies

The system will automatically handle user creation, credit deduction, and monthly resets without any manual intervention!
