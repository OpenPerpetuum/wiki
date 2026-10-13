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
    await expect(page.locator('.nav-group-link[href*="/zones/map/"]')).toContainText('Monde');
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

  test('translated home page has rich HTML cards', async ({ page, baseURL }) => {
    // Check that a translated home page (French) has the same card structure as English
    await page.goto(`${baseURL}/fr/`);
    
    // World map card
    const mapCard = page.locator('.home-card-map');
    await expect(mapCard).toBeVisible();
    await expect(mapCard).toHaveAttribute('href', '/fr/zones/map/');
    
    // Hero cards (robots + fitting)
    const heroCards = page.locator('.home-card-hero');
    expect(await heroCards.count()).toBe(2);
    
    // Feature cards
    const allCards = page.locator('.home-card');
    expect(await allCards.count()).toBeGreaterThanOrEqual(10);
    
    // Cards have data-i18n attributes for translation
    const i18nCards = page.locator('[data-i18n^="home_"]');
    expect(await i18nCards.count()).toBeGreaterThanOrEqual(10);
    
    // World map thumbnail image
    const mapImg = mapCard.locator('img');
    await expect(mapImg).toHaveAttribute('src', '/world-map-thumb.png');
  });

  test('nav links are rewritten to include language prefix', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/fr/features/combat/`);
    await page.waitForTimeout(500);

    // Home link should point to /fr/
    const homeLink = page.locator('.nav-quick a');
    await expect(homeLink).toHaveAttribute('href', '/fr/');

    // Translated nav links should have the /fr/ prefix
    const gettingStarted = page.locator('.nav-items a[href*="getting-started"]');
    await expect(gettingStarted).toHaveAttribute('href', '/fr/features/getting-started/');

    // Translated zone nav links should have the /fr/ prefix
    const zoneLink = page.locator('.nav-items a[href*="/zones/"]').first();
    const zoneHref = await zoneLink.getAttribute('href');
    expect(zoneHref).toMatch(/^\/fr\//);

    // Untranslated links (items) should NOT be prefixed
    await page.goto(`${baseURL}/fr/features/production/`);
    await page.waitForTimeout(500);
    const itemLink = page.locator('article a[href*="/content/items/"]').first();
    const itemHref = await itemLink.getAttribute('href');
    expect(itemHref).not.toMatch(/^\/fr\//);
  });

  test('no flash of English on translated pages (data-i18n-pending)', async ({ page, baseURL }) => {
    // Intercept the page to check the pending attribute is set before i18n.js runs
    await page.goto(`${baseURL}/fr/features/combat/`);

    // After full load, the pending attribute should be REMOVED (translation applied)
    const pending = await page.evaluate(() =>
        document.documentElement.hasAttribute('data-i18n-pending')
    );
    expect(pending).toBe(false);

    // The lang attribute should be set to 'fr'
    const lang = await page.evaluate(() =>
        document.documentElement.getAttribute('lang')
    );
    expect(lang).toBe('fr');

    // Chrome text should be in French (not English)
    const homeLabel = await page.locator('.nav-quick a span[data-i18n="nav_home"]').textContent();
    expect(homeLabel).not.toBe('Home');
  });

  test('on Russian home page, clicking Start (СТАРТ) navigates to /ru/menu/start/', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/ru/`);
    await page.waitForTimeout(300);

    const toggle = page.locator('#sidenav-toggle');
    if (await toggle.isVisible()) {
      await toggle.click();
      await page.waitForTimeout(200);
    }

    // Start nav group link should point to /ru/menu/start/
    const startLink = page.locator('.nav-group-link[href*="start"]');
    await expect(startLink).toHaveAttribute('href', '/ru/menu/start/');
    await expect(startLink).toContainText('Старт');

    // Click Start
    await startLink.click();
    await page.waitForURL('**/ru/menu/start/');
    await expect(page.locator('h1')).toContainText('Начало игры');
  });

  test('on English home page with Russian saved in localStorage, clicking Start navigates to /ru/menu/start/', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/`);
    await page.evaluate(() => localStorage.setItem('wiki-lang', 'ru'));
    await page.reload();
    await page.waitForTimeout(300);

    const toggle = page.locator('#sidenav-toggle');
    if (await toggle.isVisible()) {
      await toggle.click();
      await page.waitForTimeout(200);
    }

    const startLink = page.locator('.nav-group-link[href*="start"]');
    await expect(startLink).toHaveAttribute('href', '/ru/menu/start/');
    await startLink.click();
    await page.waitForURL('**/ru/menu/start/');
    await expect(page.locator('h1')).toContainText('Начало игры');
  });

  test('header and footer are translated on Russian page', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/ru/`);
    await page.waitForTimeout(300);

    // Header elements
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Поиск по вики/);
    await expect(page.locator('#lang-toggle')).toHaveAttribute('aria-label', /Выбрать язык/);
    await expect(page.locator('#palette-toggle')).toHaveAttribute('aria-label', /Выбрать цвет акцента/);
    await expect(page.locator('#theme-toggle')).toHaveAttribute('aria-label', /Переключить светлую/);
    await expect(page.locator('.mode-opt[data-mode-opt="play"]')).toHaveText('Играть');

    // Footer elements
    const footHome = page.locator('.footnav a[data-i18n="foot_home"]');
    const footFeatures = page.locator('.footnav a[data-i18n="foot_features"]');
    const footContent = page.locator('.footnav a[data-i18n="foot_content"]');
    const footZones = page.locator('.footnav a[data-i18n="foot_zones"]');

    await expect(footHome).toHaveText('Главная');
    await expect(footFeatures).toHaveText('Возможности');
    await expect(footFeatures).toHaveAttribute('href', '/ru/features/');
    await expect(footContent).toHaveText('Контент');
    await expect(footZones).toHaveText('Зоны');

    await expect(page.locator('.footcredit [data-i18n-html="foot_credit"]')).toContainText('Вики Open Perpetuum');
    await expect(page.locator('.footcredit [data-i18n-html="foot_attribution"]')).toContainText('Контент вики лицензирован');
  });

  test('header and footer are translated on German page', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/de/`);
    await page.waitForTimeout(300);

    // Header elements
    await expect(page.locator('#wiki-search')).toHaveAttribute('placeholder', /Wiki durchsuchen/);
    await expect(page.locator('#lang-toggle')).toHaveAttribute('aria-label', /Sprache wählen/);
    await expect(page.locator('#palette-toggle')).toHaveAttribute('aria-label', /Akzentfarbe wählen/);
    await expect(page.locator('.mode-opt[data-mode-opt="play"]')).toHaveText('Spielen');

    // Footer elements
    const footHome = page.locator('.footnav a[data-i18n="foot_home"]');
    const footFeatures = page.locator('.footnav a[data-i18n="foot_features"]');
    const footContent = page.locator('.footnav a[data-i18n="foot_content"]');
    const footZones = page.locator('.footnav a[data-i18n="foot_zones"]');

    await expect(footHome).toHaveText('Startseite');
    await expect(footFeatures).toHaveText('Funktionen');
    await expect(footFeatures).toHaveAttribute('href', '/de/features/');
    await expect(footContent).toHaveText('Inhalte');
    await expect(footZones).toHaveText('Zonen');

    await expect(page.locator('.footcredit [data-i18n-html="foot_credit"]')).toContainText('Open Perpetuum Wiki — generiert mit');
    await expect(page.locator('.footcredit [data-i18n-html="foot_attribution"]')).toContainText('Wiki-Inhalte sind unter der Apache License 2.0');
  });
});
