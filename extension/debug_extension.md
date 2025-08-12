# Chrome Extension Debug Guide

## 🔍 How to Check Extension Errors

### Step 1: Check Extension Errors
1. Open Chrome and go to `chrome://extensions/`
2. Find "Indeed.ca Auto Apply Assistant"
3. Click **"Inspect views: service worker"**
4. Look for any **red error messages** in the console

### Step 2: Common Error Types & Solutions

#### Error: "Cannot access chrome.sidePanel"
**Fix:** Update to Chrome 114+ or disable side panel
```javascript
// Temporary fix - comment out side panel in manifest.json
// "side_panel": {
//   "default_path": "sidepanel/panel.html"
// },
```

#### Error: "Failed to fetch local companion"
**Fix:** Make sure local companion is running
```bash
cd local-companion
python companion.py
```

#### Error: "Content script injection failed"
**Fix:** Reload extension and refresh Indeed.ca page
1. Go to `chrome://extensions/`
2. Click reload button on the extension
3. Go to Indeed.ca and refresh the page

#### Error: "Manifest parsing error"
**Fix:** Check manifest.json syntax
- Make sure all commas are correct
- No trailing commas
- Proper JSON formatting

### Step 3: Test Extension Step by Step

#### Basic Functionality Test:
1. **Load Extension:**
   - Extension appears in `chrome://extensions/`
   - No immediate errors shown

2. **Service Worker:**
   - Click "Inspect views: service worker"
   - Should see: "Indeed Automation Service Worker initialized"

3. **Popup Test:**
   - Click extension icon in toolbar
   - Popup should open without errors

4. **Content Script Test:**
   - Go to `https://ca.indeed.com/`
   - Open DevTools (F12)
   - Should see: "Indeed automation content script loaded"

### Step 4: Manual Error Checking

Open DevTools on Indeed.ca and run these commands:

```javascript
// Test 1: Check if content script loaded
console.log('Testing content script...');

// Test 2: Check extension communication
chrome.runtime.sendMessage({action: 'getUserProfile'}, (response) => {
  console.log('Extension response:', response);
});

// Test 3: Check local companion connection
fetch('http://127.0.0.1:8001/health')
  .then(r => r.json())
  .then(data => console.log('Companion status:', data))
  .catch(err => console.log('Companion error:', err));
```

### Step 5: Reset Everything

If nothing works:

1. **Remove and reload extension:**
   ```
   1. Go to chrome://extensions/
   2. Click "Remove" on the extension
   3. Click "Load unpacked" and select the extension folder again
   ```

2. **Restart Chrome completely**

3. **Clear Chrome cache for Indeed.ca:**
   ```
   1. Go to chrome://settings/content/all
   2. Search for "indeed"
   3. Delete all Indeed.ca data
   ```

### Step 6: Chrome Version Compatibility

**Check Chrome Version:**
```
chrome://version/
```

**Minimum Requirements:**
- Chrome 88+ (basic functionality)
- Chrome 114+ (full features including side panel)

**If using older Chrome:**
Comment out these lines in `manifest.json`:
```json
// "side_panel": {
//   "default_path": "sidepanel/panel.html"
// },
```

## 🚨 Most Common Issues

### Issue 1: Extension Not Loading
**Symptoms:** Extension doesn't appear or shows errors immediately

**Solutions:**
1. Check Developer mode is enabled
2. Try loading a different folder
3. Check file permissions
4. Restart Chrome as administrator

### Issue 2: Service Worker Errors
**Symptoms:** Red errors when clicking "Inspect views"

**Solutions:**
1. Make sure all files exist (service-worker.js, popup.html, etc.)
2. Check JavaScript syntax
3. Update Chrome to latest version

### Issue 3: Cannot Connect to Local Companion
**Symptoms:** "Failed to fetch" errors

**Solutions:**
1. Start companion: `python companion.py`
2. Check companion is on correct port
3. Verify no firewall blocking localhost:8001

### Issue 4: Content Script Not Working
**Symptoms:** No automation on Indeed.ca pages

**Solutions:**
1. Make sure you're on ca.indeed.com (not .com)
2. Reload extension and refresh page
3. Check content script file exists

## ✅ Success Indicators

You should see these messages if everything works:

**Extension Console:**
```
Indeed Automation Service Worker initialized
Local companion available at http://127.0.0.1:8001
User profile loaded
```

**Indeed.ca Page Console:**
```
Indeed automation content script loaded
Form detection enabled
Ready to assist with applications
```

**Local Companion Console:**
```
INFO - Started server process
INFO - Application startup complete.
```

## 🆘 Still Having Issues?

If you're still seeing errors:

1. **Tell me the exact error message** you see in Chrome DevTools
2. **Check these files exist:**
   - `extension/manifest.json`
   - `extension/background/service-worker.js`  
   - `extension/popup/popup.html`
   - `extension/content/indeed-automation.js`

3. **Run the companion first:**
   ```bash
   cd local-companion
   python companion.py
   # Wait for "Application startup complete"
   ```

4. **Then reload the extension:**
   - Go to chrome://extensions/
   - Click reload button
   - Check for errors

Let me know what specific error message you see and I can provide a targeted fix!