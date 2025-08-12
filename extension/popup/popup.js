/**
 * Popup UI Controller
 */

class PopupController {
  constructor() {
    this.userProfile = null;
    this.settings = null;
    this.init();
  }

  async init() {
    await this.loadData();
    this.setupEventListeners();
    this.updateUI();
    this.checkStatus();
  }

  async loadData() {
    // Load user profile
    const profileResult = await chrome.storage.sync.get('userProfile');
    this.userProfile = profileResult.userProfile || {};

    // Load settings
    const settingsResult = await chrome.storage.sync.get('settings');
    this.settings = settingsResult.settings || {};

    // Load today's stats
    await this.loadStats();
  }

  setupEventListeners() {
    // Profile form
    document.getElementById('save-profile').addEventListener('click', () => {
      this.saveProfile();
    });

    // Quick actions
    document.getElementById('analyze-page').addEventListener('click', () => {
      this.analyzePage();
    });

    document.getElementById('auto-fill').addEventListener('click', () => {
      this.autoFill();
    });

    document.getElementById('take-screenshot').addEventListener('click', () => {
      this.takeScreenshot();
    });

    // Settings
    document.getElementById('auto-submit').addEventListener('change', (e) => {
      this.updateSetting('autoSubmitEnabled', e.target.checked);
    });

    document.getElementById('require-confirmation').addEventListener('change', (e) => {
      this.updateSetting('confirmBeforeSubmit', e.target.checked);
    });

    document.getElementById('max-applications').addEventListener('change', (e) => {
      this.updateSetting('maxDailyApplications', parseInt(e.target.value));
    });

    // Footer links
    document.getElementById('view-logs').addEventListener('click', (e) => {
      e.preventDefault();
      this.viewLogs();
    });

    document.getElementById('export-data').addEventListener('click', (e) => {
      e.preventDefault();
      this.exportData();
    });

    document.getElementById('help').addEventListener('click', (e) => {
      e.preventDefault();
      this.openHelp();
    });

    // Companion
    document.getElementById('start-companion').addEventListener('click', () => {
      this.startCompanion();
    });
  }

  updateUI() {
    // Populate profile form
    if (this.userProfile) {
      document.getElementById('firstName').value = this.userProfile.firstName || '';
      document.getElementById('lastName').value = this.userProfile.lastName || '';
      document.getElementById('email').value = this.userProfile.email || '';
      document.getElementById('phone').value = this.userProfile.phone || '';
      document.getElementById('location').value = this.userProfile.location || '';
      document.getElementById('workAuth').value = this.userProfile.workAuthorization || '';
      document.getElementById('skills').value = (this.userProfile.skills || []).join(', ');
    }

    // Populate settings
    if (this.settings) {
      document.getElementById('auto-submit').checked = this.settings.autoSubmitEnabled || false;
      document.getElementById('require-confirmation').checked = this.settings.confirmBeforeSubmit !== false;
      document.getElementById('max-applications').value = this.settings.maxDailyApplications || 10;
    }
  }

  async saveProfile() {
    const button = document.getElementById('save-profile');
    button.classList.add('loading');

    try {
      const profile = {
        firstName: document.getElementById('firstName').value.trim(),
        lastName: document.getElementById('lastName').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        location: document.getElementById('location').value.trim(),
        workAuthorization: document.getElementById('workAuth').value,
        skills: document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s),
        resumePath: this.userProfile.resumePath || '',
        preferences: {
          autoSubmit: this.settings.autoSubmitEnabled || false,
          requireConfirmation: this.settings.confirmBeforeSubmit !== false,
          maxApplicationsPerDay: this.settings.maxDailyApplications || 10
        }
      };

      // Validate required fields
      if (!profile.firstName || !profile.lastName || !profile.email) {
        this.showMessage('Please fill in all required fields', 'error');
        return;
      }

      await chrome.storage.sync.set({ userProfile: profile });
      this.userProfile = profile;

      // Notify background script
      chrome.runtime.sendMessage({ action: 'saveUserProfile', data: profile });

      this.showMessage('Profile saved successfully!', 'success');

    } catch (error) {
      console.error('Error saving profile:', error);
      this.showMessage('Error saving profile', 'error');
    } finally {
      button.classList.remove('loading');
    }
  }

  async analyzePage() {
    const button = document.getElementById('analyze-page');
    button.classList.add('loading');

    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.url.includes('indeed.ca') && !tab.url.includes('ca.indeed.com')) {
        this.showMessage('Please navigate to Indeed.ca first', 'warning');
        return;
      }

      // Send message to content script
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'analyzePage' });
      
      if (response && response.success) {
        this.showMessage('Page analyzed successfully!', 'success');
      } else {
        this.showMessage('Could not analyze page', 'error');
      }

    } catch (error) {
      console.error('Error analyzing page:', error);
      this.showMessage('Error analyzing page', 'error');
    } finally {
      button.classList.remove('loading');
    }
  }

  async autoFill() {
    if (!this.userProfile.firstName) {
      this.showMessage('Please save your profile first', 'warning');
      return;
    }

    const button = document.getElementById('auto-fill');
    button.classList.add('loading');

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.url.includes('indeed.ca') && !tab.url.includes('ca.indeed.com')) {
        this.showMessage('Please navigate to Indeed.ca first', 'warning');
        return;
      }

      const response = await chrome.tabs.sendMessage(tab.id, { action: 'startAutoFill' });
      
      if (response && response.success) {
        this.showMessage('Auto-fill started!', 'success');
        window.close(); // Close popup to avoid blocking
      } else {
        this.showMessage('Could not start auto-fill', 'error');
      }

    } catch (error) {
      console.error('Error starting auto-fill:', error);
      this.showMessage('Error starting auto-fill', 'error');
    } finally {
      button.classList.remove('loading');
    }
  }

  async takeScreenshot() {
    const button = document.getElementById('take-screenshot');
    button.classList.add('loading');

    try {
      const response = await chrome.runtime.sendMessage({ 
        action: 'takeScreenshot', 
        data: { stage: 'manual' } 
      });
      
      if (response && response.success) {
        this.showMessage('Screenshot taken!', 'success');
      } else {
        this.showMessage('Error taking screenshot', 'error');
      }

    } catch (error) {
      console.error('Error taking screenshot:', error);
      this.showMessage('Screenshot failed', 'error');
    } finally {
      button.classList.remove('loading');
    }
  }

  async updateSetting(key, value) {
    this.settings[key] = value;
    await chrome.storage.sync.set({ settings: this.settings });
    
    // Notify background script of settings change
    chrome.runtime.sendMessage({ 
      action: 'settingsUpdated', 
      data: { [key]: value } 
    });
  }

  async checkStatus() {
    // Check extension status
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const isIndeedPage = tab.url.includes('indeed.ca') || tab.url.includes('ca.indeed.com');
      
      const statusDot = document.getElementById('status-dot');
      const statusText = document.getElementById('status-text');
      
      if (isIndeedPage) {
        statusDot.className = 'dot online';
        statusText.textContent = 'Active on Indeed.ca';
      } else {
        statusDot.className = 'dot offline';
        statusText.textContent = 'Navigate to Indeed.ca';
      }

    } catch (error) {
      console.error('Error checking status:', error);
    }

    // Check companion status
    this.checkCompanionStatus();
  }

  async checkCompanionStatus() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'checkCompanionStatus' });
      const companionText = document.getElementById('companion-text');
      const startButton = document.getElementById('start-companion');

      if (response && response.companionActive) {
        companionText.textContent = '✅ Running';
        companionText.style.color = '#28a745';
        startButton.style.display = 'none';
      } else {
        companionText.textContent = '❌ Not Running';
        companionText.style.color = '#dc3545';
        startButton.style.display = 'block';
      }

    } catch (error) {
      console.error('Error checking companion status:', error);
      const companionText = document.getElementById('companion-text');
      companionText.textContent = '❓ Unknown';
      companionText.style.color = '#6c757d';
    }
  }

  async loadStats() {
    try {
      const today = new Date().toDateString();
      const counterKey = `applications_${today}`;
      
      const result = await chrome.storage.local.get([counterKey, 'totalApplications', 'successfulApplications']);
      
      const todayCount = result[counterKey] || 0;
      const totalCount = result.totalApplications || 0;
      const successCount = result.successfulApplications || 0;
      
      document.getElementById('applications-today').textContent = todayCount;
      
      if (totalCount > 0) {
        const successRate = Math.round((successCount / totalCount) * 100);
        document.getElementById('success-rate').textContent = `${successRate}%`;
      } else {
        document.getElementById('success-rate').textContent = '0%';
      }

    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }

  showMessage(text, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());

    // Create new message
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;

    // Insert at top of main content
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(message, mainContent.firstChild);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (message.parentNode) {
        message.remove();
      }
    }, 3000);
  }

  viewLogs() {
    chrome.tabs.create({ url: chrome.runtime.getURL('logs/logs.html') });
  }

  exportData() {
    // TODO: Implement data export functionality
    this.showMessage('Export functionality coming soon!', 'info');
  }

  openHelp() {
    chrome.tabs.create({ url: 'https://github.com/your-repo/indeed-automation#help' });
  }

  startCompanion() {
    this.showMessage('Please start the local companion script manually', 'info');
    // Could potentially try to launch via native messaging in future
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});