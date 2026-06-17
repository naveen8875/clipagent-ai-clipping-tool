# Authentication System Overhaul Plan

## 🎯 Overview

Complete redesign of the authentication system to streamline user flows, implement proper email confirmation handling, and create a unified password management system.

## 📋 Core Requirements

### 1. **Page Structure Changes**

- Remove unnecessary auth pages (keep only main auth page)
- Move update password functionality to dashboard routes
- Implement forgot password flow with email redirect
- Handle email confirmation states with resend functionality

### 2. **Rate Limiting**

- Users can send confirmation emails every 60 seconds
- Users can send forgot password requests every 60 seconds
- Implemented using session storage for client-side tracking
- Server-side validation for security

## 📁 File Structure Changes

### 🗑️ Files/Directories to Remove

```
app/auth/
├── login/page.tsx                    ❌ Remove
├── sign-up/page.tsx                  ❌ Remove
├── sign-up-success/page.tsx          ❌ Remove
├── error/page.tsx                    ❌ Remove
├── forgot-password/page.tsx          ❌ Remove
└── update-password/page.tsx          ❌ Remove
```

### 📄 Files to Create/Modify

```
app/
├── auth/
│   └── page.tsx                      🔄 Modify existing
├── dashboard/
│   └── update-password/
│       └── page.tsx                  ➕ Create new
└── api/auth/
    ├── resend-verification/
    │   └── route.ts                  ➕ Create new
    └── reset-password/
        └── route.ts                  ➕ Create new
```

## 🔧 Implementation Details

### 1. **Main Auth Page Updates** (`app/auth/page.tsx`)

#### **New State Management**

```typescript
const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
const [showResendModal, setShowResendModal] = useState(false);
const [emailConfirmationStatus, setEmailConfirmationStatus] = useState<
  "confirmed" | "unconfirmed" | null
>(null);
const [isLoading, setIsLoading] = useState(false);
const [rateLimitInfo, setRateLimitInfo] = useState<{
  resendVerification: number | null;
  resetPassword: number | null;
}>({ resendVerification: null, resetPassword: null });
```

#### **Rate Limiting Implementation**

```typescript
// Check rate limit using session storage
const checkRateLimit = (
  action: "resendVerification" | "resetPassword"
): boolean => {
  const now = Date.now();
  const lastRequest = sessionStorage.getItem(`last_${action}_request`);

  if (lastRequest) {
    const timeDiff = now - parseInt(lastRequest);
    if (timeDiff < 60000) {
      // 60 seconds
      return false;
    }
  }

  sessionStorage.setItem(`last_${action}_request`, now.toString());
  return true;
};
```

#### **Enhanced Login Flow**

1. **Form Submission**: User submits login credentials
2. **Email Confirmation Check**: Verify if email is confirmed
3. **Conditional Response**:
   - If unconfirmed → Show resend verification option
   - If confirmed → Proceed with normal login
4. **Error Handling**: Display appropriate error messages

#### **Forgot Password Integration**

- Modal overlay with email input
- Rate limiting check before API call
- Success/error feedback
- Automatic modal close on success

#### **Email Confirmation Handling**

- Detect unconfirmed email status
- Show resend verification modal
- Rate limiting for resend requests
- Success confirmation with redirect

### 2. **Dashboard Update Password** (`app/dashboard/update-password/page.tsx`)

#### **Page Structure**

```typescript
interface UpdatePasswordProps {
  isForgotPasswordFlow?: boolean;
  userEmail?: string;
}

export default function UpdatePasswordPage() {
  const [isForgotPasswordFlow, setIsForgotPasswordFlow] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
}
```

#### **Two Flow Scenarios**

**Scenario A: Normal Password Change**

- Current password input (required)
- New password input
- Confirm password input
- Submit button

**Scenario B: Forgot Password Flow**

- User arrives via email link (auto-logged in)
- Only new password and confirm password inputs
- No current password required
- Submit button

#### **Form Validation**

```typescript
const passwordSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        "Password must contain uppercase, lowercase, and number"
      ),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });
```

### 3. **API Routes**

#### **Resend Verification** (`app/api/auth/resend-verification/route.ts`)

```typescript
export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    // Server-side rate limiting check
    const rateLimitKey = `resend_verification_${email}`;
    const lastRequest = await redis.get(rateLimitKey);

    if (lastRequest && Date.now() - parseInt(lastRequest) < 60000) {
      return NextResponse.json(
        {
          success: false,
          message:
            "Please wait 60 seconds before requesting another verification email",
        },
        { status: 429 }
      );
    }

    const supabase = supabaseServer();
    const { data, error } = await supabase.auth.resend({
      type: "signup",
      email: email,
    });

    if (error) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: 400 }
      );
    }

    // Set rate limit
    await redis.setex(rateLimitKey, 60, Date.now().toString());

    return NextResponse.json({
      success: true,
      message: "Verification email has been sent",
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, message: "Failed to send verification email" },
      { status: 500 }
    );
  }
}
```

#### **Reset Password** (`app/api/auth/reset-password/route.ts`)

```typescript
export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    // Server-side rate limiting check
    const rateLimitKey = `reset_password_${email}`;
    const lastRequest = await redis.get(rateLimitKey);

    if (lastRequest && Date.now() - parseInt(lastRequest) < 60000) {
      return NextResponse.json(
        {
          success: false,
          message:
            "Please wait 60 seconds before requesting another password reset",
        },
        { status: 429 }
      );
    }

    const supabase = supabaseServer();
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/dashboard/update-password`,
    });

    if (error) {
      return NextResponse.json(
        { success: false, message: error.message },
        { status: 400 }
      );
    }

    // Set rate limit
    await redis.setex(rateLimitKey, 60, Date.now().toString());

    return NextResponse.json({
      success: true,
      message: "Password reset email has been sent",
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, message: "Failed to send password reset email" },
      { status: 500 }
    );
  }
}
```

### 4. **Rate Limiting Implementation**

#### **Client-Side (Session Storage)**

```typescript
// Utility functions for rate limiting
export const RateLimitUtils = {
  checkRateLimit: (action: string): boolean => {
    const now = Date.now();
    const lastRequest = sessionStorage.getItem(`last_${action}_request`);

    if (lastRequest) {
      const timeDiff = now - parseInt(lastRequest);
      if (timeDiff < 60000) {
        return false;
      }
    }

    sessionStorage.setItem(`last_${action}_request`, now.toString());
    return true;
  },

  getRemainingTime: (action: string): number => {
    const lastRequest = sessionStorage.getItem(`last_${action}_request`);
    if (!lastRequest) return 0;

    const timeDiff = Date.now() - parseInt(lastRequest);
    return Math.max(0, 60000 - timeDiff);
  },

  formatRemainingTime: (milliseconds: number): string => {
    const seconds = Math.ceil(milliseconds / 1000);
    return `${seconds} seconds`;
  },
};
```

#### **Server-Side (Redis/Database)**

- Store rate limit timestamps in Redis or database
- Key format: `{action}_{email}_{ip}`
- 60-second expiration
- Return 429 status code when rate limited

### 5. **UI Components**

#### **Forgot Password Modal**

```typescript
interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ForgotPasswordModal = ({
  isOpen,
  onClose,
  onSuccess,
}: ForgotPasswordModalProps) => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [remainingTime, setRemainingTime] = useState(0);

  // Rate limiting logic
  const canSendRequest = RateLimitUtils.checkRateLimit("resetPassword");

  // Countdown timer
  useEffect(() => {
    if (!canSendRequest) {
      const timer = setInterval(() => {
        const remaining = RateLimitUtils.getRemainingTime("resetPassword");
        setRemainingTime(remaining);
        if (remaining === 0) {
          clearInterval(timer);
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [canSendRequest]);

  // Component JSX...
};
```

#### **Email Confirmation Modal**

```typescript
interface EmailConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
}

const EmailConfirmationModal = ({
  isOpen,
  onClose,
  userEmail,
}: EmailConfirmationModalProps) => {
  const [email, setEmail] = useState(userEmail);
  const [isLoading, setIsLoading] = useState(false);
  const [remainingTime, setRemainingTime] = useState(0);

  // Similar rate limiting logic as forgot password modal
  // Component JSX...
};
```

### 6. **Authentication Flow Logic**

#### **Login Process**

```typescript
const handleLogin = async (values: LoginFormValues) => {
  setIsLoading(true);

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });

    const data = await response.json();

    if (!response.ok) {
      // Check if email is not confirmed
      if (data.error === "email_not_confirmed") {
        setEmailConfirmationStatus("unconfirmed");
        setShowResendModal(true);
        return;
      }
      throw new Error(data.message || "Login failed");
    }

    // Successful login
    toast({ title: "Login Successful!", description: `Welcome back!` });
    router.push("/");
  } catch (error) {
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "An error occurred",
      variant: "destructive",
    });
  } finally {
    setIsLoading(false);
  }
};
```

#### **Forgot Password Process**

```typescript
const handleForgotPassword = async (email: string) => {
  if (!RateLimitUtils.checkRateLimit("resetPassword")) {
    toast({
      title: "Rate Limited",
      description:
        "Please wait 60 seconds before requesting another password reset",
      variant: "destructive",
    });
    return;
  }

  setIsLoading(true);

  try {
    const response = await fetch("/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to send reset email");
    }

    toast({
      title: "Reset Email Sent",
      description: "Please check your email for password reset instructions",
    });

    onSuccess();
  } catch (error) {
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "An error occurred",
      variant: "destructive",
    });
  } finally {
    setIsLoading(false);
  }
};
```

### 7. **Middleware Updates**

#### **Route Protection** (`middleware.ts`)

```typescript
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow access to update-password for authenticated users
  if (pathname === "/dashboard/update-password") {
    const supabase = createMiddlewareClient({ req: request, res: response });
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.redirect(new URL("/auth", request.url));
    }

    return NextResponse.next();
  }

  // Existing middleware logic...
}
```

### 8. **Error Handling**

#### **Client-Side Error States**

```typescript
interface ErrorState {
  type: "network" | "validation" | "rate_limit" | "server";
  message: string;
  retryable: boolean;
}

const ErrorHandler = {
  handleLoginError: (error: any): ErrorState => {
    if (error.message.includes("email_not_confirmed")) {
      return {
        type: "validation",
        message: "Please confirm your email before logging in",
        retryable: false,
      };
    }

    if (error.message.includes("rate limit")) {
      return {
        type: "rate_limit",
        message: "Too many requests. Please wait before trying again.",
        retryable: true,
      };
    }

    return {
      type: "server",
      message: error.message || "An unexpected error occurred",
      retryable: true,
    };
  },
};
```

#### **Server-Side Error Responses**

```typescript
const ErrorResponses = {
  RATE_LIMITED: {
    success: false,
    message: "Please wait 60 seconds before making another request",
    code: "RATE_LIMITED",
  },

  EMAIL_NOT_FOUND: {
    success: false,
    message: "No account found with this email address",
    code: "EMAIL_NOT_FOUND",
  },

  INVALID_EMAIL: {
    success: false,
    message: "Please enter a valid email address",
    code: "INVALID_EMAIL",
  },
};
```

## 🎨 UI/UX Considerations

### 1. **Design Consistency**

- Match existing auth page styling
- Use consistent color scheme and typography
- Maintain responsive design patterns
- Follow accessibility guidelines

### 2. **Loading States**

- Spinner animations during API calls
- Disabled buttons during processing
- Progress indicators for multi-step flows
- Skeleton loading for dynamic content

### 3. **Success/Error Feedback**

- Toast notifications for actions
- Inline error messages for form validation
- Success confirmations with clear next steps
- Error recovery suggestions

### 4. **Rate Limiting UX**

- Countdown timers showing remaining wait time
- Disabled buttons with explanatory text
- Visual indicators for rate limit status
- Clear messaging about when user can retry

## 🔒 Security Considerations

### 1. **Rate Limiting Security**

- Server-side validation (client-side is UX only)
- IP-based rate limiting for additional security
- Exponential backoff for repeated violations
- Logging of rate limit violations

### 2. **Email Security**

- Validate email format server-side
- Prevent email enumeration attacks
- Secure redirect URL validation
- CSRF protection for all forms

### 3. **Password Security**

- Strong password requirements
- Password strength indicator
- Secure password transmission
- Session invalidation after password change

### 4. **Session Management**

- Secure session handling
- Proper logout functionality
- Session timeout handling
- Cross-site request forgery protection

## 📱 User Experience Flows

### **Flow 1: Successful Login**

1. User enters email and password
2. System validates credentials
3. User is redirected to dashboard
4. Success toast notification shown

### **Flow 2: Unconfirmed Email Login**

1. User enters email and password
2. System detects unconfirmed email
3. Shows "Email not confirmed" message
4. Displays resend verification option
5. User can resend verification email
6. User receives email and confirms account
7. User can now login successfully

### **Flow 3: Forgot Password**

1. User clicks "Forgot password?" on login form
2. Modal opens with email input
3. User enters email and clicks "Send Reset Email"
4. System checks rate limit (60 seconds)
5. If rate limited, shows countdown timer
6. If allowed, sends reset email
7. User receives email with reset link
8. User clicks link and is auto-logged in
9. User is redirected to update password page
10. User enters new password and confirms
11. Password is updated successfully
12. User is redirected to dashboard

### **Flow 4: Normal Password Change**

1. User goes to profile page
2. Clicks "Reset Password" button
3. Redirected to update password page
4. User enters current password
5. User enters new password and confirmation
6. System validates current password
7. Password is updated successfully
8. User is logged out and redirected to login

### **Flow 5: Rate Limited Request**

1. User attempts to send verification/reset email
2. System checks if 60 seconds have passed
3. If not, shows countdown timer
4. Button is disabled with explanatory text
5. Timer counts down to zero
6. Button becomes enabled again
7. User can retry the request

## 🚨 Edge Cases and User Flows

### **Edge Case 1: Network Connectivity Issues**

**Scenario**: User loses internet connection during form submission
**Flow**:

1. User submits form
2. Network request fails
3. Show error message with retry option
4. User regains connection
5. User can retry the action
6. System processes request successfully

**Handling**:

- Implement retry logic with exponential backoff
- Show clear error messages
- Provide retry buttons
- Maintain form state during network issues

### **Edge Case 2: Email Delivery Failures**

**Scenario**: User requests password reset but email doesn't arrive
**Flow**:

1. User requests password reset
2. System sends email successfully
3. Email doesn't arrive (spam, server issues, etc.)
4. User waits and doesn't receive email
5. User tries again after 60 seconds
6. System sends another email
7. User receives email and completes reset

**Handling**:

- Provide clear instructions about checking spam folder
- Allow multiple reset attempts with rate limiting
- Show success message even if email fails
- Provide alternative contact methods

### **Edge Case 3: Invalid Email Format**

**Scenario**: User enters invalid email address
**Flow**:

1. User enters malformed email (e.g., "user@")
2. Client-side validation catches error
3. Show inline error message
4. User corrects email format
5. Form submission proceeds normally

**Handling**:

- Real-time email validation
- Clear error messages
- Prevent form submission with invalid data
- Provide examples of correct email format

### **Edge Case 4: Account Doesn't Exist**

**Scenario**: User tries to reset password for non-existent account
**Flow**:

1. User enters email for non-existent account
2. System processes request
3. Returns success message (security measure)
4. No email is sent
5. User waits for email that never arrives
6. User can try again after 60 seconds

**Handling**:

- Always return success message for security
- Provide generic instructions about checking email
- Don't reveal whether account exists
- Allow multiple attempts with rate limiting

### **Edge Case 5: Session Expiration During Password Update**

**Scenario**: User's session expires while updating password
**Flow**:

1. User clicks password reset link
2. User is auto-logged in
3. User takes time to enter new password
4. Session expires during this time
5. User submits form
6. System detects expired session
7. User is redirected to login page
8. User must request new reset email

**Handling**:

- Extend session timeout for password reset flow
- Detect expired sessions before form submission
- Show warning messages about session expiration
- Provide option to request new reset email

### **Edge Case 6: Multiple Browser Tabs**

**Scenario**: User has multiple tabs open with auth forms
**Flow**:

1. User opens forgot password modal in tab 1
2. User opens forgot password modal in tab 2
3. User sends request from tab 1
4. User tries to send request from tab 2
5. System shows rate limit message
6. User must wait 60 seconds

**Handling**:

- Use session storage for rate limiting (shared across tabs)
- Show consistent rate limit status across tabs
- Provide clear messaging about rate limits
- Allow user to close extra tabs

### **Edge Case 7: Email Confirmation Link Expiration**

**Scenario**: User receives confirmation email but link expires
**Flow**:

1. User receives confirmation email
2. User doesn't click link immediately
3. Link expires after 24 hours
4. User clicks expired link
5. System shows "Link expired" message
6. User can request new confirmation email
7. User receives new email with fresh link

**Handling**:

- Detect expired confirmation links
- Show clear expiration messages
- Provide option to request new confirmation
- Maintain rate limiting for new requests

### **Edge Case 8: Password Reset Link Already Used**

**Scenario**: User clicks password reset link multiple times
**Flow**:

1. User receives password reset email
2. User clicks link and is redirected to update page
3. User bookmarks the page
4. User clicks link again later
5. System detects already used link
6. User is redirected to login page
7. User must request new reset email

**Handling**:

- Track used reset links
- Show appropriate error messages
- Redirect to login page
- Provide option to request new reset

### **Edge Case 9: User Changes Email During Reset Process**

**Scenario**: User starts password reset but changes email in another tab
**Flow**:

1. User requests password reset for email A
2. User changes email to email B in profile
3. User receives reset email for email A
4. User clicks link but account now uses email B
5. System detects email mismatch
6. User is redirected to login page
7. User must request new reset for email B

**Handling**:

- Validate email consistency during reset
- Show clear error messages
- Provide guidance on next steps
- Allow new reset request for current email

### **Edge Case 10: Rate Limit Bypass Attempts**

**Scenario**: User tries to bypass rate limiting by clearing session storage
**Flow**:

1. User hits rate limit for reset request
2. User clears browser session storage
3. User tries to send another request
4. Server-side rate limiting still applies
5. User receives rate limit error
6. User must wait for server-side rate limit to expire

**Handling**:

- Implement server-side rate limiting as primary protection
- Client-side rate limiting is UX only
- Log rate limit bypass attempts
- Provide clear messaging about server-side limits

### **Edge Case 11: Concurrent Password Updates**

**Scenario**: User tries to update password from multiple devices
**Flow**:

1. User starts password update on device A
2. User starts password update on device B
3. User completes update on device A
4. User tries to complete update on device B
5. System detects password already changed
6. User on device B is logged out
7. User must login with new password

**Handling**:

- Invalidate all sessions after password change
- Show clear messages about password changes
- Force re-authentication on all devices
- Provide option to login with new password

### **Edge Case 12: Email Provider Blocking**

**Scenario**: User's email provider blocks our emails
**Flow**:

1. User requests password reset
2. System sends email successfully
3. Email provider blocks our domain
4. User never receives email
5. User tries again after 60 seconds
6. Same issue occurs
7. User contacts support

**Handling**:

- Monitor email delivery rates
- Provide alternative contact methods
- Show instructions about email provider issues
- Offer manual account recovery options

### **Edge Case 13: Browser Autofill Issues**

**Scenario**: Browser autofill interferes with form validation
**Flow**:

1. User opens forgot password modal
2. Browser autofills email field
3. User clicks send button
4. Form validation doesn't trigger properly
5. Invalid email is submitted
6. System returns validation error
7. User must manually correct email

**Handling**:

- Implement proper autofill event handling
- Validate form on autofill events
- Show clear validation messages
- Provide manual correction options

### **Edge Case 14: Mobile Device Orientation Changes**

**Scenario**: User rotates device during form submission
**Flow**:

1. User fills out form in portrait mode
2. User rotates device to landscape
3. Form layout changes
4. User continues filling form
5. User submits form
6. System processes request normally

**Handling**:

- Ensure responsive design works in all orientations
- Maintain form state during orientation changes
- Test on various mobile devices
- Provide consistent user experience

### **Edge Case 15: Slow Network Conditions**

**Scenario**: User has slow internet connection
**Flow**:

1. User submits form
2. Network request takes long time
3. User thinks form didn't submit
4. User clicks submit button again
5. System processes duplicate request
6. User receives duplicate emails

**Handling**:

- Show loading indicators during requests
- Disable submit button during processing
- Implement request deduplication
- Provide clear feedback about request status

## 🎯 Success Metrics

### **User Experience Metrics**

- Login success rate: >95%
- Password reset completion rate: >80%
- Email confirmation rate: >70%
- User satisfaction score: >4.5/5

### **Technical Metrics**

- Page load time: <2 seconds
- API response time: <500ms
- Error rate: <1%
- Rate limit hit rate: <5%

### **Security Metrics**

- Failed login attempts: <10 per IP per hour
- Rate limit violations: <2% of requests
- Email delivery rate: >98%
- Session security: 100% secure

## 📅 Implementation Timeline

### **Phase 1: Core Infrastructure (Week 1)**

- Remove unnecessary auth pages
- Create API routes for resend verification and reset password
- Implement basic rate limiting

### **Phase 2: UI Components (Week 2)**

- Create forgot password modal
- Create email confirmation modal
- Implement update password page

### **Phase 3: Integration (Week 3)**

- Integrate all components
- Implement error handling
- Add comprehensive testing

### **Phase 4: Polish & Testing (Week 4)**

- UI/UX refinements
- Edge case handling
- Performance optimization
- Security audit

## 🔍 Testing Strategy

### **Unit Tests**

- Form validation logic
- Rate limiting utilities
- Error handling functions
- API route handlers

### **Integration Tests**

- Complete authentication flows
- Email sending functionality
- Rate limiting behavior
- Error recovery scenarios

### **End-to-End Tests**

- User journey testing
- Cross-browser compatibility
- Mobile device testing
- Performance testing

### **Security Tests**

- Rate limiting bypass attempts
- Email enumeration attacks
- Session hijacking prevention
- CSRF protection validation

## 📚 Documentation Requirements

### **API Documentation**

- Endpoint specifications
- Request/response formats
- Error codes and messages
- Rate limiting details

### **User Documentation**

- Password reset process
- Email confirmation steps
- Troubleshooting guide
- FAQ section

### **Developer Documentation**

- Code architecture overview
- Component usage examples
- Testing guidelines
- Deployment instructions

---

This comprehensive plan covers all aspects of the authentication system overhaul, including detailed edge cases and user flows. The implementation will provide a robust, secure, and user-friendly authentication experience while maintaining the existing design consistency.
