import 'dotenv/config';
import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// require('dotenv').config();

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  timeout: 12 * 1000,
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [ ['html', { open: 'never' }] ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',
    browserName: "chromium",
    viewport: { width: 1280, height: 900 },
    ignoreHTTPSErrors: true,
    permissions: ['microphone'],
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    launchOptions: {
      ignoreDefaultArgs: ['--mute-audio'],
      args: [
        "--use-fake-device-for-media-stream",
        "--use-fake-ui-for-media-stream",
      ],
    }
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      // grepInvert: /mobile/,
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 900 },
      },
    },

    {
      name: 'firefox',
      // grepInvert: /mobile/,
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      // grepInvert: /mobile/,
      use: { ...devices['Desktop Safari'] },
    },

    // Test against mobile viewports. 
    {
      name: 'MobileChrome',
      // grep: /mobile/,
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'MobileSafari',
      // grep: /mobile/,
      use: { ...devices['iPhone 12'] },
    },

    /*
    // Test against branded browsers.
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    }*/
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://127.0.0.1:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
