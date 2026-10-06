// i18n: UI chrome language switching + content navigation.
// The language toggle:
//   - Swaps chrome strings (nav, topbar, search, footer) at runtime
//   - Navigates to the translated page if one exists (e.g. / → /fr/)
//   - Stays on the current page (chrome-only swap) if no translation exists
const { test, expect } = require('@playwright/test');

test.describe('i18n language switcher', () => {
  async function clearLang(page) {
    await page.evaluate(() => localStorage.removeItem('wiki-lang'));
  }

  test('defaults to English on first visit', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await clearLang(page);
    await page.reload();
    await expect(page.locator('.nav-quick a')).toContainText('Home');
    await expect(page.locator('.nav-group-link[href="/menu/start/"]')).toContainText('Start');
    await expect(page.locator('.nav-group-link[href="/zones/map/"]')).toContainText('World');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Search the wiki/);
  });

  test('switching to French on a page WITH a translation navigates', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await clearLang(page);
    await page.reload();
    // Click the language toggle → French
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    // Navigated to /fr/ (the French home page exists)
    await page.waitForURL('**/fr/');
    // French chrome is active
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Rechercher/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
  });

  test('switching to French on a page WITHOUT a translation swaps chrome only', async ({ page, baseURL }) => {
    // /content/items/titanium/ is a generated page with no French equivalent
    await page.goto(`${baseURL}/content/items/titanium/`);
    await clearLang(page);
    await page.reload();
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    // Stayed on the same page (no /fr/ navigation)
    await page.waitForTimeout(300);
    expect(page.url()).not.toMatch(/\/fr\//);
    // But the chrome is French
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    await expect(page.locator('.nav-group-link[href="/zones/map/"]')).toContainText('Monde');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Rechercher/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
    // Content is still English
    await expect(page.locator('h1')).toContainText('Titanium');
  });

  test('switching back to English from a French page navigates', async ({ page, baseURL }) => {
    // Go directly to the French home page
    await page.goto(`${baseURL}/fr/`);
    await page.evaluate(() => localStorage.setItem('wiki-lang', 'fr'));
    await page.reload();
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    // Switch back to English (navigates to /)
    const navPromise = page.waitForNavigation({ waitUntil: 'domcontentloaded' });
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="en"]').click();
    await navPromise;
    await expect(page.locator('.nav-quick a')).toContainText('Home');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Search the wiki/);
  });

  test('language preference persists across page loads', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/features/getting-started/`);
    await clearLang(page);
    await page.reload();
    // Switch to French (chrome-only, no nav)
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    await page.waitForTimeout(300);
    // Navigate to another page (no French equivalent)
    await page.goto(`${baseURL}/features/faq/`);
    // French chrome is still active
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Rechercher/);
  });

  test('WIKI_UI object updates with language', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/features/getting-started/`);
    await clearLang(page);
    await page.reload();
    expect(await page.evaluate(() => window.WIKI_UI.searchNoResults)).toBe('No pages match');
    // Switch to French (chrome-only on this page)
    await page.evaluate(() => window.WIKI_applyLang('fr'));
    expect(await page.evaluate(() => window.WIKI_UI.searchNoResults)).toBe('Aucune page correspondante');
  });

  test('aria-labels update with language', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/features/getting-started/`);
    await page.evaluate(() => window.WIKI_applyLang('fr'));
    await expect(page.locator('#lang-toggle')).toHaveAttribute('aria-label', /Choisir la langue/);
    await expect(page.locator('#theme-toggle')).toHaveAttribute('aria-label', /clair.sombre/);
  });

  test('lang menu shows all available languages', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.locator('#lang-toggle').click();
    const en = page.locator('#lang-menu button[data-lang="en"]');
    const fr = page.locator('#lang-menu button[data-lang="fr"]');
    await expect(en).toHaveText(/EN/);
    await expect(fr).toHaveText(/FR/);
    await expect(en).toHaveAttribute('aria-pressed', 'true');
    await expect(fr).toHaveAttribute('aria-pressed', 'false');
  });
});
