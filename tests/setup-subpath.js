// Global setup: build the subpath test fixture — a copy of public/ exactly as
// the GitHub Pages deploy serves it (project site under /wiki/):
//   1. every href/src prefixed with /wiki (tools/rewrite_site_base.py — the
//      same rewrite the deploy pipeline runs)
//   2. data-root + the head-script wikiRoot pointed at the full Pages URL
//      (the deploy build compiles with that base_url; the local build uses "/")
//
// The result (.subpath-public/) is served under /wiki/ by tests/serve.js for
// the "subpath" Playwright project (tests/i18n-subpath.spec.js).

'use strict';

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BASE = 'https://openperpetuum.github.io/wiki';
const OUT = '.subpath-public';

function walk(d, out) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.html')) out.push(p);
  }
}

module.exports = async () => {
  const src = path.resolve('public');
  if (!fs.existsSync(src)) {
    throw new Error('public/ not found — run `make build` first');
  }
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.cpSync(src, OUT, { recursive: true });

  // 1. Prefix site-absolute links with /wiki (idempotent, CI-identical).
  execFileSync('python3', ['tools/rewrite_site_base.py', OUT, BASE], { stdio: 'inherit' });

  // 2. Point the deploy base at the Pages URL (what config.base_url is in
  //    the deploy build) so the runtime JS sees the subpath.
  const html = [];
  walk(OUT, html);
  for (const f of html) {
    let t = fs.readFileSync(f, 'utf-8');
    t = t.split('data-root="/"').join(`data-root="${BASE}"`);
    t = t.split('wikiRoot = "/"').join(`wikiRoot = "${BASE}"`);
    fs.writeFileSync(f, t);
  }
};

// Runnable as a CLI: the Playwright webServer command chains
// `node tests/setup-subpath.js && node tests/serve.js ...` (webServer starts
// before globalSetup, so the fixture must be built as part of the server
// command).
if (require.main === module) {
  module.exports()
    .then(() => console.log('subpath fixture ready: .subpath-public/'))
    .catch((e) => { console.error(e); process.exit(1); });
}
