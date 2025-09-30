# Google Sheets API Setup Guide

This guide will walk you through setting up Google Sheets API integration for the French Novel Processor.

---

## 📋 Prerequisites

- Google Account (Gmail, Workspace, etc.)
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- French Novel Processor installed and working

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click **"New Project"**
4. Enter project name: `FrenchNovelProcessor` (or any name you like)
5. Click **"Create"**
6. Wait for project creation (takes a few seconds)
7. Select your new project from the dropdown

### Step 2: Enable Required APIs

#### Enable Google Sheets API

1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. Search for: `Google Sheets API`
3. Click on **"Google Sheets API"**
4. Click **"Enable"** button
5. Wait for activation

#### Enable Google Drive API

1. Click **"APIs & Services"** → **"Library"** again
2. Search for: `Google Drive API`
3. Click on **"Google Drive API"**
4. Click **"Enable"** button
5. Wait for activation

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (unless you have a Workspace account)
3. Click **"Create"**

**App Information:**
- App name: `French Novel Processor`
- User support email: Your email
- Developer contact: Your email
- Click **"Save and Continue"**

**Scopes:**
- Click **"Add or Remove Scopes"**
- Search for: `.../auth/spreadsheets`
- Select: `https://www.googleapis.com/auth/spreadsheets`
- Search for: `.../auth/drive.file`
- Select: `https://www.googleapis.com/auth/drive.file`
- Click **"Update"**
- Click **"Save and Continue"**

**Test Users (for External apps):**
- Click **"Add Users"**
- Add your email address
- Click **"Save and Continue"**

**Summary:**
- Review and click **"Back to Dashboard"**

### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** at the top
3. Select **"OAuth client ID"**

**Configure:**
- Application type: **Desktop app**
- Name: `French Novel Processor Desktop`
- Click **"Create"**

**Download Credentials:**
1. A dialog will appear with your client ID and secret
2. Click **"Download JSON"**
3. Rename the downloaded file to: `credentials.json`
4. Move it to your project root directory:
   ```
   H:\WORK\FrenchNovelProcessor\credentials.json
   ```

### Step 5: Test the Integration

1. Open Command Prompt in your project directory
2. Activate virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

3. Run the test script:
   ```bash
   python tests\test_google_sheets.py
   ```

4. **First-time authorization:**
   - A browser window will open
   - Select your Google account
   - Click **"Allow"** to grant permissions
   - You may see a warning "This app isn't verified"
     - Click **"Advanced"**
     - Click **"Go to French Novel Processor (unsafe)"**
   - Grant all requested permissions
   - Browser will show "The authentication flow has completed"
   - Close the browser window

5. **Check results:**
   - The script will create a test spreadsheet
   - You'll see a URL to view it
   - The `token.json` file will be created automatically

---

## 📁 File Structure

After setup, you should have:

```
FrenchNovelProcessor/
├── credentials.json     ← Downloaded from Google Cloud Console
├── token.json          ← Auto-generated after first authorization
└── ...
```

**Important:**
- ✅ `credentials.json` - Keep this file secure, don't share publicly
- ✅ `token.json` - Generated after first auth, can be regenerated
- 🚫 Never commit these files to Git (they're in .gitignore)

---

## 🔧 Troubleshooting

### "credentials.json not found"

**Solution:**
- Make sure you downloaded the credentials file
- Rename it exactly to `credentials.json`
- Place it in the project root (same level as README.md)

### "Access denied" or "Permission denied"

**Solution:**
- Make sure you enabled both APIs (Sheets + Drive)
- Check OAuth consent screen configuration
- Verify you added your email as a test user
- Try deleting `token.json` and re-authenticating

### "This app isn't verified"

**This is normal!** Your app is in development mode.

**To proceed:**
1. Click **"Advanced"**
2. Click **"Go to French Novel Processor (unsafe)"**
3. Grant permissions

**To verify your app (optional):**
- Required if you want to publish publicly
- Not necessary for personal use

### Browser doesn't open for authorization

**Solution:**
1. Copy the URL from terminal
2. Open it manually in your browser
3. Complete authorization
4. Return to terminal

### "Invalid grant" or "Token expired"

**Solution:**
- Delete `token.json`
- Run the application again
- Re-authorize when prompted

---

## 🔒 Security Notes

### What these credentials do:

**credentials.json:**
- Identifies your application to Google
- Contains client ID and client secret
- Required to request authorization

**token.json:**
- Contains your personal authorization
- Allows the app to access YOUR Google account
- Can be revoked at any time

### How to revoke access:

1. Go to [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
2. Find "French Novel Processor"
3. Click **"Remove Access"**
4. Delete `token.json` from your project

### Best practices:

- ✅ Keep `credentials.json` secure
- ✅ Don't share `token.json`
- ✅ Add both files to `.gitignore`
- ✅ Regenerate if compromised
- ❌ Don't commit to public repositories
- ❌ Don't share on forums or chat

---

## 🎯 Testing Your Setup

### Quick Test

```bash
python tests\test_google_sheets.py
```

**Expected output:**
```
============================================================
Testing Google Sheets Authentication
============================================================

Credentials file: H:\WORK\FrenchNovelProcessor\credentials.json
Token file: H:\WORK\FrenchNovelProcessor\token.json

✓ credentials.json found

⏳ Authenticating with Google Sheets API...
✓ Authentication successful!
✓ Token saved to: H:\WORK\FrenchNovelProcessor\token.json

============================================================
Testing Spreadsheet Creation
============================================================

⏳ Creating test spreadsheet...

✓ Spreadsheet created successfully!
📊 Spreadsheet ID: 1A2B3C...
🔗 URL: https://docs.google.com/spreadsheets/d/...

...

============================================================
✅ ALL TESTS PASSED!
============================================================

📊 View your test spreadsheet:
🔗 https://docs.google.com/spreadsheets/d/...
```

### Full Integration Test

Run a complete PDF processing:

```bash
scripts\run_application.bat
```

Then:
1. Upload a PDF
2. Process it
3. Check for Google Sheets link in results
4. Click the link to open in browser

---

## 📊 Using Google Sheets Output

### Automatic Creation

When you process a PDF:
1. Local Excel and CSV files are created
2. Google Spreadsheet is created automatically
3. Link appears in results section
4. Click to open in new tab

### Features

**Three Sheets:**
1. **Sentences** - Main results
   - Color-coded by method
   - Green = AI-rewritten
   - Orange = Mechanical
   - White = Direct

2. **Processing Log** - Detailed log (if enabled)
   - All processing steps
   - Errors and warnings
   - API call details

3. **Summary** - Statistics
   - Total sentences
   - Processing time
   - Cost breakdown
   - Success rate

### Sharing

To share your results:
1. Open the Google Spreadsheet
2. Click **"Share"** button (top right)
3. Add email addresses or generate link
4. Set permissions (Viewer, Commenter, Editor)
5. Click **"Send"** or **"Copy link"**

### Offline Access

Google Sheets offers offline access:
1. Open the spreadsheet
2. Click **File** → **Make available offline**
3. Install Google Docs Offline extension
4. Access even without internet

---

## 💡 Tips & Best Practices

### Organizing Your Spreadsheets

**Create a folder:**
1. Go to [Google Drive](https://drive.google.com)
2. Create folder: "French Novel Processing"
3. Move generated spreadsheets there
4. Keep organized by date or novel name

### Collaborative Work

**Multiple people can:**
- View results simultaneously
- Add comments
- Make edits (if granted permission)
- Export to different formats

### Integration with Other Tools

**Google Sheets connects to:**
- Google Data Studio (visualizations)
- Google Forms (data collection)
- Other Google Workspace apps
- Third-party apps via Zapier/IFTTT

---

## 🆘 Getting Help

### Official Documentation

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

### Common Issues

1. **Quota exceeded**
   - Default: 100 requests/100 seconds/user
   - Solution: Throttle requests, increase quota

2. **Rate limiting**
   - Solution: App handles this automatically
   - Wait a few seconds between large operations

3. **Permission errors**
   - Solution: Re-authorize or check scopes

---

## ✅ Checklist

Before processing PDFs with Google Sheets output:

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created and downloaded
- [ ] `credentials.json` in project root
- [ ] Test script passed successfully
- [ ] `token.json` created automatically
- [ ] Test spreadsheet visible in Google Drive

---

**Setup Complete!** 🎉

You can now process PDFs and get beautifully formatted Google Spreadsheets automatically!
