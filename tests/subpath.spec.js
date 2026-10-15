// Base-path regression tests that run ONLY in the 'subpath' project, which
// mirrors the GitHub Pages deploy: the same build served under /wiki/ with
// the CI link rewrites + data-root (see tests/setup-subpath.js).
//
// Mermaid `click` targets: the generators write them site-absolute
// (click b "/content/items/...") and Zola never rewrites code-fence text,
// so the page script must prefix them with the base path before rendering
// (templates/base.html, same data-root pattern as search.js). Without that
// fix every diagram box link 404s on the live site.

const { test, expect } = require('@playwright/test');

// The diagram source the page hands to mermaid (and reuses on theme change).
async function mermaidSrc(page, clickFilter) {
  return page.evaluate((filter) => {
    const divs = Array.from(document.querySelectorAll('.mermaid[data-src]'));
    const div = divs.find((d) => d.getAttribute('data-src').includes(filter)) || divs[0];
    return div ? div.getAttribute('data-src') : null;
  }, clickFilter);
}

test('production-tree click URLs are prefixed with the subpath', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/items/alligior/`, { waitUntil: 'load' });
  const src = await mermaidSrc(page, 'click');
  expect(src).toBeTruthy();
  // Item targets and the "+N more" overflow link both carry the base path…
  expect(src).toContain('"/wiki/content/items/artifact-a-armor-repairer-upgrade/"');
  expect(src).toContain('"/wiki/content/recipes/"');
  // …and no site-absolute click URL is left unprefixed (or double-prefixed).
  expect(src).not.toMatch(/click\s+\S+\s+"\/(?!wiki\/)/);
  expect(src).not.toContain('/wiki/wiki/');
});

test('bot and transport-diagram click URLs are prefixed too', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/content/items/material-boss-gamma-syndicate/`, { waitUntil: 'load' });
  const src = await mermaidSrc(page, 'robots');
  expect(src).toContain('"/wiki/content/robots/"');
  expect(src).not.toMatch(/click\s+\S+\s+"\/(?!wiki\/)/);

  await page.goto(`${baseURL}/content/items/ammo-medium-projectile-t/`, { waitUntil: 'load' });
  const tsrc = await mermaidSrc(page, 'click');
  expect(tsrc).toContain('"/wiki/content/items/ammo-medium-projectile-t/"');
  expect(tsrc).not.toContain('/wiki/wiki/');
});

// Multi-destination teleport columns: the selector's entry URLs are built
// AT RUNTIME (map.js hrefOf), so the CI SVG rewrite cannot help them —
// map.js must prefix them with the base path itself. A parse-time read of
// body[data-root] used to make withRoot() a no-op (the script loads in
// <head>, before <body> exists), 404'ing every selector link on the live
// site — English and translated pages alike.
test('multi-destination TP selector navigates under the subpath', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/zones/zone-asi-a-real/`, { waitUntil: 'load' });
  await page.locator('svg.zonemap').waitFor({ state: 'visible', timeout: 20000 });
  const info = await page.evaluate(() => {
    const c = [...document.querySelectorAll('svg.zonemap circle[data-dests]')]
      .find(el => (el.getAttribute('data-dests') || '').split(';').filter(Boolean).length >= 2);
    if (!c) return null;
    c.scrollIntoView({ block: 'center' });
    const b = c.getBoundingClientRect();
    return { x: b.left + b.width / 2, y: b.top + b.height / 2, dests: c.getAttribute('data-dests') };
  });
  expect(info).toBeTruthy();
  // first entry's destination = zone name (after the last '|') of the
  // first pair — same math as map.js hrefOf
  const zoneName = info.dests.split(';')[0].split('|').pop();
  const expected = `${baseURL}/zones/${zoneName.toLowerCase().replace(/_/g, '-')}/`;
  let hit = 0;
  await page.route(expected, (route) => { hit += 1; return route.abort(); });
  await page.mouse.move(info.x, info.y);
  await expect(page.locator('.tp-sel')).toBeVisible();
  await page.locator('.tp-sel .tp-sel-item').first().click();
  await page.waitForTimeout(200);
  expect(hit).toBe(1);
});

test('single-destination TP links in the inlined map carry the prefix', async ({ page, baseURL }) => {
  await page.goto(`${baseURL}/zones/zone-asi-a-real/`, { waitUntil: 'load' });
  await page.locator('svg.zonemap').waitFor({ state: 'visible', timeout: 20000 });
  const hrefs = await page.locator('svg.zonemap a[href]').evaluateAll(as => as.map(a => a.getAttribute('href')));
  expect(hrefs.length).toBeGreaterThan(0);
  for (const h of hrefs) expect(h).toMatch(/^\/wiki\/zones\//);
});

test('clicking a diagram node navigates to the prefixed page', async ({ page, baseURL }) => {
  const target = `${baseURL}/content/items/named2-thermal-kers/`;
  let hit = 0;
  // Intercept the navigation the click triggers (mermaid does
  // window.open(url, "_self")) so the test does not actually leave the page.
  await page.route(target, (route) => {
    hit += 1;
    return route.abort();
  });
  await page.goto(`${baseURL}/content/items/named1-thermal-kers/`, { waitUntil: 'load' });
  await page.locator('.mermaid svg').first().waitFor({ timeout: 20000 });
  // Node b is the first product ("DE-melt thermal ERP"); the rendered group
  // id (flowchart-<id>-<n>) is stable, unlike label text (the prototype
  // node's label starts with the same words).
  await page.locator('.mermaid g#flowchart-b-1').click();
  await page.waitForTimeout(200);
  expect(hit).toBe(1);
});
