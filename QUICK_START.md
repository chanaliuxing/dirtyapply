# Indeed Automation System - Quick Start Guide

Get your automated job application system up and running in minutes!

## 🚀 System Overview

This system automates job applications on Indeed.ca with:
- **Chrome Extension** - Browser automation for Indeed.ca
- **Local Companion** - Desktop service for form filling
- **Cloud Backend** - AI-powered resume tailoring and job matching

## 📋 Prerequisites

- **Python 3.8+** installed
- **Chrome Browser** 
- **Git** (optional, for cloning)

## ⚡ Quick Setup (5 Minutes)

### 1. Install Chrome Extension

```bash
# Navigate to extension folder
cd extension/

# Open Chrome and go to chrome://extensions/
# Enable "Developer mode" (top right toggle)
# Click "Load unpacked" and select the extension folder
```

### 2. Start Local Companion

```bash
# Navigate to local companion
cd local-companion/

# Install dependencies
pip install -r requirements.txt

# Start the companion service
python companion.py
```

### 3. Start Cloud Backend (Optional - for AI features)

```bash
# Navigate to cloud backend
cd cloud-backend/

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
set OPENAI_API_KEY=your_openai_api_key_here
set ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🎯 Basic Usage

### Using the Chrome Extension

1. **Go to Indeed.ca** and search for jobs
2. **Click the extension icon** in your Chrome toolbar
3. **Enable automation** in the popup
4. **Navigate to job postings** - the system will auto-fill applications

### Extension Controls

- **Start/Stop Automation**: Toggle automation on/off
- **Settings**: Configure automation behavior
- **View Logs**: Monitor automation activity

### Local Companion Features

- **Automatic Form Detection**: Detects Indeed application forms
- **Smart Field Mapping**: Maps your data to form fields
- **Screenshot Capture**: Takes screenshots for verification
- **Log Tracking**: Maintains detailed operation logs

## 🛡️ Safety Features (Always Enabled)

- ✅ **No Auto-Submit**: Never submits applications automatically
- ✅ **Human Confirmation**: Always requires your approval
- ✅ **Daily Limits**: Maximum 25 applications per day
- ✅ **Domain Whitelist**: Only works on Indeed.ca
- ✅ **Manual Review**: You control every submission

## 📁 Project Structure

```
indeed-automation/
├── extension/           # Chrome extension
├── local-companion/     # Desktop automation service
├── cloud-backend/       # AI backend (optional)
├── automated-tests/     # Testing scripts
└── documentation/       # Setup guides
```

## 🔧 Configuration

### Basic Settings (No AI)

The system works out-of-the-box without AI features:
- Form auto-filling
- Basic job matching  
- Application tracking
- Screenshot capture

### Advanced Settings (With AI)

For AI-powered features, configure:

1. **API Keys** (in cloud-backend/.env):
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
SECRET_KEY=your-secret-key
```

2. **Database** (optional):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/indeed_db
REDIS_URL=redis://localhost:6379
```

## 🚦 System Status

### Essential Components
- ✅ **Chrome Extension** - Browser automation
- ✅ **Local Companion** - Form filling service  

### Optional AI Components  
- 🔄 **Cloud Backend** - AI resume tailoring
- 🔄 **Database** - Advanced tracking
- 🔄 **Vector DB** - Semantic matching

## 📝 Usage Examples

### Basic Job Application
1. Open Indeed.ca and search for jobs
2. Click on a job posting
3. Extension automatically fills application form
4. Review and submit manually

### With AI Features (if backend running)
1. System analyzes job requirements
2. Tailors your resume automatically
3. Generates personalized cover letters
4. Suggests relevant skills to highlight
5. Provides job match scoring

## 🐛 Troubleshooting

### Common Issues

**Extension not loading?**
- Ensure Developer mode is enabled
- Try reloading the extension
- Check Chrome console for errors

**Companion not starting?**
- Verify Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check firewall settings (port 8080)

**Forms not auto-filling?**
- Ensure companion service is running
- Check if you're on Indeed.ca (not .com)
- Verify extension permissions

### Log Files
- **Extension**: Check Chrome DevTools console
- **Companion**: `companion.log` in local-companion folder
- **Backend**: Console output when running

## 📞 Support

### Quick Fixes
1. **Restart all services** (extension, companion, backend)
2. **Clear Chrome cache** for Indeed.ca
3. **Check log files** for error messages
4. **Verify permissions** for all components

### Advanced Support
- Check `TESTING_GUIDE.md` for diagnostic tests
- Review `REQUIREMENTS_VALIDATION.md` for system status
- Run validation scripts in automated-tests folder

## 🔒 Privacy & Security

- **Local Processing**: Most data stays on your machine
- **No Data Collection**: System doesn't collect personal information  
- **Secure Storage**: Credentials encrypted locally
- **Manual Control**: You approve all applications

## 🎉 You're Ready!

Your Indeed automation system is now configured and ready to use. The system prioritizes your safety and control while providing powerful automation features.

**Remember**: Always review applications before submitting. The system is designed to assist, not replace your judgment.

---

*For detailed configuration and advanced features, see the full documentation in each component folder.*