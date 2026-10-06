// i18n: UI chrome language switching.
// The language toggle switches the nav/topbar/search/footer strings
// at runtime (no page reload). Content stays in the default language.
const { test, expect } = require('@playwright/test');

test.describe('i18n language switcher', () => {
  // Helper: clear the saved language on the current page context.
  async function clearLang(page) {
    await page.evaluate(() => localStorage.removeItem('wiki-lang'));
  }

  test('defaults to English on first visit', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await clearLang(page);
    await page.reload();
    // Nav shows English
    await expect(page.locator('.nav-quick a')).toContainText('Home');
    await expect(page.locator('.nav-group-link[href="/menu/start/"]')).toContainText('Start');
    await expect(page.locator('.nav-group-link[href="/zones/map/"]')).toContainText('World');
    // Search placeholder is English
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Search the wiki/);
  });

  test('switching to French translates the chrome', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    // Click the language toggle
    await page.locator('#lang-toggle').click();
    // Click French
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    // Nav is now French
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    await expect(page.locator('.nav-group-link[href="/menu/start/"]')).toContainText('Démarrer');
    await expect(page.locator('.nav-group-link[href="/zones/map/"]')).toContainText('Monde');
    await expect(page.locator('.nav-group-link[href="/menu/play/"]')).toContainText('Jouer');
    await expect(page.locator('.nav-group-link[href="/menu/systems/"]')).toContainText('Systèmes');
    // Search placeholder is French
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Rechercher/);
    // Mode toggle is French
    await expect(page.locator('.mode-opt[data-mode-opt="play"]')).toContainText('Jouer');
    // html lang attribute updated
    await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
    // Content is STILL English (Phase 1: chrome only)
    await expect(page.locator('h1')).toContainText('Open Perpetuum');
  });

  test('switching back to English restores the chrome', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    // Switch back
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="en"]').click();
    await expect(page.locator('.nav-quick a')).toContainText('Home');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Search the wiki/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });

  test('language preference persists across page loads', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await clearLang(page);
    await page.reload();
    // Switch to French
    await page.locator('#lang-toggle').click();
    await page.locator('#lang-menu button[data-lang="fr"]').click();
    // Navigate to another page (full page load)
    await page.goto(`${baseURL}/features/faq/`);
    // French is still active (restored from localStorage on load)
    await expect(page.locator('.nav-quick a')).toContainText('Accueil');
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Rechercher/);
  });

  test('WIKI_UI object updates with language', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    // English defaults
    let ui = await page.evaluate(() => window.WIKI_UI.searchNoResults);
    expect(ui).toBe('No pages match');
    // Switch to French
    await page.evaluate(() => window.WIKI_setLang('fr'));
    ui = await page.evaluate(() => window.WIKI_UI.searchNoResults);
    expect(ui).toBe('Aucune page correspondante');
  });

  test('aria-labels update with language', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.evaluate(() => window.WIKI_setLang('fr'));
    await expect(page.locator('#lang-toggle')).toHaveAttribute('aria-label', /Choisir la langue/);
    await expect(page.locator('#theme-toggle')).toHaveAttribute('aria-label', /clair.sombre/);
  });

  test('lang menu shows both languages with correct active state', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.locator('#lang-toggle').click();
    const en = page.locator('#lang-menu button[data-lang="en"]');
    const fr = page.locator('#lang-menu button[data-lang="fr"]');
    await expect(en).toHaveText(/EN/);
    await expect(fr).toHaveText(/FR/);
    // English is active by default
    await expect(en).toHaveAttribute('aria-pressed', 'true');
    await expect(fr).toHaveAttribute('aria-pressed', 'false');
    // Switch to French
    await fr.click();
    await expect(fr).toHaveAttribute('aria-pressed', 'true');
  });
});
