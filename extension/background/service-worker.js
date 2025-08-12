/**
 * Service Worker for Indeed.ca Automation
 * Handles communication between content script, popup, and local companion
 */

class IndeedServiceWorker {
  constructor() {
    this.localCompanionUrl = 'http://127.0.0.1:8001'; // Default, will be updated by auto-detection
    this.userProfile = null;
    this.whitelist = ['ca.indeed.com', 'indeed.ca'];
    this.init();
  }

  init() {
    console.log('Indeed Automation Service Worker initialized');
    this.setupMessageHandlers();
    this.loadUserProfile();
    this.checkLocalCompanion();
  }

  setupMessageHandlers() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async response
    });

    // Handle extension icon click
    chrome.action.onClicked.addListener((tab) => {
      this.openSidePanel(tab);
    });

    // Monitor tab updates
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && this.isWhitelistedDomain(tab.url)) {
        this.notifyContentScript(tabId, 'pageReloaded');
      }
    });
  }

  async handleMessage(message, sender, sendResponse) {
    const { action, data } = message;

    try {
      switch (action) {
        case 'getUserProfile':
          sendResponse({ success: true, data: await this.getUserProfile() });
          break;

        case 'saveUserProfile':
          await this.saveUserProfile(data);
          sendResponse({ success: true });
          break;

        case 'jobDataExtracted':
          await this.processJobData(data);
          sendResponse({ success: true });
          break;

        case 'formFieldsDetected':
          await this.processFormFields(data);
          sendResponse({ success: true });
          break;

        case 'uploadFile':
          await this.handleFileUpload(data);
          sendResponse({ success: true });
          break;

        case 'takeScreenshot':
          await this.takeScreenshot(data);
          sendResponse({ success: true });
          break;

        case 'applicationSubmitted':
          await this.logApplicationSubmission(data);
          sendResponse({ success: true });
          break;

        case 'openSidePanel':
          await this.openSidePanel(sender.tab);
          sendResponse({ success: true });
          break;

        case 'checkCompanionStatus':
          const status = await this.checkLocalCompanion();
          sendResponse({ success: true, companionActive: status });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async getUserProfile() {
    if (!this.userProfile) {
      const result = await chrome.storage.sync.get('userProfile');
      this.userProfile = result.userProfile || this.getDefaultProfile();
    }
    return this.userProfile;
  }

  getDefaultProfile() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      location: '',
      workAuthorization: '',
      availableStartDate: '',
      skills: [],
      resumePath: '',
      preferences: {
        autoSubmit: false,
        requireConfirmation: true,
        maxApplicationsPerDay: 10
      }
    };
  }

  async saveUserProfile(profile) {
    this.userProfile = profile;
    await chrome.storage.sync.set({ userProfile: profile });
    console.log('User profile saved');
  }

  async processJobData(jobData) {
    // Store job data and analyze for automation opportunities
    const jobId = jobData.jobId || Date.now().toString();
    
    await chrome.storage.local.set({
      [`job_${jobId}`]: {
        ...jobData,
        timestamp: new Date().toISOString(),
        status: 'analyzed'
      }
    });

    // Notify content script with analysis results
    if (jobData.matchScore) {
      this.notifyContentScript(null, 'jobAnalyzed', {
        jobId,
        matchScore: jobData.matchScore,
        requiredSkills: jobData.requiredSkills
      });
    }

    console.log('Job data processed:', jobData.title, jobData.company);
  }

  async processFormFields(formFields) {
    // Analyze form complexity and prepare auto-fill strategy
    const fieldCount = Object.keys(formFields).filter(key => formFields[key]).length;
    const hasFileUpload = Object.values(formFields).some(field => 
      field && field.type === 'file'
    );

    const strategy = {
      complexity: fieldCount > 5 ? 'high' : 'low',
      requiresCompanion: hasFileUpload,
      estimatedTime: fieldCount * 2 + (hasFileUpload ? 10 : 0)
    };

    console.log('Form analysis:', strategy);
    return strategy;
  }

  async handleFileUpload(data) {
    // Delegate file upload to local companion
    try {
      const response = await fetch(`${this.localCompanionUrl}/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: data.filePath,
          input_selector: data.selector
        })
      });

      if (!response.ok) {
        throw new Error(`Companion upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('File upload successful:', result);
      
    } catch (error) {
      console.error('File upload error:', error);
      // Fallback: notify user to upload manually
      this.notifyContentScript(null, 'fileUploadFailed', { 
        error: error.message 
      });
    }
  }

  async takeScreenshot(data) {
    try {
      const response = await fetch(`${this.localCompanionUrl}/screenshot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: data.filename || `screenshot_${data.stage}_${Date.now()}.png`
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Screenshot taken:', result.filepath);
      }
    } catch (error) {
      console.error('Screenshot error:', error);
    }
  }

  async logApplicationSubmission(data) {
    // Store application record
    const applicationRecord = {
      ...data,
      timestamp: new Date().toISOString(),
      domain: 'ca.indeed.com'
    };

    await chrome.storage.local.set({
      [`application_${data.jobId}_${Date.now()}`]: applicationRecord
    });

    // Update daily counter
    const today = new Date().toDateString();
    const counterKey = `applications_${today}`;
    const result = await chrome.storage.local.get(counterKey);
    const count = (result[counterKey] || 0) + 1;
    
    await chrome.storage.local.set({ [counterKey]: count });

    console.log('Application logged:', data.jobId, data.success);
    
    // Check daily limit
    const profile = await this.getUserProfile();
    if (count >= profile.preferences.maxApplicationsPerDay) {
      this.notifyContentScript(null, 'dailyLimitReached', { count });
    }
  }

  async openSidePanel(tab) {
    try {
      // Check if sidePanel API is available (Chrome 114+)
      if (typeof chrome.sidePanel !== 'undefined' && chrome.sidePanel.open) {
        await chrome.sidePanel.open({ tabId: tab.id });
      } else {
        console.log('Side panel not supported, using popup fallback');
        // For older Chrome versions, just log - popup will open via manifest
      }
    } catch (error) {
      console.log('Side panel error, using popup fallback:', error.message);
      // Popup will open via manifest action
    }
  }

  async checkLocalCompanion() {
    try {
      // Check multiple common ports
      const ports = [8001, 8002, 8003, 8080];
      
      for (const port of ports) {
        try {
          const response = await this.fetchWithTimeout(`http://127.0.0.1:${port}/health`, 2000);
          
          if (response.ok) {
            this.localCompanionUrl = `http://127.0.0.1:${port}`;
            console.log(`Local companion found on port ${port}`);
            await chrome.storage.local.set({ companionStatus: true, companionPort: port });
            return true;
          }
        } catch (portError) {
          // Try next port
          continue;
        }
      }
      
      // No companion found
      await chrome.storage.local.set({ companionStatus: false });
      return false;
      
    } catch (error) {
      console.log('Local companion check failed:', error.message);
      await chrome.storage.local.set({ companionStatus: false });
      return false;
    }
  }

  async fetchWithTimeout(url, timeout = 3000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  isWhitelistedDomain(url) {
    if (!url) return false;
    return this.whitelist.some(domain => url.includes(domain));
  }

  async notifyContentScript(tabId, action, data = {}) {
    try {
      if (!tabId) {
        // Send to all Indeed.ca tabs
        const tabs = await chrome.tabs.query({
          url: ['https://ca.indeed.com/*', 'https://indeed.ca/*']
        });
        
        for (const tab of tabs) {
          chrome.tabs.sendMessage(tab.id, { action, data }).catch(() => {
            // Ignore errors for tabs without content script
          });
        }
      } else {
        await chrome.tabs.sendMessage(tabId, { action, data });
      }
    } catch (error) {
      console.error('Error notifying content script:', error);
    }
  }

  async loadUserProfile() {
    this.userProfile = await this.getUserProfile();
    console.log('User profile loaded');
  }
}

// Initialize service worker with error handling
let serviceWorker;
try {
  serviceWorker = new IndeedServiceWorker();
  console.log('Service worker initialized successfully');
} catch (error) {
  console.error('Service worker initialization failed:', error);
  // Create minimal service worker for basic functionality
  serviceWorker = {
    async handleMessage(message, sender, sendResponse) {
      sendResponse({ success: false, error: 'Service worker not fully initialized' });
    }
  };
}

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Indeed Automation extension installed');
    // Set default settings
    chrome.storage.sync.set({
      settings: {
        autoSubmitEnabled: false,
        confirmBeforeSubmit: true,
        maxDailyApplications: 10,
        companionPort: 8001
      }
    });
  }
});

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log('Indeed Automation extension started');
  serviceWorker.checkLocalCompanion();
});