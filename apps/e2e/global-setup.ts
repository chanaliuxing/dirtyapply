import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for E2E tests
 * Prepares test environment and validates services
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test environment setup...');
  
  // Validate that required services are running
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Check API health
    console.log('📡 Checking API service...');
    await page.goto('http://localhost:8000/health');
    const apiHealth = await page.textContent('body');
    if (!apiHealth?.includes('healthy')) {
      throw new Error('API service not healthy');
    }
    
    // Check Mock ATS service
    console.log('🎭 Checking Mock ATS service...');
    await page.goto('http://localhost:3000/health');
    // Mock ATS might not have health endpoint, so just check if it loads
    
    // Check Companion service
    console.log('🤖 Checking Companion service...');
    await page.goto('http://localhost:8765/health');
    const companionHealth = await page.textContent('body');
    if (!companionHealth?.includes('healthy')) {
      throw new Error('Companion service not healthy');
    }
    
    console.log('✅ All services are running and healthy');
    
  } catch (error) {
    console.error('❌ Service health check failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;