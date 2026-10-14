// Shortcuts window (? key): a dialog inside the content area listing the
// wiki's keyboard shortcuts. Two-column grid when it fits, one column on
// narrow screens. Closes on Esc, the ✕ button, or a click outside.

const { test, expect } = require('@playwright/test');

const PANEL = '#shortcuts-panel';
const BACKDROP = '#shortcuts-backdrop';

// Playwright gives each test a fresh browser context, so localStorage
// (wiki-mode / wiki-lang) can not leak between tests.

test('? opens the shortcuts window inside the content area', async ({ page }) => {
  await page.goto('/');
  expect(await page.locator(PANEL).isVisible()).toBe(false);
  await page.keyboard.press('?');
  await expect(page.locator(PANEL)).toBeVisible();
  await expect(page.locator(BACKDROP)).toBeVisible();
  // a real dialog with a title + close button
  await expect(page.locator('#shortcuts-title')).toHaveText('Shortcuts');
  expect(await page.locator(PANEL).getAttribute('role')).toBe('dialog');
  // it sits INSIDE the content area (right of the sidenav on desktop)
  const inContent = await page.evaluate(() => {
    const p = document.querySelector('#shortcuts-panel').getBoundingClientRect();
    const c = document.querySelector('.content-col').getBoundingClientRect();
    return p.left >= c.left - 1 && p.right <= c.right + 1
        && p.top >= c.top - 1 && p.bottom <= c.bottom + 1;
  });
  expect(inContent).toBe(true);
});

test('? shows the shortcut rows with key caps (7 rows)', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  // read everything in one round-trip (one CDP call is far less likely to
  // hit a transient session hiccup than a dozen sequential locator calls)
  const rows = await page.evaluate(() =>
      [...document.querySelectorAll('.shortcuts-grid li')].map((li) => ({
        keys: li.querySelector('.sc-keys').textContent.trim(),
        kbds: [...li.querySelectorAll('kbd')].map((k) => k.textContent),
        desc: li.querySelector('span[data-i18n]').textContent.trim(),
      })));
  expect(rows).toHaveLength(7);
  // every row: key caps on the left, a description on the right
  for (const r of rows) {
    expect(r.kbds.length).toBeGreaterThanOrEqual(1);
    expect(r.desc.length).toBeGreaterThan(3);
  }
  // the "/" row (focus the search) is first
  expect(rows[0].kbds[0]).toBe('/');
});

test('the grid is two-column on desktop and one-column on mobile', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  const cols = await page.evaluate(() =>
      getComputedStyle(document.querySelector('.shortcuts-grid')).gridTemplateColumns.split(' ').length);
  if (page.viewportSize().width > 500) {
    expect(cols).toBe(2); // desktop: two columns when it fits
  } else {
    expect(cols).toBe(1); // narrow phone: one column
  }
});

test('Esc closes the window', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  await expect(page.locator(PANEL)).toBeVisible();
  await page.keyboard.press('Escape');
  expect(await page.locator(PANEL).isVisible()).toBe(false);
  expect(await page.locator(BACKDROP).isVisible()).toBe(false);
});

test('the ✕ button closes the window', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  await expect(page.locator(PANEL)).toBeVisible();
  await page.click('#shortcuts-close');
  expect(await page.locator(PANEL).isVisible()).toBe(false);
});

test('clicking outside (the backdrop) closes the window', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  await expect(page.locator(PANEL)).toBeVisible();
  // click the dimmed backdrop, far away from the panel
  await page.mouse.click(8, 8);
  expect(await page.locator(PANEL).isVisible()).toBe(false);
});

test('? toggles: pressing it again closes the window', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  await expect(page.locator(PANEL)).toBeVisible();
  await page.keyboard.press('Shift+?');
  expect(await page.locator(PANEL).isVisible()).toBe(false);
});

test('? does not open the window while typing in the search box', async ({ page }) => {
  await page.goto('/');
  await page.click('#wiki-search');
  await page.keyboard.type('?');
  expect(await page.locator(PANEL).isVisible()).toBe(false);
  // the character went into the search box
  await expect(page.locator('#wiki-search')).toHaveValue('?');
});

test('the window follows the page language', async ({ page }) => {
  // on a French page the chrome (incl. the shortcuts window) is French
  await page.goto('/fr/');
  await page.keyboard.press('?');
  await expect(page.locator('#shortcuts-title')).toHaveText('Raccourcis');
  await expect(page.locator('.shortcuts-grid li').first().locator('span[data-i18n]')).toContainText('recherche');
});

test('the window is styled like the chrome (border + panel background)', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('?');
  const style = await page.evaluate(() => {
    const s = getComputedStyle(document.querySelector('#shortcuts-panel'));
    return { border: s.borderTopWidth, radius: s.borderRadius };
  });
  expect(style.border).toBe('1px');
  expect(style.radius).not.toBe('0px');
});
