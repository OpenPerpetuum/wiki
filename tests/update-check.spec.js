// update-check.js: while a page is open, the site re-fetches the current
// page (no-store) and compares the pristine <main> against a snapshot
// taken while the document was still parsing. A difference means the site
// was redeployed → a toast appears, bottom right; clicking it reloads.
const { test, expect } = require('@playwright/test');

const PAGE = '/features/items/';

// make the server pretend the deployed page changed: the initial navigation
// passes through untouched, every later fetch (the checker's no-store
// re-fetch) gets a modified <main>. The route is installed BEFORE navigation:
// the checker's first re-fetch fires ~2 s after the script parses (before
// 'load'), so installing it afterwards would race the page load on slow
// runners — a clean first check then throttles the next one ~60 s out, past
// the test's timeout. (sec-fetch-dest cannot be used to tell the requests
// apart: it is not populated on Playwright-intercepted requests.)
async function pretendRedeploy(page, baseURL) {
  let first = true;
  await page.route(`${baseURL}${PAGE}`, async (route) => {
    if (first) { first = false; return route.continue(); }
    const response = await route.fetch();
    const html = (await response.text()).replace('</main>', '<p data-deployed="newer">x</p></main>');
    return route.fulfill({ response, body: html });
  });
}

test('no toast when the deployed page is unchanged', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}${PAGE}`, { waitUntil: 'load' });
  // the first check runs ~2 s after load
  await page.waitForTimeout(4000);
  expect(await page.locator('.update-toast').count()).toBe(0);
});

test('toast appears when the deployed page changed, and clicking it refreshes', async ({ page, baseURL, context }) => {
  await pretendRedeploy(page, baseURL);
  await page.goto(`${baseURL}${PAGE}`, { waitUntil: 'load' });

  const toast = page.locator('.update-toast');
  await toast.waitFor({ state: 'visible', timeout: 15000 });
  expect((await toast.textContent()).toLowerCase()).toContain('a new update is available');

  // clicking reloads; once the loaded page matches the deployment again,
  // the toast goes away
  await toast.click();
  await page.waitForLoadState('load');
  await context.unroute(`${baseURL}${PAGE}`);
  await page.waitForTimeout(4000);
  expect(await page.locator('.update-toast').count()).toBe(0);
});
