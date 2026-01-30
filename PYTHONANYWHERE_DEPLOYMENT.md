# PythonAnywhere Deployment Guide

## Step 1: Upload Your Code

### Option A: Using Git (Recommended)
1. Go to PythonAnywhere Dashboard
2. Open a **Bash console**
3. Clone your repository:
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### Option B: Upload Files Manually
1. Use the **Files** tab in PythonAnywhere
2. Upload your entire project folder

## Step 2: Set Up Virtual Environment

In the Bash console:
```bash
cd ~/your-project-folder
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Configure Web App

1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration** (NOT Django wizard)
4. Select **Python 3.9** (or your version)

## Step 4: Configure WSGI File

1. In the **Web** tab, find the **WSGI configuration file** link
2. Click on it to edit
3. **Delete everything** in the file
4. Replace with this:

```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/your-project-folder'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell Django where your settings are
os.environ['DJANGO_SETTINGS_MODULE'] = 'payslip_project.settings'

# Activate your virtual environment
activate_this = '/home/yourusername/your-project-folder/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important:** Replace:
- `yourusername` with your PythonAnywhere username
- `your-project-folder` with your actual folder name (e.g., `Payslip`)

## Step 5: Configure Virtualenv Path

1. Still in the **Web** tab
2. Find the **Virtualenv** section
3. Enter the path to your virtualenv:
```
/home/yourusername/your-project-folder/venv
```

## Step 6: Configure Static Files

In the **Web** tab, scroll to **Static files** section:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/your-project-folder/staticfiles` |

## Step 7: Update Settings

Edit your `payslip_project/settings.py`:

```python
# Replace yourusername with your actual PythonAnywhere username
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# For production, set DEBUG = False (but keep it True while testing)
DEBUG = True  # Change to False after testing

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/your-project-folder/staticfiles'
STATICFILES_DIRS = ['/home/yourusername/your-project-folder/payslip/static']
```

## Step 8: Collect Static Files

In the Bash console:
```bash
cd ~/your-project-folder
source venv/bin/activate
python manage.py collectstatic --noinput
```

## Step 9: Run Migrations

```bash
python manage.py migrate
```

## Step 10: Reload Web App

1. Go back to the **Web** tab
2. Click the big green **Reload** button

## Step 11: Test Your App

Visit: `https://yourusername.pythonanywhere.com`

## Common Issues & Fixes

### Issue 1: "Something went wrong" Error
**Fix:** Check the **Error log** in the Web tab for details

### Issue 2: Static Files Not Loading
**Fix:** 
```bash
python manage.py collectstatic --noinput
```
Then reload the web app

### Issue 3: ModuleNotFoundError
**Fix:** Make sure virtualenv path is correct in Web tab and all packages are installed

### Issue 4: DisallowedHost Error
**Fix:** Add your domain to ALLOWED_HOSTS in settings.py:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
```

### Issue 5: 404 on All Pages
**Fix:** Check that your WSGI file path is correct and points to the right project

## Quick Troubleshooting Checklist

- [ ] Virtual environment path is correct in Web tab
- [ ] WSGI file has correct paths (username and folder name)
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Migrations run: `python manage.py migrate`
- [ ] ALLOWED_HOSTS includes your PythonAnywhere domain
- [ ] Web app reloaded after changes
- [ ] Check error logs in Web tab

## File Upload Considerations

Since your app handles file uploads (Excel, images), make sure:
1. Upload directory has write permissions
2. Consider storing uploads in `/home/yourusername/uploads/` folder
3. Create the folder: `mkdir ~/uploads`

## For Updates

When you update your code:
```bash
cd ~/your-project-folder
git pull  # if using git
source venv/bin/activate
pip install -r requirements.txt  # if requirements changed
python manage.py collectstatic --noinput
python manage.py migrate  # if models changed
```

Then **Reload** the web app in the Web tab.

---

## Your Specific Configuration

Based on your project structure:

**Project Name:** `Payslip`
**Settings Module:** `payslip_project.settings`
**WSGI Application:** `payslip_project.wsgi.application`

**Your WSGI file should look like:**
```python
import os
import sys

project_home = '/home/yourusername/Payslip'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'payslip_project.settings'

activate_this = '/home/yourusername/Payslip/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `yourusername` with your actual PythonAnywhere username!**

