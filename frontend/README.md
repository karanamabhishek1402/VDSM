# VDSM Frontend - Authentication System

This document describes the authentication system implemented in the VDSM frontend application.

## Features

### Authentication Pages

1. **Login Page** (`/login`)
   - Email and password fields with validation
   - Password visibility toggle
   - Remember me option
   - Error message display
   - Loading states during authentication
   - Redirects to dashboard on successful login
   - Link to registration page

2. **Register Page** (`/register`)
   - Full name, email, username, password fields
   - Password confirmation field
   - Password strength indicator
   - Form validation with real-time feedback
   - Terms and conditions checkbox
   - Error message display
   - Loading states during registration
   - Redirects to login on successful registration

### Components

- **AuthContext**: Global authentication state management
- **ProtectedRoute**: Route protection wrapper
- **Navbar**: Responsive navigation with auth state
- **ErrorBoundary**: Error handling component
- **Loading**: Reusable loading spinner

### API Integration

All authentication endpoints are connected to the backend API:
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user profile

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **React Router** - Navigation
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Authentication Flow

### Login
1. User enters email and password
2. Form validation checks for valid email and password
3. API call to `/auth/login` endpoint
4. On success, JWT token and user data are stored in localStorage
5. User is redirected to dashboard

### Registration
1. User fills out registration form
2. Real-time validation checks all fields
3. Password must:
   - Be at least 8 characters
   - Contain uppercase and lowercase letters
   - Contain at least one number
   - Contain at least one special character
4. Username must be 3-20 alphanumeric characters
5. API call to `/auth/register` endpoint
6. On success, user is redirected to login page

### Logout
1. Click logout button in navbar
2. Confirmation dialog appears
3. Token and user data are cleared from localStorage
4. User is redirected to login page

### Session Management
- Token is stored in localStorage as `vdsm_token`
- User data is stored as `vdsm_user`
- On app load, token and user data are loaded from localStorage
- Session is verified via `/auth/me` endpoint
- Token is automatically included in API request headers
- 401 responses automatically redirect to login

## Form Validation

### Login Form
- Email: Required, valid email format
- Password: Required

### Register Form
- Full Name: 2-100 characters
- Email: Required, valid email format
- Username: 3-20 characters, alphanumeric only
- Password: 8+ characters, mixed case, number, special character
- Confirm Password: Must match password
- Terms: Must be accepted

## Error Handling

- Field-specific validation errors
- Server-side errors from API
- Network errors
- Token expiration handling
- User-friendly error messages
- Auto-clear errors on retry

## Security Features

- Password visibility toggle
- HTTPS ready (use in production)
- Token-based authentication
- Automatic token inclusion in headers
- Token expiration handling
- Protected routes
- Form validation on client and server

## Responsive Design

- Mobile-first approach
- Responsive navbar with hamburger menu
- Full-width forms on mobile
- Touch-friendly buttons
- Proper spacing and padding

## Development

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## Testing Scenarios

1. ✅ Navigate to /login → Login page loads
2. ✅ Submit login with invalid email → Error message shows
3. ✅ Submit login with missing password → Error message shows
4. ✅ Submit login with invalid credentials → Error message shows
5. ✅ Submit login with valid credentials → Token stored, redirect to dashboard
6. ✅ Navigate to /register → Register page loads
7. ✅ Submit with mismatched passwords → Error message shows
8. ✅ Submit with username too short → Validation error shows
9. ✅ Submit with duplicate email → Server error displays
10. ✅ Register successfully → Redirect to login
11. ✅ Click logout → Token cleared, redirect to login
12. ✅ Refresh page while logged in → Stay on dashboard
13. ✅ Manually clear localStorage → Redirect to login
14. ✅ Access protected route without login → Redirect to login
15. ✅ Show/hide password toggles work

## Future Enhancements

- Forgot password functionality
- Email verification
- OAuth integration (Google, GitHub)
- Two-factor authentication
- Password reset via email
- Remember me with persistent tokens
- Session timeout warning
- Social login buttons
- Biometric authentication (mobile)

## Troubleshooting

### Token not persisting
- Check browser localStorage
- Ensure browser allows localStorage
- Check for browser extensions blocking localStorage

### CORS errors
- Ensure backend CORS is configured
- Verify API_URL in .env file
- Check network requests in browser DevTools

### Form validation not working
- Check browser console for errors
- Verify Zod schema is correct
- Ensure react-hook-form is properly configured

### Not redirecting after login
- Check if token is stored
- Verify AuthContext is working
- Check browser console for errors
