# Apply-Copilot 🤖

**Job-Driven Resume Rewriter & Auto-Apply Agent**

An intelligent, ethical job application automation system implementing the "职位→简历重写（JTR）+ ATS 优化 + 自动填表/提交" specification with **Reasoned Synthesis (RS)** capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/chrome-extension-green.svg)](https://developer.chrome.com/docs/extensions/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a96e.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Overview

This system automates job applications on Indeed.ca while maintaining ethical standards and human oversight. It combines browser automation, AI-powered resume tailoring, and intelligent job matching to streamline your job search process.

### ⚡ Quick Start
**Ready to get started?** → **[QUICK_START.md](QUICK_START.md)**

## ✨ Key Features

### 🔄 **Automated Application Process**
- **Smart Form Detection**: Automatically detects and fills Indeed.ca application forms
- **Data Persistence**: Remembers your information across sessions
- **Multi-Tab Support**: Handles multiple job applications simultaneously
- **Progress Tracking**: Monitors application status and success rates

### 🧠 **AI-Powered Job Matching**
- **Skill Analysis**: Compares your skills with job requirements
- **Experience Matching**: Evaluates experience level compatibility  
- **Salary Alignment**: Checks compensation expectations
- **Cultural Fit**: Analyzes company culture preferences

### 📄 **Resume Tailoring (JTR)**
- **Job-Tailored Resumes**: Creates custom resumes for each application
- **ATS Optimization**: Ensures compatibility with applicant tracking systems
- **Reasonable Synthesis (RS)**: Ethically enhances bullets with evidence
- **Change Tracking**: Shows exactly what was modified and why

### 🗃️ **Evidence Vault**
- **Achievement Storage**: Securely stores your professional accomplishments  
- **Contextual Retrieval**: Finds relevant evidence for each application
- **Risk Assessment**: Evaluates enhancement safety (LOW/MEDIUM/HIGH/CRITICAL)
- **Attribution Tracking**: Maintains sources for all enhancements

### 💬 **Automated Q&A Generation**
- **Question Classification**: Categorizes common application questions
- **Evidence-Based Answers**: Generates responses using your stored achievements
- **Template System**: Uses proven templates for standard questions
- **Personalization**: Tailors answers to specific jobs and companies

## 🛡️ Safety First

### Critical Safety Features (Always Enabled)
- ✅ **Auto-Submit DISABLED**: Never submits applications automatically
- ✅ **Human Confirmation REQUIRED**: You approve every submission
- ✅ **Daily Limits**: Maximum 25 applications per day
- ✅ **Domain Whitelist**: Only operates on Indeed.ca
- ✅ **Risk Assessment**: Evaluates all AI enhancements for safety

### Ethical AI Constraints
- ✅ **Evidence-Based Only**: All enhancements must be supported by evidence
- ✅ **Confidence Thresholds**: Minimum 70% confidence for AI enhancements
- ✅ **Temporal Validation**: Evidence must be from relevant time periods
- ✅ **No Fabrication**: Strict policy against creating false information
- ✅ **Full Attribution**: Complete tracking of all AI modifications

## 🏗️ System Architecture

### Components Overview

| Component | Purpose | Required | AI Features |
|-----------|---------|----------|-------------|
| **Chrome Extension** | Browser automation | ✅ Yes | ❌ No |
| **Local Companion** | Form filling service | ✅ Yes | ❌ No |  
| **Cloud Backend** | AI orchestration | 🔄 Optional | ✅ Yes |
| **Database** | Data persistence | 🔄 Optional | ✅ Yes |
| **Vector Database** | Semantic search | 🔄 Optional | ✅ Yes |

## 🚀 Installation & Setup

### Method 1: Quick Setup (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/your-repo/indeed-automation
cd indeed-automation

# 2. Follow the quick start guide
# See QUICK_START.md for detailed steps
```

### Method 2: Component-by-Component

#### Chrome Extension
```bash
cd extension/
# Load in Chrome: chrome://extensions/ -> Load unpacked
```

#### Local Companion  
```bash
cd local-companion/
pip install -r requirements.txt
python companion.py
```

#### Cloud Backend (Optional - for AI)
```bash
cd cloud-backend/
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## 📊 System Requirements

### Minimum Requirements (Basic Features)
- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.8 or higher
- **Browser**: Chrome 90+ or Chromium-based
- **RAM**: 4GB minimum
- **Storage**: 1GB available space

### Recommended Requirements (AI Features)  
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.9+ with pip
- **RAM**: 8GB or more
- **Storage**: 5GB available space
- **Internet**: Stable connection for AI services

## 📈 Performance & Limitations

### Performance Metrics
- **Form Fill Speed**: ~2-3 seconds per form
- **Resume Generation**: ~30-60 seconds with AI
- **Job Analysis**: ~10-15 seconds per job
- **Daily Throughput**: Up to 25 applications (safety limit)

### Current Limitations
- **Indeed.ca Only**: Currently supports Indeed Canada only
- **English Language**: Optimized for English job postings
- **Manual Review**: Requires human approval for all submissions
- **Internet Dependent**: AI features require internet connectivity

## 🧪 Testing & Validation

### Automated Testing
```bash
# Run component tests
cd automated-tests/
python test_components.py

# Run system validation
cd cloud-backend/
python final_validation.py
```

### Manual Testing
1. **Extension Testing**: Load extension and test on Indeed.ca
2. **Companion Testing**: Verify form detection and filling
3. **Backend Testing**: Check AI services and API endpoints

## 📚 Documentation

### User Guides
- 📖 **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- 🧪 **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing and validation
- ⚙️ **Component READMEs** - Detailed component docs

### Technical Documentation  
- 📋 **[REQUIREMENTS_VALIDATION.md](REQUIREMENTS_VALIDATION.md)** - System compliance
- 🏗️ **Architecture Docs** - Technical specifications
- 🔍 **API Documentation** - Interactive API docs (when backend running)

## 🤝 Usage Guidelines

### Best Practices
1. **Review Every Application**: Always check before submitting
2. **Customize When Needed**: Personalize auto-generated content  
3. **Monitor Daily Limits**: Stay within ethical application quotas
4. **Update Your Profile**: Keep skills and experience current
5. **Use Evidence Vault**: Store achievements for better AI enhancement

### Ethical Usage
- ✅ **Be Truthful**: All information must be accurate
- ✅ **Respect Limits**: Don't exceed daily application quotas  
- ✅ **Quality Over Quantity**: Focus on relevant applications
- ✅ **Human Oversight**: Maintain control over your applications

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# AI Service Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database (Optional)  
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Safety Settings (Pre-configured)
AUTO_SUBMIT_ENABLED=false
REQUIRE_CONFIRMATION=true
MAX_APPLICATIONS_PER_DAY=25
```

### Safety Configuration (Pre-set)
```python
# These settings are hardcoded for safety
AUTO_SUBMIT_ENABLED = False  # Never submit automatically
REQUIRE_CONFIRMATION = True  # Always ask for approval
RS_CONFIDENCE_THRESHOLD = 0.7  # High confidence required
MAX_RS_BULLETS_PER_RESUME = 15  # Reasonable limits
```

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **Application Success Rate**: Track acceptance rates
- **System Performance**: Monitor response times
- **AI Enhancement Quality**: Evaluate AI improvements
- **Daily Activity**: Summary of applications and actions

### Log Files
- **Extension Logs**: Chrome DevTools console
- **Companion Logs**: `local-companion/companion.log`
- **Backend Logs**: Console output with structured logging

## 🚨 Troubleshooting

### Common Issues & Solutions

**🔍 Extension Not Working?**
- Verify Developer mode is enabled in Chrome
- Check if you're on Indeed.ca (not .com)
- Reload the extension from chrome://extensions/

**⚡ Companion Service Issues?**
- Ensure Python 3.8+ is installed
- Check if port 8080 is available
- Verify all dependencies are installed

**🤖 AI Features Not Working?**  
- Confirm API keys are configured
- Check internet connectivity
- Verify backend service is running

### Getting Help
1. **Check Log Files** for error messages
2. **Run Diagnostic Tests** in automated-tests/
3. **Review Documentation** for your specific issue
4. **Restart All Services** as a first step

## 📄 License & Legal

### License
This project is licensed under the MIT License.

### Disclaimer  
- **Educational Purpose**: This system is for learning and personal use
- **Compliance**: Users responsible for compliance with Indeed.ca terms
- **No Warranties**: System provided as-is without guarantees
- **Ethical Use**: Users must ensure truthful and ethical application practices

### Terms of Use
By using this system, you agree to:
- ✅ Use only for legitimate job applications
- ✅ Provide accurate information in all applications  
- ✅ Respect Indeed.ca's terms of service
- ✅ Not exceed reasonable application volumes
- ✅ Maintain human oversight of all activities

## 🎉 Get Started Now!

Ready to streamline your job search? **[Start with the Quick Setup Guide →](QUICK_START.md)**

---

**Built with ❤️ for job seekers who value efficiency and ethics.**

*Last updated: August 2025*