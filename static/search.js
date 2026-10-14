// Lightweight wiki search over the /search_index.json
// (title + description + URL per page). Debounced; shows a result count.
// This file is loaded from <head>, so wait for the body to exist before
// binding the input.
function wikiSearchInit() {
    var input = document.getElementById('wiki-search');
    var box = document.getElementById('search-results');
    if (!input || !box) return;

    var pages = null;
    var rootPath = '';  // site root as an absolute path ('/' or '/user/repo/wiki/')
    var timer = null;
    var DEBOUNCE_MS = 200;
    var hits = [];      // current result list (search() output)
    var sel = 0;        // index of the keyboard-selected result

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    // Site root, from the deploy base (body[data-root] = config.base_url):
    // "/" locally, the full GitHub Pages URL on the project site. Only the
    // PATH part matters — the site always lives on the CURRENT origin under
    // that path — so both the index fetch and the result links are built
    // origin-relative (a full-URL fetch would leave the origin).
    var baseRoot = (document.body && document.body.getAttribute('data-root')) || '';
    function rootInfo() {
        if (baseRoot) {
            var p = baseRoot.replace(/^https?:\/\/[^/]+/, '').replace(/\/+$/, ''); // "" | "/Wiki"
            return { fetch: p + '/search_index.json', path: p || '/' };
        }
        // no data-root (older build): climb out of the current path
        var parts = location.pathname.replace(/\/+$/, '').split('/').filter(Boolean);
        return {
            fetch: parts.map(function () { return '..'; }).concat('search_index.json').join('/'),
            path: new URL(parts.map(function () { return '..'; }).join('/') + '/', location.href).pathname
        };
    }

    function loadIndex() {
        if (pages) return Promise.resolve(pages);
        var ri = rootInfo();
        rootPath = ri.path;
        var fetchJson = function (url) {
            return fetch(url, { cache: 'force-cache' })
                .then(function (r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.json();
                });
        };
        return Promise.all([
            fetchJson(ri.fetch),
            // Menu tree (static/menu_tree.json, generated from the sidenav):
            // label key or literal + href + ancestor labels per menu link.
            fetchJson(ri.fetch.replace(/search_index\.json$/, 'menu_tree.json'))
                .catch(function () { return null; })
        ]).then(function (res) {
            var data = res[0], menu = res[1] || [];
            var i18n = window.WIKI_I18N || {};
            var lang = (window.WIKI_getLang || function () { return 'en'; })();
            // Menu labels: nav_* keys resolve through the per-language UI
            // strings (fallback English); anything else is a literal
            // (proper nouns like shop/techtree group names, stay English).
            function menuLabel(l) {
                if (typeof l !== 'string') return '';
                if (l.indexOf('nav_') === 0)
                    return (i18n[lang] && i18n[lang][l]) || (i18n.en && i18n.en[l]) || l;
                return l;
            }
            pages = data.map(function (p) {
                var t = p.t || '';
                var d = p.d || '';
                // p.u is site-absolute ("/content/x/"); rootPath is "" for
                // "/" (no change) or the base path ("/Wiki") to prepend.
                var u = p.u || '/';
                if (rootPath && rootPath !== '/' && u.indexOf(rootPath + '/') !== 0)
                    u = rootPath + (u.charAt(0) === '/' ? u : '/' + u);
                return {
                    t: t, d: d, u: u,
                    tl: t.toLowerCase(), dl: (d + ' ' + u).toLowerCase(),
                    _site: p.u || '/'   // site-absolute URL, for menu matching
                };
            });
            // Merge the menu tree: a fragmentless menu link that matches a
            // page URL adds its label + breadcrumb to that page's search
            // space (no duplicate rows); anchor links and URLs missing from
            // the index become their own result rows, so clicking a menu
            // result lands on the right page/section.
            var byUrl = {};
            for (var i = 0; i < pages.length; i++) byUrl[pages[i]._site] = pages[i];
            menu.forEach(function (m) {
                var label = menuLabel(m.l);
                if (!label) return;
                var crumb = (m.p || []).map(menuLabel).join(' \u203A ');
                var site = (m.u || '').split('#')[0];
                if (site.charAt(0) !== '/') site = '/' + site;
                if (site.charAt(site.length - 1) !== '/') site += '/';
                var target = byUrl[site];
                if (target && (m.u || '') === site) {
                    target.tl += ' ' + label.toLowerCase();
                    target.dl += ' ' + label.toLowerCase() + ' ' + crumb.toLowerCase();
                    // Page title: the index holds the English title, but when
                    // the menu label is a translatable (nav_*) key whose
                    // ENGLISH form IS the page's English title, the label is
                    // a translation of that title (not a different label) —
                    // show the translated form, e.g. /zones/map/ "World"
                    // -> "Monde" (fr) / "Welt" (de). Pages whose nav label
                    // differs from the title ("Groups" vs "With others")
                    // keep the index title.
                    if (typeof m.l === 'string' && m.l.indexOf('nav_') === 0) {
                        var enUi = (i18n.en || {})[m.l];
                        if (enUi && enUi === target.t) {
                            target.t = label;
                            target.tl = (label + ' ' + label).toLowerCase();
                        }
                    }
                } else {
                    var u2 = m.u || '/';
                    if (rootPath && rootPath !== '/' && u2.indexOf(rootPath + '/') !== 0)
                        u2 = rootPath + (u2.charAt(0) === '/' ? u2 : '/' + u2);
                    pages.push({
                        t: label, d: crumb, u: u2,
                        tl: label.toLowerCase(),
                        dl: (crumb + ' ' + site).toLowerCase()
                    });
                }
            });
            return pages;
        });
    }

    function search(q) {
        var tokens = q.toLowerCase().split(/\s+/).filter(Boolean);
        if (!tokens.length) return [];
        var out = [];
        for (var i = 0; i < pages.length; i++) {
            var p = pages[i];
            var score = 0;
            var allFound = true;
            for (var j = 0; j < tokens.length; j++) {
                var tk = tokens[j];
                if (p.tl.indexOf(tk) !== -1) score += 3;
                else if (p.dl.indexOf(tk) !== -1) score += 1;
                else { allFound = false; break; }
            }
            if (allFound) out.push([score, p]);
        }
        out.sort(function (a, b) { return b[0] - a[0] || a[1].tl.localeCompare(b[1].tl); });
        return out.slice(0, 25).map(function (x) { return x[1]; });
    }

    function render(q) {
        loadIndex().then(function () {
            hits = search(q);
            sel = 0;
            var ui = window.WIKI_UI || {};
            if (!hits.length) {
                box.innerHTML = '<div class="no-results">' + escapeHtml(ui.search_no_results || 'No pages match') + ' “' + escapeHtml(q) + '”.</div>';
            } else {
                var count = hits.length === 1
                    ? (ui.search_pages_found_one || '1 page found')
                    : (ui.search_pages_found_many || '{n} pages found').replace('{n}', hits.length);
                box.innerHTML =
                    '<div class="result-count">' + escapeHtml(count) + '</div>' +
                    hits.map(function (p, i) {
                        return '<a href="' + escapeHtml(p.u) + '" id="wiki-search-opt-' + i + '" role="option" aria-selected="' + (i === 0) + '">' +
                            '<strong>' + escapeHtml(p.t) + '</strong>' +
                            (p.d ? '<span class="result-desc"> — ' + escapeHtml(p.d.length > 100 ? p.d.slice(0, 100) + '…' : p.d) + '</span>' : '') +
                            '</a>';
                    }).join('');
            }
            box.hidden = false;
            updateSelection();
        }).catch(function () {
            hits = [];
            box.innerHTML = '<div class="no-results">' + escapeHtml((window.WIKI_UI || {}).search_unavailable || 'Search is unavailable') + '</div>';
            box.hidden = false;
        });
    }

    // Keyboard selection over the visible results: ArrowUp/Down move the
    // highlight, Home/End jump to the ends, Enter follows the selection.
    // Mouse hover and the keyboard share the same `sel` index.
    function updateSelection() {
        var links = box.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            var on = i === sel;
            links[i].classList.toggle('sel', on);
            links[i].setAttribute('aria-selected', on ? 'true' : 'false');
            if (on) links[i].scrollIntoView({ block: 'nearest' });
        }
        input.setAttribute('aria-expanded', String(!box.hidden && links.length > 0));
        input.setAttribute('aria-activedescendant',
            !box.hidden && links.length ? 'wiki-search-opt-' + sel : '');
    }

    input.addEventListener('input', function () {
        var v = input.value.trim();
        clearTimeout(timer);
        if (!v) { hits = []; sel = 0; box.hidden = true; box.innerHTML = ''; return; }
        timer = setTimeout(function () { render(v); }, DEBOUNCE_MS);
    });

    input.addEventListener('keydown', function (e) {
        var open = !box.hidden && hits.length;
        if (open && e.key === 'ArrowDown') {
            e.preventDefault();
            sel = Math.min(sel + 1, hits.length - 1);
            updateSelection();
        } else if (open && e.key === 'ArrowUp') {
            e.preventDefault();
            sel = Math.max(sel - 1, 0);
            updateSelection();
        } else if (open && (e.key === 'Home' || e.key === 'End')) {
            e.preventDefault();
            sel = e.key === 'Home' ? 0 : hits.length - 1;
            updateSelection();
        } else if (e.key === 'Escape') {
            input.value = '';
            box.hidden = true;
            box.innerHTML = '';
            input.blur();
        } else if (e.key === 'Enter') {
            // Enter follows the selected result (default: the top one);
            // with nothing shown, clear the box.
            if (open) { window.location.href = hits[sel].u; }
            else { input.value = ''; box.hidden = true; box.innerHTML = ''; }
        }
    });

    // Hovering a result with the mouse moves the keyboard selection with it.
    box.addEventListener('mouseover', function (e) {
        var a = e.target && e.target.closest ? e.target.closest('a') : null;
        if (!a) return;
        var links = box.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            if (links[i] === a) { sel = i; updateSelection(); break; }
        }
    });

    document.addEventListener('click', function (e) {
        if (box.hidden) return;
        if (box.contains(e.target) || e.target === input) return;
        box.hidden = true;
    });
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wikiSearchInit);
} else {
    wikiSearchInit();
}
