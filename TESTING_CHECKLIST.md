# Pre-Deployment Testing Checklist

## ✓ Changes Summary

### 1. Homepage Font Size Reduction
- [x] Reduced `.survey-header p` font size from `0.95rem` → `0.85rem` in `styles.css`
- **Visual Impact**: The survey description text ("Customer experience feedback...") is now smaller

### 2. Admin User Management
- [x] Created management command: `python manage.py setup_admin`
- [x] Can create or update admin user with custom credentials
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`

### 3. Password Reset Feature  
- [x] Added `/dashboard/change-password/` route (requires login)
- [x] Added `/dashboard/change-password/done/` success page
- [x] Created styled templates with form validation
- **How to Access**: Visit `/dashboard/change-password/` after logging in

---

## Testing Checklist

### Step 1: Verify File Changes
- [ ] Check `styles.css` has `font-size: 0.85rem;` in `.survey-header p` (line ~67)
- [ ] Check `dashboard/views.py` imports `PasswordChangeForm` and `messages`
- [ ] Check `dashboard/urls.py` includes password change routes
- [ ] Verify management command exists: `dashboard/management/commands/setup_admin.py`
- [ ] Verify templates exist:
  - [ ] `dashboard/templates/dashboard/password_change.html`
  - [ ] `dashboard/templates/dashboard/password_change_done.html`

### Step 2: Test Locally (If possible)

**2a. Create Admin User**:
```bash
# Open terminal in /home/tuwa1simon/Hostinger
python manage.py setup_admin
```
Expected output:
```
Admin user 'admin' created successfully!
   Username: admin
   Email: admin@example.com
   Password: admin123
```

**2b. Start Development Server**:
```bash
python manage.py runserver
```

**2c. Test Homepage Font Size**:
1. Open browser: `http://localhost:8000/`
2. Look at subtitle text: "Customer experience feedback for public and private-sector service providers."
3. Right-click → Inspect
4. Check computed font-size is `13.6px` or `0.85rem`
5. Confirm it looks smaller than before

**2d. Test Admin Login**:
1. Visit: `http://localhost:8000/dashboard/login/`
2. Try credentials:
   - Username: `admin`
   - Password: `admin123`
3. Should successfully login and redirect to dashboard

**2e. Test Password Reset**:
1. Once logged in, visit: `http://localhost:8000/dashboard/change-password/`
2. Enter current password: `admin123`
3. Enter new password: `testpass123`
4. Confirm new password: `testpass123`
5. Click "Update Password"
6. Should see success page
7. Logout and try new password to verify it works

### Step 3: Code Review
- [ ] No syntax errors in Python files
- [ ] HTML templates are properly formatted
- [ ] Import statements are correct
- [ ] No missing dependencies

---

## Files Changed/Created

### Modified:
- `styles.css` - Font size change
- `dashboard/views.py` - Added password change views
- `dashboard/urls.py` - Added password change routes

### Created:
- `dashboard/management/__init__.py`
- `dashboard/management/commands/__init__.py`
- `dashboard/management/commands/setup_admin.py`
- `dashboard/templates/dashboard/password_change.html`
- `dashboard/templates/dashboard/password_change_done.html`
- `SETUP_AND_CHANGES.md` - Setup documentation

---

## Before Pushing to GitHub

1. [ ] All local tests pass
2. [ ] Admin user created and login works
3. [ ] Password change feature works
4. [ ] Homepage looks good with smaller font
5. [ ] No Python errors or warnings
6. [ ] All files are properly formatted

---

## Deployment Instructions

Once everything is tested and pushed to GitHub:

1. Pull changes on hosting server
2. Run: `python manage.py setup_admin --password=yoursecurepassword`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Restart web server
5. Test login at: `https://yourdomain.com/dashboard/login/`

---

## Need Help?

If something doesn't work:

1. **Admin login fails**: Run `python manage.py setup_admin` again
2. **Templates not found**: Verify file paths and template directories
3. **Password reset doesn't work**: Check Django messages framework is enabled in settings
4. **Font size not changing**: Clear browser cache (Ctrl+Shift+Delete)

