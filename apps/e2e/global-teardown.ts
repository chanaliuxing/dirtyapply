import { FullConfig } from '@playwright/test';

/**
 * Global teardown for E2E tests
 * Cleanup test environment
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up E2E test environment...');
  
  // Cleanup any test data, temporary files, etc.
  // Services will be stopped by webServer configuration
  
  console.log('✅ E2E test environment cleanup completed');
}

export default globalTeardown;