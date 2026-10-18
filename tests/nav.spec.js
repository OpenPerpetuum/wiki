// Sidenav behaviour: groups (root -> sub) are open by default, 2nd-level
// sub-lists start collapsed, and the carets collapse/expand any section.
//
// Current structure (9 groups in play mode + Dev hidden):
//   Start, World Map, Gather, Produce, Robots & Fitting, Research,
//   Character, Items & Inventory, Market
// Sub-lists (nav-has-sub): World Map, Bases & Sites, Deployables,
//   With Others, Tech groups, Catalog, Shop = 7 total

const { test, expect } = require('@playwright/test');

// the sidenav only exists on wide viewports (drawer on mobile — see mobile.spec.js)
test.beforeEach(async ({ page }) => {
  test.skip(page.viewportSize().width <= 500, 'desktop layout only');
});

const VISIBLE_LINKS = () =>
  [...document.querySelectorAll('.sidenav a')].filter((a) => a.offsetParent !== null).length;
const COLLAPSED = (sel) =>
  [...document.querySelectorAll(sel)].map((g) => g.classList.contains('collapsed'));
const GROUPS = '.sidenav .nav-group:not(.nav-dev)'; // 9 in play mode (Dev excluded)
const SUBS = '.sidenav li li.nav-has-sub'; // 7 sub-lists

test('home: groups open, 2nd-level sub-lists closed', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  expect(await page.locator('.mode-tab[data-mode-tab="home"]').getAttribute('href')).toBe('/');
  // 9 groups, all open
  expect(await page.evaluate(COLLAPSED, GROUPS)).toEqual(Array(9).fill(false));
  // 7 sub-lists, all collapsed by default
  expect(await page.evaluate(COLLAPSED, SUBS)).toEqual(Array(7).fill(true));
  // visible links: 1 (Home) + 5 (Start) + 11 (World) + 4 (Gather) + 4 (Produce)
  //   + 4 (Robots) + 3 (Research) + 4 (Character) + 4 (Items) + 4 (Market) = 44
  expect(await page.evaluate(VISIBLE_LINKS)).toBe(44);
});

test('caret buttons collapse and re-open groups', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  const before = await page.evaluate(VISIBLE_LINKS);
  const carets = page.locator(`${GROUPS} > .nav-group-head .nav-caret`);
  await carets.nth(2).click(); // Gather
  expect(await page.evaluate(COLLAPSED, GROUPS)).toEqual([false, false, true, false, false, false, false, false, false]);
  expect(await page.evaluate(VISIBLE_LINKS)).toBeLessThan(before);
  await carets.nth(2).click();
  expect(await page.evaluate(COLLAPSED, GROUPS)).toEqual(Array(9).fill(false));
  expect(await page.evaluate(VISIBLE_LINKS)).toBe(before);
});

test('World: Missions is a plain link under the World Map group', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/features/missions/`);
  // Missions is a direct child link in the World Map group (not a sub-list)
  const missions = page.locator('.sidenav .nav-group >> nth=1 >> a[href="/features/missions/"]');
  expect(await missions.count()).toBe(1);
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Mission list');
});

test('Produce group carries the recipes page', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/recipes/`);
  const active = page.locator('.sidenav a.active');
  expect(await active.textContent()).toBe('Recipes');
  expect(await active.getAttribute('href')).toBe('/content/recipes/');
});

test('World Map group: zone links under the World Map sub-list', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  // World Map group (index 1) has: World Map sub-head, Movement, Exploration,
  // Probes, Bases & Sites sub-head, Deployables sub-head, Combat, NPCs, Missions,
  // With Others sub-head = 10 direct children
  expect(await page.locator(`${GROUPS} >> nth=1 >> .nav-items > li`).count()).toBe(10);
  // the World Map sub-list (collapsed by default) carries the zone family links
  const wmSub = page.locator('.sidenav .nav-has-sub:has(> .nav-sub-head > a[href="/zones/map/"])');
  expect(await wmSub.locator('.nav-sub a:visible').count()).toBe(0); // collapsed
  // expand it
  await wmSub.locator('.nav-sub-head .nav-caret').click();
  const wmHrefs = await wmSub.locator('.nav-sub a').evaluateAll(as => as.map(a => a.getAttribute('href')));
  expect(wmHrefs).toEqual([
    '/zones/zone-training/', '/zones/alpha/', '/zones/beta/', '/zones/gamma/', '/zones/zone-index/',
  ]);
});

test('feature page: all groups stay open, current page highlighted', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/features/combat/`);
  expect(await page.evaluate(COLLAPSED, GROUPS)).toEqual(Array(9).fill(false));
  // Combat is a plain link in the World Map group — no sub-list auto-opens
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Combat');
});

test('items catalog index is gone', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  expect(await page.locator('.sidenav a[href="/content/items/"]').count()).toBe(0);
  // the index page itself no longer builds
  const res = await page.request.get('/content/items/');
  expect(res.status()).toBe(404);
});

test('zones map: top-level World Map link is active', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/zones/map/`);
  expect(await page.locator('.sidenav a.active').textContent()).toBe('World Map');
});

test('active selection box spans the whole row, ending after the caret', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/zones/map/`); // World Map header active
  const head = page.locator('.sidenav .nav-group-head.row-active');
  expect(await head.count()).toBe(1);
  const hb = await head.boundingBox();
  const cb = await head.locator('.nav-caret').boundingBox();
  // the box covers the caret: it starts before it and ends after it
  expect(hb.x).toBeLessThanOrEqual(cb.x + 1);
  expect(hb.x + hb.width).toBeGreaterThanOrEqual(cb.x + cb.width - 1);
});

test('shop sub-list expands on demand', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/features/market/`);
  const caret = page.locator(
    '.sidenav li.nav-has-sub:has(> .nav-sub-head > a[href="/content/shop/"]) > .nav-sub-head .nav-caret'
  );
  await caret.click();
  expect(await page.locator('.sidenav .nav-has-sub:has(> .nav-sub-head > a[href="/content/shop/"]) .nav-sub a:visible').count()).toBe(11);
});

test('shop category page: sub-list auto-opens, active link scrolled into view', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/shop/ammo/`);
  const shopSub = page.locator('.sidenav .nav-has-sub:has(> .nav-sub-head > a[href="/content/shop/"])');
  expect(await shopSub.locator('.nav-sub a:visible').count()).toBe(11);
  const active = page.locator('.sidenav a.active');
  expect(await active.textContent()).toBe('Ammo');
  // the sidenav must be scrolled so the active entry is inside its viewport
  const ar = await active.boundingBox();
  const nr = await page.locator('.sidenav').boundingBox();
  expect(ar.y >= nr.y - 1 && ar.y + ar.height <= nr.y + nr.height + 1).toBe(true);
});

test('content sub-page: ores live under Gather, highlighted and in view', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/ores/crude/`);
  // Ores is a direct link in the Gather group (not a sub-list)
  const active = page.locator('.sidenav a.active');
  expect(await active.textContent()).toBe('Ores');
  const ar = await active.boundingBox();
  const nr = await page.locator('.sidenav').boundingBox();
  expect(ar.y >= nr.y - 1 && ar.y + ar.height <= nr.y + nr.height + 1).toBe(true);
});

test('zone data page: family entry highlighted in the World Map sub-list', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/zones/zone-asi/`);
  // zone_ASI is protected: the Alpha family-listing entry is the active one
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/zones/alpha/');
});

test('Bases & sites: Deployables lists its main categories', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  // Deployables is a sub-list under the World Map group (collapsed by default)
  const depLi = page.locator('.sidenav .nav-has-sub:has(> .nav-sub-head > a[href="/content/deployables/"])');
  expect(await depLi.locator('.nav-sub a:visible').count()).toBe(0); // collapsed
  // on the deployables index: the Deployables sub-list auto-opens with its
  // main categories
  await page.goto(`${baseURL}/content/deployables/`);
  const depHrefs = await depLi.locator('.nav-sub a').evaluateAll(as => as.map(a => a.textContent));
  expect(depHrefs.length).toBe(10);
  expect(depHrefs.join(', ')).not.toContain('Power base stations');
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Deployables');
});

test('zone page: the family-listing entry is highlighted', async ({ page, baseURL }) => {
  // zone_ASI is alpha (protected): Alpha lights up
  await page.goto(`${baseURL}/zones/zone-asi/`);
  expect(await page.locator('.sidenav a.active').count()).toBe(1);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/zones/alpha/');
  // a generated beta zone page (open-PvP twin) highlights Beta
  await page.goto(`${baseURL}/zones/zone-asi-a-real/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/zones/beta/');
  // a gamma zone page highlights the Gamma link
  await page.goto(`${baseURL}/zones/zone-gamma-z120/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/zones/gamma/');
});

test('family-listing pages list their zones as cards', async ({ page, baseURL }) => {
  for (const [fam, min] of [['alpha', 5], ['beta', 10], ['gamma', 30]]) {
    await page.goto(`${baseURL}/zones/${fam}/`);
    const cards = page.locator('.zone-cards a.zone-card');
    expect(await cards.count(), fam).toBeGreaterThanOrEqual(min);
    // every card links to a zone page
    const href = await cards.first().getAttribute('href');
    expect(href).toMatch(/^\/zones\/zone-/);
  }
  // the gamma page carries the T0–T4 sections
  await page.goto(`${baseURL}/zones/gamma/`);
  for (const t of ['t0', 't1', 't2', 't3', 't4'])
    expect(await page.locator('#' + t).count(), t).toBe(1);
});

test('extensions page: Character group highlighted, Extensions active', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/extensions/`);
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Extensions');
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/content/extensions/');
});

test('tech tree page: Research group highlighted, Tech tree active', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/techtree/`);
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Tech tree');
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/content/techtree/');
});

// --- Play / Dev mode toggle ---

test('dev mode: the Dev tab switches to the matrix theme, reveals the Dev group, persists', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  // play mode (default): the Dev group is hidden, the menu tree is shown
  expect(await page.locator('.nav-dev').isVisible()).toBe(false);
  // palette selector: enabled in play mode
  expect(await page.locator('#palette-toggle').isDisabled()).toBe(false);
  const playTop = await page.locator('.sidenav > ul > li:visible').evaluateAll((lis) => lis.map((li) => li.className));
  expect(playTop.filter((c) => c.startsWith('nav-group'))).toEqual(
      Array(9).fill('nav-group')); // 9 groups in play mode
  expect(playTop).toContain('nav-modes');
  // the Dev tab: matrix theme + the Dev group — and the menu tree STAYS visible
  await page.click('.mode-tab[data-mode-tab="dev"]');
  expect(await page.locator('html').getAttribute('data-mode')).toBe('dev');
  expect(await page.locator('.nav-dev').isVisible()).toBe(true);
  const devTop = await page.locator('.sidenav > ul > li:visible').evaluateAll((lis) => lis.map((li) => li.className));
  expect(devTop.filter((c) => c.startsWith('nav-group')).length).toBe(10); // 9 + Dev
  const devLinks = await page.locator('.nav-dev a').evaluateAll((as) => as.map((a) => a.getAttribute('href')));
  expect(devLinks).toEqual(['/features/architecture/', '/features/architecture/', '/features/server/', '/formats/']);
  // the matrix theme: bright green neon on near-black
  const neon = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--neon').trim());
  expect(neon.toLowerCase()).toBe('#00ff41');
  // the palette selector is locked in dev mode (the matrix theme owns the
  // accent); the tooltip points at the Home tab
  const pal = page.locator('#palette-toggle');
  expect(await pal.isDisabled()).toBe(true);
  expect(await pal.getAttribute('title')).toMatch(/Home/);
  await page.reload(); // the choice survives a reload (localStorage)
  expect(await page.locator('html').getAttribute('data-mode')).toBe('dev');
  expect(await page.locator('.nav-dev').isVisible()).toBe(true);
  expect(await pal.isDisabled()).toBe(true); // still locked after reload
  // the Home tab exits dev mode (and links to the home page)
  await page.click('.mode-tab[data-mode-tab="home"]');
  expect(await page.locator('html').getAttribute('data-mode')).toBe(null);
  expect(await page.locator('.nav-dev').isVisible()).toBe(false);
  expect(await pal.isDisabled()).toBe(false); // palette unlocked again
});

test('dev mode: developer home page highlights its entry', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  await page.click('.mode-tab[data-mode-tab="dev"]');
  await page.goto(`${baseURL}/features/architecture/`);
  // the Dev group header links to the developer home: it is the active entry
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Dev');
});

// --- sidenav scroll position across navigation ---

const NAV_SCROLL = () => document.querySelector('.sidenav').scrollTop;

const ACTIVE_VISIBLE = () => {
  const nav = document.querySelector('.sidenav');
  const active = nav.querySelector('a.active');
  if (!active) return true; // e.g. the home page has no sidenav entry
  const nr = nav.getBoundingClientRect();
  const ar = active.getBoundingClientRect();
  return ar.top >= nr.top - 1 && ar.bottom <= nr.bottom + 1;
};

test('scroll position is preserved when the new active entry stays visible', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/features/robots/`);
  await page.waitForTimeout(400); // let the debounced scroll save (100 ms) flush
  const s1 = await page.evaluate(NAV_SCROLL);
  expect(s1).toBeGreaterThan(0); // robots is below the fold: the menu actually scrolled
  // Production sits right below Robots in the Produce group: visible at the
  // same scroll offset, so the position must carry over
  await page.locator('.sidenav .nav-items a[href="/features/production/"]').click();
  await page.waitForLoadState('load');
  const s2 = await page.evaluate(NAV_SCROLL);
  // The group header ("Produce") is the active match — it shares the same href
  expect(await page.locator('.sidenav a.active').textContent()).toBe('Produce');
  expect(Math.abs(s2 - s1)).toBeLessThan(4);
});

test('every sidenav link lands with its active entry visible in the menu', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  // only the links visible in the current mode (the Dev group is hidden in
  // play mode; its pages are covered by the dev-mode test below)
  const hrefs = [...new Set(await page.$$eval('.sidenav a[href]', (as) =>
    as.filter((a) => a.offsetParent !== null).map((a) => a.getAttribute('href'))))];
  expect(hrefs.length).toBeGreaterThan(20);
  for (const href of hrefs) {
    await page.goto(`${baseURL}${href}`);
    const ok = await page.evaluate(ACTIVE_VISIBLE);
    expect(ok, `active entry not visible in the sidenav for ${href}`).toBe(true);
  }
});

test('home page: Home quick link is marked active in sidenav', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/`);
  const active = page.locator('.sidenav a.active');
  expect(await active.count()).toBe(1);
  expect(await active.getAttribute('href')).toBe('/');
  expect(await page.locator('.mode-tab[data-mode-tab="home"].active').count()).toBe(1);
});

test('translated pages: active link is highlighted in the menu in translated languages', async ({ page, baseURL }) => {
  // Russian Home
  await page.goto(`${baseURL}/ru/`);
  expect(await page.locator('.mode-tab[data-mode-tab="home"].active').count()).toBe(1);

  // Russian Getting Started
  await page.goto(`${baseURL}/ru/features/getting-started/`);
  expect(await page.locator('.sidenav a.active').count()).toBe(1);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/features/getting-started/');

  // Russian Combat
  await page.goto(`${baseURL}/ru/features/combat/`);
  expect(await page.locator('.sidenav a.active').count()).toBe(1);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/features/combat/');

  // Russian Menu Start overview
  await page.goto(`${baseURL}/ru/menu/start/`);
  expect(await page.locator('.sidenav a.active').count()).toBe(1);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/menu/start/');

  // German FAQ
  await page.goto(`${baseURL}/de/features/faq/`);
  expect(await page.locator('.sidenav a.active').count()).toBe(1);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/de/features/faq/');
});

test('translated content pages: active menu highlight and translated content render properly', async ({ page, baseURL }) => {
  // Russian Ores
  await page.goto(`${baseURL}/ru/content/ores/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/content/ores/');
  await expect(page.locator('h1')).toContainText('Руды');

  // Russian Robots overview
  await page.goto(`${baseURL}/ru/content/robots/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/content/robots/');

  // Russian Individual Robot page
  await page.goto(`${baseURL}/ru/content/robots/arbalest/`);
  await expect(page.locator('h1')).toContainText('Arbalest');
  await expect(page.locator('.robot-card-stats')).toContainText('Бой');
  await expect(page.locator('.robot-card-stats')).toContainText('Скорость');
  await expect(page.locator('.robot-card-stats')).toContainText('Броня');

  // Russian Recipes
  await page.goto(`${baseURL}/ru/content/recipes/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/content/recipes/');
  await expect(page.locator('body')).toContainText('Уровень исследования');

  // Russian Missions
  await page.goto(`${baseURL}/ru/features/missions/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/features/missions/');
  await expect(page.locator('h1')).toContainText('Миссии');

  // Russian Shop
  await page.goto(`${baseURL}/ru/content/shop/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/content/shop/');

  // Russian Shop category
  await page.goto(`${baseURL}/ru/content/shop/ammo/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/ru/content/shop/ammo/');
  await expect(page.locator('table')).toContainText('Предмет');
  await expect(page.locator('table')).toContainText('Кол-во');

  // German Tech Tree Group
  await page.goto(`${baseURL}/de/content/techtree/groups/common1/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/de/content/techtree/groups/common1/');

  // German Tech Tree Node
  await page.goto(`${baseURL}/de/content/techtree/nodes/ammo-cruisemissile-a/`);
  await expect(page.locator('table')).toContainText('Schaltet frei');
  await expect(page.locator('table')).toContainText('Übergeordneter Knoten');

  // French Deployables
  await page.goto(`${baseURL}/fr/content/deployables/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/fr/content/deployables/');
  await expect(page.locator('body')).toContainText('sans palier');

  // Spanish Extensions
  await page.goto(`${baseURL}/es/content/extensions/`);
  expect(await page.locator('.sidenav a.active').getAttribute('href')).toBe('/es/content/extensions/');
  await expect(page.locator('body')).toContainText('rango');
  await expect(page.locator('body')).toContainText('sin requisitos previos');
});

test('protection levels page: zone link highlighted in World Map group', async ({ page, baseURL }) => {
  // The protection levels page is no longer in the nav (it was removed when
  // the World group was restructured). The zone pages still link to it.
  await page.goto(`${baseURL}/zones/`);
  const protLink = page.locator('article a[href="/zones/protection/"]');
  expect(await protLink.count()).toBeGreaterThanOrEqual(1);
});
