// Playwright configuration for the wiki browser tests (tests/).
//
// The tests run against a locally built site: `make build && npm test`
// (CI builds the site first, see .github/workflows/wiki.yml). A small static
// server (tests/serve.js) serves public/ — no extra tooling needed.
//
// The Playwright-bundled Chromium is used by default; to use a system browser
// instead (skips the download), set CHROMIUM_PATH, e.g.
//   CHROMIUM_PATH=/usr/bin/chromium npm test

const { defineConfig } = require('@playwright/test');

const port = process.env.WIKI_TEST_PORT || '4173';

module.exports = defineConfig({
  testDir: 'tests',
  timeout: 180 * 1000,
  retries: 0,
  // The static server is stateless, so many workers can share one port.
  // Capped below Playwright's default (cores/2) because the mermaid suite is
  // CPU-heavy; override with -w <n> (e.g. `npx playwright test -w 16`).
  workers: 8,
  reporter: 'list',
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    launchOptions: process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {},
  },
  projects: [
    // The subpath project runs ONLY i18n-subpath.spec.js; the other projects
    // skip it (the rest of the suite is base-path-agnostic — it already
    // passes against the root build).
    { name: 'desktop', testMatch: '**/*.spec.js', testIgnore: 'i18n-subpath.spec.js', use: { viewport: { width: 1280, height: 720 } } },
    // Simulates the GitHub Pages project site: the same build served under
    // /wiki/ with deploy-style link rewrites + data-root (see
    // tests/setup-subpath.js).
    { name: 'subpath', testMatch: 'i18n-subpath.spec.js', use: { viewport: { width: 1280, height: 720 }, baseURL: `http://127.0.0.1:${port}/wiki` } },
    // phone-sized; isMobile/hasTouch emulate a real handset (viewport meta,
    // touch events). Mobile-only tests skip on the desktop project.
    {
      name: 'mobile',
      testMatch: '**/*.spec.js',
      testIgnore: 'i18n-subpath.spec.js',
      use: {
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 2,
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
  webServer: {
    // Build the /wiki subpath deploy fixture first (webServer starts before
    // globalSetup, so this must be part of the command chain).
    command: `node tests/setup-subpath.js && node tests/serve.js public ${port} .subpath-public`,
    url: `http://127.0.0.1:${port}/`,
    reuseExistingServer: true,
    // Generous: the command first builds the subpath fixture (~35s for the
    // ~21k-file public/ copy + rewrites) before the server binds.
    timeout: 120 * 1000,
  },
});
