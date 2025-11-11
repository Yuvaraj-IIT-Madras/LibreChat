import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: 'specs/',
  outputDir: 'specs/.test-results',
  
  /* Run tests serially (not in parallel) */
  fullyParallel: false,
  workers: 1,
  
  /* Reporter configurations */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }],
    ['list'], // Console output
  ],
  
  /* Shared settings for all tests */
  use: {
    baseURL: 'http://localhost:3080',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    actionTimeout: 10000,
  },
  
  timeout: 30000,
  expect: { timeout: 10000 },
  
  /* Browser configurations */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  
  /* Web server configuration (already running in Docker) */
  webServer: {
    command: '',
    reuseExistingServer: true,
    url: 'http://localhost:3080',
  },
  
  /* Global timeout for all tests */
  globalTimeout: 5 * 60 * 1000, // 5 minutes
});
