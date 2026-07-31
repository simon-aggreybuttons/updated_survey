# GCSI Survey - Setup & Changes Summary

## All Changes Completed ✓

### 1. Homepage Copywrite Font Size Reduction ✓
**Files Modified**: 
- `styles.css` - `.survey-header p` from `0.95rem` → `0.85rem`
- `static/css/style.css` - `.home-footer__copyright` from `0.9rem` → `0.7rem`
- Description text under survey title is now smaller
- Copyright text at footer is now significantly smaller

### 2. Admin User Setup & Credentials ✓
**Files Created**: 
- `dashboard/management/commands/setup_admin.py`
- `dashboard/management/__init__.py`
- `dashboard/management/commands/__init__.py`

**How to use**:
```bash
# Create admin user with default credentials (admin/admin123)
python manage.py setup_admin

# Create admin user with custom credentials
python manage.py setup_admin --username=admin --email=admin@example.com --password=admin123

# Update existing admin password
python manage.py setup_admin --password=newpassword123
```

### 3. Password Reset Feature ✓
**Files Created**: 
- `dashboard/management/commands/setup_admin.py`
- `dashboard/templates/dashboard/password_change.html` - Clean, professional form
- `dashboard/templates/dashboard/password_change_done.html` - Success page

**Files Modified**:
- `dashboard/views.py` - Added `PasswordChangeView` and `PasswordChangeDoneView`
- `dashboard/urls.py` - Added password change routes
- `dashboard/templates/dashboard/dashboard.html` - Added "Change Password" button

**How to use**:
1. Click the **"Change Password"** button on your dashboard (next to Export buttons)
2. Or visit: `/dashboard/change-password/`
3. Enter current password: `admin123`
4. Enter new password (min 8 chars, can't be all numbers)
5. Confirm password
6. Click "Update Password"
7. See success message, then return to dashboard
8. Next login: use your new password

---

## What's New vs Before

| Feature | Before | After |
|---------|--------|-------|
| Homepage text | Large (0.95rem) | Smaller, refined (0.85rem) |
| Copyright | Large, hard to read (0.9rem) | Very small, minimal (0.7rem) |
| Password reset | No UI, must use setup command | Button on dashboard + clean form |
| Password page | Django admin styled | Professional, matches site design |

---

## Testing Instructions

### Local Testing (Before Deployment)

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install Dependencies** (if needed):
   ```bash
   pip install django djangorestframework
   ```

3. **Run Migrations** (if any):
   ```bash
   python manage.py migrate
   ```

4. **Setup Admin User**:
   ```bash
   python manage.py setup_admin
   ```

5. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Test in Browser**:
   - **Homepage**: Visit `http://localhost:8000/` 
     - Check that the description text is smaller (0.85rem)
     - Check copyright text at bottom is very small (0.7rem)
   
   - **Admin Login**: Visit `http://localhost:8000/dashboard/login/`
     - Login with: `admin` / `admin123`
   
   - **Dashboard**: Visit `http://localhost:8000/dashboard/`
     - Click the "Change Password" button in the top right next to Export buttons
   
   - **Password Change**: On password change page
     - Enter current password: `admin123`
     - Enter new password: `TestPass2024`
     - Confirm: `TestPass2024`
     - Click "Update Password"
     - See success message with checkmark ✓
     - Click "Back to Dashboard"
     - Logout and login with new password to verify

---

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "feat: reduce homepage font size, fix admin login, add password reset"
git push origin main
```

### 2. On Your Hosting Server
```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Create/update admin user with desired credentials
python manage.py setup_admin --username=admin --email=your-email@example.com --password=your-new-password

# Collect static files
python manage.py collectstatic --noinput

# Restart web server
sudo systemctl restart gunicorn  # or your web server
```

---

## Admin Credentials

After deployment, use the following to login:
- **URL**: `https://yourdomain.com/dashboard/login/`
- **Username**: `admin`
- **Password**: `admin123` (or your custom password)

### To Change Password After First Login:
1. Go to: `https://yourdomain.com/dashboard/change-password/`
2. Enter your current password
3. Enter and confirm your new password
4. Click "Update Password"

---

## Files Summary

### Modified Files:
- `styles.css` - Reduced font size for copywrite text
- `dashboard/views.py` - Added password change views
- `dashboard/urls.py` - Added password change routes

### New Files:
- `dashboard/management/commands/setup_admin.py` - Setup admin management command
- `dashboard/management/__init__.py` - Management package init
- `dashboard/management/commands/__init__.py` - Commands package init
- `dashboard/templates/dashboard/password_change.html` - Password change form template
- `dashboard/templates/dashboard/password_change_done.html` - Password change success template

---

## Troubleshooting

### Admin Login Not Working
1. Verify the admin user exists:
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(username='admin')
   ```

2. Reset the admin password:
   ```bash
   python manage.py setup_admin --password=admin123
   ```

### Password Change Page Shows Blank
- Ensure you're logged in first
- Check that Django messages framework is configured
- Verify all template files exist

### Font Size Not Changing
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Verify `styles.css` is being loaded correctly
- Check browser DevTools (F12) to confirm font-size is 0.85rem

---

## Next Steps

1. Test all features locally
2. Verify admin login works with credentials: `admin` / `admin123`
3. Confirm password reset works
4. Push to GitHub
5. Deploy to your hosting server
6. Test again on the live site
7. Change admin password to something secure

