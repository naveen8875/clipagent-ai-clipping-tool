# Build Errors Phase 2 - Focused Fix Plan

## Current Status

- **Total Errors Remaining**: ~80+ errors
- **Phase 1 Progress**: ✅ Fixed unused imports, ✅ Fixed unused parameters
- **Current Focus**: Systematic cleanup of remaining issues

## New Categorized Approach

### **Category 1: Unused Variables/Imports (25 errors)**

**Priority: HIGH** - Quick wins, easy fixes

#### 1.1 Unused Function Parameters (12 errors)

- `_request` parameters in API routes (already prefixed, need to remove)
- `data` variables assigned but never used
- `email`, `setEmail` variables

#### 1.2 Unused Imports (8 errors)

- `Button`, `Input`, `Label` components
- `MoreHorizontal`, `Plus`, `Badge` icons
- `Key`, `Activity`, `HardDrive` icons
- `LogOut`, `Settings` icons

#### 1.3 Unused Variables (5 errors)

- `isUpgrade`, `isDowngrade` variables
- `autoOpened`, `formatDateTime` variables
- `selectedClip`, `setSelectedClip` state
- `videoId`, `isLoading` variables

### **Category 2: TypeScript `any` Types (30 errors)**

**Priority: HIGH** - Type safety improvements

#### 2.1 API Route `any` Types (8 errors)

- `app/api/billing/change-plan/route.ts` - 4 errors
- `app/api/billing/create-checkout/route.ts` - 3 errors
- `app/api/webhooks/stripe/route.ts` - 6 errors

#### 2.2 Component `any` Types (12 errors)

- `components/billing/` files - 6 errors
- `components/credits/` files - 4 errors
- `components/dashboard/` files - 2 errors

#### 2.3 Library `any` Types (10 errors)

- `lib/api.ts` - 1 error
- `lib/billing-error-handler.ts` - 2 errors
- `lib/error-handler.ts` - 4 errors
- `lib/pricing-*.ts` files - 3 errors

### **Category 3: React/JSX Issues (15 errors)**

**Priority: MEDIUM** - UI improvements

#### 3.1 Unescaped Entities (8 errors)

- Apostrophes in text content
- Quotes in JSX attributes

#### 3.2 React Hooks Issues (4 errors)

- Missing dependencies in `useEffect`
- Conditional hook calls
- Hook dependency warnings

#### 3.3 Image Optimization (3 errors)

- `<img>` tags should use Next.js `<Image>`

### **Category 4: ESLint Rule Violations (10 errors)**

**Priority: LOW** - Code quality

#### 4.1 Empty Interfaces (2 errors)

- `components/ui/command.tsx`
- `components/ui/textarea.tsx`

#### 4.2 Unsafe Declarations (2 errors)

- `lib/error-handler.ts`

#### 4.3 Unused Parameters (6 errors)

- `_props` parameters in UI components

## **New Execution Strategy**

### **Phase A: Quick Cleanup (15 minutes)**

1. Remove all unused imports
2. Remove all unused variables
3. Fix unescaped entities

### **Phase B: Type Safety (30 minutes)**

1. Fix API route `any` types
2. Fix component `any` types
3. Fix library `any` types

### **Phase C: React Improvements (15 minutes)**

1. Fix React hooks issues
2. Fix image optimization
3. Fix conditional hooks

### **Phase D: Final Cleanup (10 minutes)**

1. Fix empty interfaces
2. Fix unsafe declarations
3. Final verification

## **Expected Results**

- **Total Time**: ~70 minutes
- **Error Reduction**: 80+ → 0 errors
- **Code Quality**: Significantly improved
- **Type Safety**: Much better

## **Key Principles**

1. **Batch similar fixes** - Fix all unused imports at once
2. **Prioritize by impact** - Fix high-impact issues first
3. **Test frequently** - Check build after each phase
4. **Maintain functionality** - Don't break existing features

## **Success Metrics**

- ✅ Zero build errors
- ✅ Zero TypeScript `any` types
- ✅ Clean, maintainable code
- ✅ Better developer experience
