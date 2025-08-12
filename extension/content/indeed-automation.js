/**
 * Indeed.ca Automation Content Script
 * Handles job posting extraction, form field detection, and auto-fill functionality
 */

class IndeedAutomation {
  constructor() {
    this.domain = 'ca.indeed.com';
    this.isActive = false;
    this.jobData = null;
    this.userProfile = null;
    this.whitelistDomains = ['ca.indeed.com', 'indeed.ca'];
    this.init();
  }

  init() {
    console.log('Indeed.ca Automation initialized');
    this.loadUserProfile();
    this.setupEventListeners();
    this.injectSidePanel();
    this.detectPageType();
  }

  detectPageType() {
    const url = window.location.href;
    
    if (url.includes('/viewjob?')) {
      this.handleJobDetailPage();
    } else if (url.includes('/apply?')) {
      this.handleApplicationPage();
    } else if (url.includes('/jobs?')) {
      this.handleJobListingPage();
    }
  }

  // Job Detail Page Handler
  handleJobDetailPage() {
    console.log('Job detail page detected');
    this.extractJobData();
    this.showSidePanelButton();
  }

  extractJobData() {
    try {
      // Indeed.ca job detail selectors (common patterns)
      const jobData = {
        title: this.getTextContent([
          'h1[data-jk]',
          '.jobsearch-JobInfoHeader-title span[title]',
          'h1.jobTitle span[title]'
        ]),
        company: this.getTextContent([
          '[data-testid="inlineHeader-companyName"] a',
          '.jobsearch-CompanyInfoWithoutHeaderImage a',
          '.jobsearch-InlineCompanyRating a'
        ]),
        location: this.getTextContent([
          '[data-testid="job-location"]',
          '.jobsearch-JobInfoHeader-subtitle div',
          '.locationsContainer'
        ]),
        salary: this.getTextContent([
          '[data-testid="job-salary"]',
          '.salary-snippet',
          '.jobsearch-JobMetadataHeader-item'
        ]),
        jobType: this.getTextContent([
          '[data-testid="job-type-badge"]',
          '.jobsearch-JobMetadataHeader-item'
        ]),
        description: this.getHTML([
          '[data-testid="jobsearch-JobComponent-description"]',
          '.jobsearch-jobDescriptionText',
          '#jobDescriptionText'
        ]),
        applyUrl: this.getApplyButtonUrl(),
        postedDate: this.getTextContent([
          '.jobsearch-JobMetadataFooter',
          '.date'
        ]),
        jobId: this.extractJobId(window.location.href)
      };

      this.jobData = jobData;
      this.analyzeJobRequirements();
      this.sendToBackground('jobDataExtracted', jobData);
      
    } catch (error) {
      console.error('Error extracting job data:', error);
    }
  }

  getTextContent(selectors) {
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        return element.textContent.trim();
      }
    }
    return null;
  }

  getHTML(selectors) {
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        return element.innerHTML;
      }
    }
    return null;
  }

  getApplyButtonUrl() {
    const applyButton = document.querySelector('a[href*="/apply"]');
    return applyButton ? applyButton.href : null;
  }

  extractJobId(url) {
    const match = url.match(/jk=([a-zA-Z0-9]+)/);
    return match ? match[1] : null;
  }

  // Application Page Handler
  handleApplicationPage() {
    console.log('Application page detected');
    this.detectFormFields();
    this.setupAutoFill();
  }

  detectFormFields() {
    const formFields = {
      firstName: this.findField([
        'input[name*="firstName"]',
        'input[name*="first_name"]',
        'input[id*="firstName"]',
        'input[placeholder*="First name"]'
      ]),
      lastName: this.findField([
        'input[name*="lastName"]',
        'input[name*="last_name"]',
        'input[id*="lastName"]',
        'input[placeholder*="Last name"]'
      ]),
      email: this.findField([
        'input[type="email"]',
        'input[name*="email"]',
        'input[id*="email"]'
      ]),
      phone: this.findField([
        'input[type="tel"]',
        'input[name*="phone"]',
        'input[id*="phone"]'
      ]),
      resume: this.findField([
        'input[type="file"][accept*="pdf"]',
        'input[name*="resume"]',
        'input[id*="resume"]'
      ]),
      coverLetter: this.findField([
        'textarea[name*="cover"]',
        'textarea[id*="cover"]',
        'textarea[placeholder*="cover"]'
      ]),
      location: this.findField([
        'input[name*="location"]',
        'input[name*="city"]',
        'input[id*="location"]'
      ]),
      workAuth: this.findField([
        'select[name*="work_auth"]',
        'select[name*="authorization"]',
        'input[name*="authorized"]'
      ]),
      startDate: this.findField([
        'input[type="date"]',
        'input[name*="start"]',
        'select[name*="start"]'
      ])
    };

    this.formFields = formFields;
    this.highlightDetectedFields();
    this.sendToBackground('formFieldsDetected', formFields);
  }

  findField(selectors) {
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element && this.isVisible(element)) {
        return {
          element,
          selector,
          type: element.type || element.tagName.toLowerCase(),
          required: element.required || element.hasAttribute('required')
        };
      }
    }
    return null;
  }

  isVisible(element) {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && element.offsetParent !== null;
  }

  highlightDetectedFields() {
    Object.entries(this.formFields).forEach(([key, field]) => {
      if (field && field.element) {
        field.element.style.border = '2px solid #4CAF50';
        field.element.style.boxShadow = '0 0 5px rgba(76, 175, 80, 0.5)';
      }
    });
  }

  setupAutoFill() {
    if (!this.userProfile) {
      console.log('User profile not loaded, requesting from background');
      this.sendToBackground('getUserProfile');
      return;
    }

    this.createAutoFillControls();
  }

  createAutoFillControls() {
    const controlPanel = document.createElement('div');
    controlPanel.id = 'indeed-auto-fill-controls';
    controlPanel.innerHTML = `
      <div class="auto-fill-panel">
        <h3>Auto Fill Assistant</h3>
        <div class="controls">
          <button id="preview-fill" class="btn btn-primary">Preview Fill</button>
          <button id="auto-fill" class="btn btn-success">Auto Fill</button>
          <button id="submit-app" class="btn btn-warning" disabled>Submit Application</button>
        </div>
        <div class="status" id="fill-status"></div>
      </div>
    `;

    document.body.appendChild(controlPanel);
    this.attachControlEvents();
  }

  attachControlEvents() {
    document.getElementById('preview-fill').addEventListener('click', () => {
      this.previewAutoFill();
    });

    document.getElementById('auto-fill').addEventListener('click', () => {
      this.executeAutoFill();
    });

    document.getElementById('submit-app').addEventListener('click', () => {
      this.confirmAndSubmit();
    });
  }

  previewAutoFill() {
    const preview = {};
    
    Object.entries(this.formFields).forEach(([key, field]) => {
      if (field && this.userProfile) {
        preview[key] = this.getFieldValue(key, field);
      }
    });

    this.showPreviewModal(preview);
  }

  getFieldValue(fieldKey, field) {
    const profile = this.userProfile;
    
    switch (fieldKey) {
      case 'firstName':
        return profile.firstName;
      case 'lastName':
        return profile.lastName;
      case 'email':
        return profile.email;
      case 'phone':
        return profile.phone;
      case 'location':
        return profile.location;
      case 'workAuth':
        return profile.workAuthorization;
      case 'startDate':
        return profile.availableStartDate;
      case 'coverLetter':
        return this.generateCoverLetter();
      default:
        return '';
    }
  }

  executeAutoFill() {
    if (!this.formFields || !this.userProfile) {
      this.showStatus('Missing form fields or user profile', 'error');
      return;
    }

    let filledCount = 0;
    const errors = [];

    Object.entries(this.formFields).forEach(([key, field]) => {
      if (field && field.element) {
        try {
          const value = this.getFieldValue(key, field);
          if (value) {
            this.fillField(field.element, value);
            filledCount++;
          }
        } catch (error) {
          console.error(`Error filling field ${key}:`, error);
          errors.push(`${key}: ${error.message}`);
        }
      }
    });

    if (errors.length > 0) {
      this.showStatus(`Filled ${filledCount} fields with ${errors.length} errors`, 'warning');
    } else {
      this.showStatus(`Successfully filled ${filledCount} fields`, 'success');
      document.getElementById('submit-app').disabled = false;
    }
  }

  fillField(element, value) {
    // Handle different field types
    if (element.type === 'file') {
      // File upload requires special handling - will be done via local companion
      this.sendToBackground('uploadFile', { 
        selector: this.getElementSelector(element),
        filePath: value 
      });
      return;
    }

    // Clear existing value
    element.value = '';
    element.focus();

    // Trigger input events to ensure React/Vue reactivity
    if (element.type === 'select-one') {
      const option = Array.from(element.options).find(opt => 
        opt.value === value || opt.textContent.includes(value)
      );
      if (option) {
        element.value = option.value;
      }
    } else {
      // Simulate typing for better compatibility
      this.simulateTyping(element, value);
    }

    // Trigger change events
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.dispatchEvent(new Event('blur', { bubbles: true }));
  }

  simulateTyping(element, text) {
    // Split text and type character by character with small delays
    const chars = text.split('');
    let index = 0;

    const typeChar = () => {
      if (index < chars.length) {
        element.value += chars[index];
        element.dispatchEvent(new KeyboardEvent('keydown', { key: chars[index] }));
        element.dispatchEvent(new KeyboardEvent('keypress', { key: chars[index] }));
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new KeyboardEvent('keyup', { key: chars[index] }));
        index++;
        setTimeout(typeChar, Math.random() * 50 + 10); // Random delay 10-60ms
      }
    };

    typeChar();
  }

  confirmAndSubmit() {
    const confirmDialog = confirm(
      'Are you sure you want to submit this application? Please review all fields before confirming.'
    );

    if (confirmDialog) {
      this.submitApplication();
    }
  }

  submitApplication() {
    // Find submit button
    const submitButton = document.querySelector([
      'button[type="submit"]',
      'input[type="submit"]',
      'button[id*="submit"]',
      'button[class*="submit"]'
    ].join(', '));

    if (submitButton) {
      // Take screenshot before submission
      this.sendToBackground('takeScreenshot', { stage: 'before_submit' });
      
      submitButton.click();
      
      // Monitor for success/error
      setTimeout(() => {
        this.checkSubmissionResult();
      }, 2000);
    } else {
      this.showStatus('Submit button not found', 'error');
    }
  }

  checkSubmissionResult() {
    // Check for success indicators
    const successIndicators = [
      'Application submitted',
      'Thank you',
      'Application received',
      'Successfully submitted'
    ];

    const pageText = document.body.textContent.toLowerCase();
    const isSuccess = successIndicators.some(indicator => 
      pageText.includes(indicator.toLowerCase())
    );

    if (isSuccess) {
      this.sendToBackground('applicationSubmitted', {
        jobId: this.jobData?.jobId,
        success: true,
        timestamp: new Date().toISOString()
      });
      this.showStatus('Application submitted successfully!', 'success');
    } else {
      this.showStatus('Submission status unclear - please verify', 'warning');
    }
  }

  // Utility methods
  showStatus(message, type) {
    const statusEl = document.getElementById('fill-status');
    if (statusEl) {
      statusEl.textContent = message;
      statusEl.className = `status ${type}`;
    }
  }

  showPreviewModal(preview) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Auto Fill Preview</h3>
        <div class="preview-fields">
          ${Object.entries(preview).map(([key, value]) => 
            `<div class="field-preview">
              <label>${key}:</label>
              <span>${value || 'Not available'}</span>
            </div>`
          ).join('')}
        </div>
        <div class="modal-actions">
          <button id="confirm-fill" class="btn btn-success">Proceed with Auto Fill</button>
          <button id="cancel-fill" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('confirm-fill').addEventListener('click', () => {
      document.body.removeChild(modal);
      this.executeAutoFill();
    });

    document.getElementById('cancel-fill').addEventListener('click', () => {
      document.body.removeChild(modal);
    });
  }

  generateCoverLetter() {
    if (!this.jobData) return '';

    return `Dear Hiring Manager,

I am writing to express my interest in the ${this.jobData.title} position at ${this.jobData.company}. 

Based on the job description, I believe my experience aligns well with your requirements. I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my skills can benefit ${this.jobData.company}.

Thank you for your consideration.

Best regards,
${this.userProfile?.firstName} ${this.userProfile?.lastName}`;
  }

  getElementSelector(element) {
    if (element.id) return `#${element.id}`;
    if (element.name) return `[name="${element.name}"]`;
    
    // Generate CSS selector path
    const path = [];
    let current = element;
    
    while (current && current !== document.body) {
      let selector = current.tagName.toLowerCase();
      
      if (current.className) {
        selector += '.' + current.className.split(' ').join('.');
      }
      
      path.unshift(selector);
      current = current.parentElement;
    }
    
    return path.join(' > ');
  }

  analyzeJobRequirements() {
    if (!this.jobData?.description) return;

    // Extract key requirements and skills
    const description = this.jobData.description.toLowerCase();
    const commonSkills = [
      'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws',
      'docker', 'kubernetes', 'git', 'agile', 'scrum', 'rest api'
    ];

    const foundSkills = commonSkills.filter(skill => 
      description.includes(skill.toLowerCase())
    );

    this.jobData.requiredSkills = foundSkills;
    this.jobData.matchScore = this.calculateMatchScore(foundSkills);
  }

  calculateMatchScore(requiredSkills) {
    if (!this.userProfile?.skills) return 0;

    const userSkills = this.userProfile.skills.map(s => s.toLowerCase());
    const matches = requiredSkills.filter(skill => 
      userSkills.some(userSkill => userSkill.includes(skill))
    );

    return Math.round((matches.length / requiredSkills.length) * 100);
  }

  // Communication with background script
  sendToBackground(action, data = {}) {
    chrome.runtime.sendMessage({ action, data, domain: this.domain });
  }

  setupEventListeners() {
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.action) {
        case 'userProfileLoaded':
          this.userProfile = message.data;
          if (window.location.href.includes('/apply?')) {
            this.setupAutoFill();
          }
          break;
        case 'startAutoFill':
          this.executeAutoFill();
          break;
        case 'toggleAutomation':
          this.isActive = message.data.active;
          break;
      }
    });

    // Monitor for navigation changes
    let lastUrl = window.location.href;
    new MutationObserver(() => {
      if (window.location.href !== lastUrl) {
        lastUrl = window.location.href;
        setTimeout(() => this.detectPageType(), 1000);
      }
    }).observe(document.body, { childList: true, subtree: true });
  }

  loadUserProfile() {
    this.sendToBackground('getUserProfile');
  }

  showSidePanelButton() {
    // Create floating action button
    const fab = document.createElement('div');
    fab.id = 'indeed-automation-fab';
    fab.innerHTML = `
      <button class="fab-button" title="Open Auto Apply Assistant">
        🤖
      </button>
    `;
    document.body.appendChild(fab);

    fab.addEventListener('click', () => {
      this.sendToBackground('openSidePanel');
    });
  }

  injectSidePanel() {
    // This will be handled by the chrome.sidePanel API
    // Content script just needs to notify background
    this.sendToBackground('contentScriptReady');
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new IndeedAutomation());
} else {
  new IndeedAutomation();
}