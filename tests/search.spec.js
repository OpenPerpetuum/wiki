// Wiki search keyboard shortcuts: "/" (outside a text field), Ctrl+F and
// Cmd+F focus the search box; Esc blurs + clears it.
const { test, expect } = require('@playwright/test');

test.describe('search keyboard shortcuts', () => {
  test('placeholder hints at all three shortcuts', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await expect(page.locator('#wiki-search'))
      .toHaveAttribute('placeholder', /\/ or Ctrl\+F or Cmd\+F/);
  });

  test('bare / focuses the search box', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.keyboard.press('/');
    await expect(page.locator('#wiki-search')).toBeFocused();
  });

  test('Ctrl+F focuses the search box', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.keyboard.press('Control+f');
    await expect(page.locator('#wiki-search')).toBeFocused();
  });

  test('a second / is typed into the focused box, not re-triggered', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.keyboard.press('/');
    await expect(page.locator('#wiki-search')).toBeFocused();
    await page.keyboard.press('/');
    await expect(page.locator('#wiki-search')).toHaveValue('/');
  });

  test('Esc blurs and clears the search box', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.keyboard.press('/');
    await page.locator('#wiki-search').fill('mech');
    await page.keyboard.press('Escape');
    await expect(page.locator('#wiki-search')).not.toBeFocused();
    await expect(page.locator('#wiki-search')).toHaveValue('');
  });
});

test.describe('search: menu tree + keyboard result navigation', () => {
  // Wait until the URL ends with a site-absolute path (as in a result href).
  async function waitForPath(page, path) {
    const esc = path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    await page.waitForURL(new RegExp(esc + '$'));
  }

  async function typeAndAwait(page, baseURL, q) {
    await page.goto(`${baseURL}/`);
    await page.locator('#wiki-search').fill(q);
    await expect(page.locator('#search-results')).toBeVisible();
    await expect(page.locator('#search-results a').first()).toBeVisible();
  }

  test('the World map page title is translated in results (fr: Carte du monde)', async ({ page, baseURL }) => {
    // The search index holds the English title "World Map"; the menu label
    // nav_world ("World Map"/"Carte du monde") matches, so the result row
    // shows the translated form on the French page.
    await page.goto(`${baseURL}/`);
    await page.evaluate(() => localStorage.setItem('wiki-lang', 'fr'));
    await page.goto(`${baseURL}/`);
    await page.locator('#wiki-search').fill('monde');
    await expect(page.locator('#search-results')).toBeVisible();
    const link = page.locator('#search-results a[href="/zones/map/"]');
    await expect(link).toBeVisible();
    await expect(link).toContainText('Carte du monde');
    // the English title must not appear on the French page
    await expect(link).not.toContainText('World');
  });

  test('menu labels find their pages (label differs from the page title)', async ({ page, baseURL }) => {
    // Sidenav label "Robot stat tables" (nav_content_robots) vs page title "Robots":
    // typing the menu label must still surface /content/robots/.
    await typeAndAwait(page, baseURL, 'stat tables');
    const link = page.locator('#search-results a[href="/content/robots/"]');
    await expect(link).toBeVisible();
    await link.click();
    await page.waitForURL('**/content/robots/');
  });

  test('sidenav anchor links are their own results and keep the fragment', async ({ page, baseURL }) => {
    // "Mobile teleports" (nav_dep_mobile_tp) → /content/deployables/#mobile-teleports-12.
    // The label is a menu-only string (the page title is "Deployables"), so
    // the anchor entry is the top hit; the page itself follows.
    await typeAndAwait(page, baseURL, 'mobile teleports');
    const link = page.locator('#search-results a[href="/content/deployables/#mobile-teleports-12"]');
    await expect(link).toBeVisible();
    await expect(link).toContainText('Mobile teleports');
    await link.click();
    await page.waitForURL('**/content/deployables/#mobile-teleports-12');
  });

  test('arrow keys move the selection, Enter follows it', async ({ page, baseURL }) => {
    await typeAndAwait(page, baseURL, 'zone');
    const links = page.locator('#search-results a');
    expect(await links.count()).toBeGreaterThanOrEqual(3);
    // top result is selected by default
    await expect(links.nth(0)).toHaveClass(/sel/);
    await expect(links.nth(0)).toHaveAttribute('aria-selected', 'true');
    await expect(page.locator('#wiki-search')).toHaveAttribute('aria-activedescendant', 'wiki-search-opt-0');

    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowDown');
    await expect(links.nth(2)).toHaveClass(/sel/);
    await expect(links.nth(2)).toHaveAttribute('aria-selected', 'true');
    await expect(page.locator('#wiki-search')).toHaveAttribute('aria-activedescendant', 'wiki-search-opt-2');

    // ArrowUp back, then Home
    await page.keyboard.press('ArrowUp');
    await expect(links.nth(1)).toHaveAttribute('aria-selected', 'true');
    await page.keyboard.press('Home');
    await expect(links.nth(0)).toHaveAttribute('aria-selected', 'true');

    // End jumps to the last result, Enter navigates there
    await page.keyboard.press('End');
    const last = await links.count() - 1;
    await expect(links.nth(last)).toHaveAttribute('aria-selected', 'true');
    const target = await links.nth(last).getAttribute('href');
    await page.keyboard.press('Enter');
    await waitForPath(page, target);
  });

  test('selection is clamped at both ends', async ({ page, baseURL }) => {
    await typeAndAwait(page, baseURL, 'zone');
    const links = page.locator('#search-results a');
    const n = await links.count();
    await page.keyboard.press('ArrowUp'); // already at 0 → stays
    await expect(links.nth(0)).toHaveAttribute('aria-selected', 'true');
    for (let i = 0; i < n + 3; i++) await page.keyboard.press('ArrowDown');
    await expect(links.nth(n - 1)).toHaveAttribute('aria-selected', 'true');
  });

  test('mouse hover syncs with the keyboard selection', async ({ page, baseURL }) => {
    await typeAndAwait(page, baseURL, 'zone');
    const links = page.locator('#search-results a');
    expect(await links.count()).toBeGreaterThanOrEqual(2);
    await links.nth(1).hover();
    await expect(links.nth(1)).toHaveAttribute('aria-selected', 'true');
    await expect(page.locator('#wiki-search')).toHaveAttribute('aria-activedescendant', 'wiki-search-opt-1');
    // Enter now follows the hovered (selected) result
    const target = await links.nth(1).getAttribute('href');
    await page.keyboard.press('Enter');
    await waitForPath(page, target);
  });
});
