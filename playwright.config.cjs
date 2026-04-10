/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  testDir: "./e2e",
  timeout: 180_000,
  expect: {
    timeout: 20_000,
  },
  use: {
    headless: false,
    viewport: { width: 1366, height: 900 },
    launchOptions: {
      slowMo: 220,
    },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  reporter: "list",
  workers: 1,
};
