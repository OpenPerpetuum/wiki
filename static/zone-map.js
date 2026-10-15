// Zone teleport maps: the generated zone pages embed the maps as plain
// <img src="/zonemaps/<zone>.svg">. The SVGs carry clickable teleport
// elements (<a href="/zones/...">), which an <img> cannot show — so fetch
// the SVG, inline it into the shared .zonemap-wrap wrapper (with the
// reset button) and replace the <img>. static/map.js watches the DOM and
// attaches wheel-zoom / drag-pan / pinch / reset to the new wrapper, so
// the zone maps behave exactly like the world map.
// If the fetch fails (offline, unsupported browser) the static <img>
// stays — the map is still visible, just not interactive.
(function () {
    'use strict';

    // The display mode (height/color) is a user preference: it is
    // remembered and applied to every zone map that gets inlined. (Older
    // versions also had a 'plain' mode; that value now reads as 'height'.)
    var MODE_KEY = 'wiki-zonemap-mode';
    function getMode() {
        try { return localStorage.getItem(MODE_KEY); } catch (err) { return null; }
    }
    function setMode(m) {
        try { localStorage.setItem(MODE_KEY, m); } catch (err) { /* private mode */ }
    }

    var LANDMARKS_KEY = 'wiki-zonemap-landmarks';
    var DEFAULT_LANDMARKS = {
        teleports: true,
        outposts: true,
        terminals: true,
        roads: true,
        labels: true
    };

    function getLandmarks() {
        try {
            var raw = localStorage.getItem(LANDMARKS_KEY);
            if (raw) return Object.assign({}, DEFAULT_LANDMARKS, JSON.parse(raw));
        } catch (e) {}
        return Object.assign({}, DEFAULT_LANDMARKS);
    }

    function setLandmarks(cfg) {
        try {
            localStorage.setItem(LANDMARKS_KEY, JSON.stringify(cfg));
        } catch (e) {}
        applyLandmarksGlobally(cfg);
    }

    function applyLandmarksToWrap(wrap, cfg) {
        wrap.classList.toggle('zm-hide-teleports', !cfg.teleports);
        wrap.classList.toggle('zm-hide-outposts', !cfg.outposts);
        wrap.classList.toggle('zm-hide-terminals', !cfg.terminals);
        wrap.classList.toggle('zm-hide-roads', !cfg.roads);
        wrap.classList.toggle('zm-hide-labels', !cfg.labels);

        var panel = wrap.querySelector('.zonemap-landmarks-panel');
        if (panel) {
            var inputs = panel.querySelectorAll('input[type="checkbox"][data-landmark]');
            for (var i = 0; i < inputs.length; i++) {
                var k = inputs[i].getAttribute('data-landmark');
                if (k && typeof cfg[k] !== 'undefined') {
                    inputs[i].checked = !!cfg[k];
                }
            }
        }
    }

    function applyLandmarksGlobally(cfg) {
        var wraps = document.querySelectorAll('.zonetp-wrap');
        for (var i = 0; i < wraps.length; i++) {
            applyLandmarksToWrap(wraps[i], cfg);
        }
    }

    window.addEventListener('storage', function (e) {
        if (e.key === LANDMARKS_KEY) {
            applyLandmarksGlobally(getLandmarks());
        }
    });
    function applyWorldMode(svg, mode) {
        if (mode !== 'color' && mode !== 'height') mode = 'base';
        Array.prototype.forEach.call(svg.querySelectorAll('.wm-base'), function(el) { el.style.display = mode === 'base' ? '' : 'none'; });
        Array.prototype.forEach.call(svg.querySelectorAll('.wm-height'), function(el) { el.style.display = mode === 'height' ? '' : 'none'; });
        Array.prototype.forEach.call(svg.querySelectorAll('.wm-color'), function(el) { el.style.display = mode === 'color' ? '' : 'none'; });
        var wrap = svg.closest('.zonemap-wrap');
        if (wrap) {
            wrap.classList.toggle('zm-color', mode === 'color');
            var bar = wrap.querySelector('.zonemap-modes');
            if (bar) {
                Array.prototype.forEach.call(bar.querySelectorAll('.zonemap-mode'), function (x) {
                    x.setAttribute('aria-pressed', x.getAttribute('data-mode') === mode ? 'true' : 'false');
                });
            }
        }
    }

    function applyMode(hImg, cImg, mode, bar) {
        if (mode !== 'color' && mode !== 'height') mode = 'base';
        hImg.style.display = mode === 'height' ? '' : 'none';
        cImg.style.display = mode === 'color' ? '' : 'none';
        var wrap = hImg.closest ? hImg.closest('.zonetp-wrap') : null;
        if (wrap) {
            wrap.classList.toggle('zm-color', mode === 'color');
        }
        if (bar) {
            Array.prototype.forEach.call(bar.querySelectorAll('.zonemap-mode'), function (x) {
                x.setAttribute('aria-pressed', x.getAttribute('data-mode') === mode ? 'true' : 'false');
            });
        }
    }

    // Deploy base (body[data-root]): the SVG files carry SITE-ABSOLUTE
    // links and image hrefs (written by the generator; fetched as plain
    // files, so nothing rewrites them) — prefix with the base's PATH part
    // for subpath deploys (no-op when the base is "/").
    //
    // Read LAZILY: this script loads in <head>, so document.body does not
    // exist yet at parse time (an eager read made ROOT_PATH "" forever).
    var ROOT_PATH = null;
    function rootPath() {
        if (ROOT_PATH === null && document.body) {
            var root = document.body.getAttribute('data-root') || '/';
            ROOT_PATH = root.replace(/^https?:\/\/[^/]+/, '').replace(/\/+$/, '');
        }
        return ROOT_PATH || '';
    }
    function withRoot(h) {
        if (!h || h.charAt(0) !== '/') return h;
        var rp = rootPath();
        if (rp && h.indexOf(rp + '/') === 0) return h;
        return rp + h;
    }

    function upgrade(img) {
        var src = img.getAttribute('src');
        fetch(src + "?t=" + Date.now(), { credentials: 'same-origin' }).then(function (r) {
            if (!r.ok) throw new Error('http ' + r.status);
            return r.text();
        }).then(function (text) {
            var doc = new DOMParser().parseFromString(text, 'image/svg+xml');
            if (doc.querySelector('parsererror')) throw new Error('bad svg');
            var svg = doc.querySelector('svg');
            if (!svg) throw new Error('no svg');
            // fill the wrapper like the world map (CSS sizes .zonemap)
            svg.classList.add('zonemap');
            svg.removeAttribute('width');
            svg.removeAttribute('height');
            // teleport links + terrain <image>s: prefix the deploy base
            Array.prototype.forEach.call(svg.querySelectorAll('a[href]'), function (a) {
                a.setAttribute('href', withRoot(a.getAttribute('href')));
            });
            Array.prototype.forEach.call(svg.querySelectorAll('image'), function (im) {
                var h = im.getAttribute('href') || im.getAttribute('xlink:href');
                if (h) im.setAttribute('href', withRoot(h));
            });
            Array.prototype.forEach.call(svg.querySelectorAll('.zonemap-node-special[data-title]'), function (node) {
                var t = document.createElementNS('http://www.w3.org/2000/svg', 'title');
                t.textContent = node.getAttribute('data-title');
                node.appendChild(t);
            });


            var wrap = document.createElement('div');
            wrap.className = 'zonemap-wrap zonetp-wrap';
            var ui = window.WIKI_UI || {};
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'zonemap-reset';
            btn.title = ui.zonemapResetZoom || 'Reset the zoom';
            btn.textContent = '⟲';
            wrap.appendChild(btn);

            var lmToggle = document.createElement('button');
            lmToggle.type = 'button';
            lmToggle.className = 'zonemap-landmarks-toggle';
            lmToggle.setAttribute('aria-expanded', 'false');
            lmToggle.title = ui.zonemapLandmarks || 'Landmarks';
            lmToggle.textContent = ui.zonemapLandmarks || 'Landmarks';

            var lmPanel = document.createElement('div');
            lmPanel.className = 'zonemap-landmarks-panel panel-hidden';
            lmPanel.setAttribute('role', 'dialog');
            lmPanel.setAttribute('aria-label', ui.zonemapLandmarks || 'Landmarks');

            var lmHeader = document.createElement('div');
            lmHeader.className = 'zonemap-landmarks-header';
            var lmTitle = document.createElement('span');
            lmTitle.textContent = ui.zonemapLandmarks || 'Landmarks';
            var lmToggleAll = document.createElement('button');
            lmToggleAll.type = 'button';
            lmToggleAll.className = 'zonemap-landmarks-all-btn';
            lmToggleAll.textContent = ui.zonemapToggleAll || 'Toggle all';
            lmHeader.appendChild(lmTitle);
            lmHeader.appendChild(lmToggleAll);
            lmPanel.appendChild(lmHeader);

            var items = [
                { key: 'teleports', label: ui.zonemapLmTeleports || 'Teleports & Gates', icon: '⬡' },
                { key: 'outposts', label: ui.zonemapLmOutposts || 'Outposts', icon: '◉' },
                { key: 'terminals', label: ui.zonemapLmTerminals || 'Field terminals', icon: '▽' },
                { key: 'roads', label: ui.zonemapLmRoads || 'Roads', icon: '━' },
                { key: 'labels', label: ui.zonemapLmLabels || 'Labels', icon: 'Aa' }
            ];

            var lmList = document.createElement('div');
            lmList.className = 'zonemap-landmarks-list';

            items.forEach(function (item) {
                var lbl = document.createElement('label');
                lbl.className = 'zonemap-landmark-item';
                var cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.setAttribute('data-landmark', item.key);
                cb.addEventListener('change', function () {
                    var cfg = getLandmarks();
                    cfg[item.key] = cb.checked;
                    setLandmarks(cfg);
                });
                var iconSpan = document.createElement('span');
                iconSpan.className = 'zonemap-lm-icon';
                iconSpan.textContent = item.icon;
                var textSpan = document.createElement('span');
                textSpan.textContent = item.label;
                lbl.appendChild(cb);
                lbl.appendChild(iconSpan);
                lbl.appendChild(textSpan);
                lmList.appendChild(lbl);
            });
            lmPanel.appendChild(lmList);

            lmToggleAll.addEventListener('click', function (e) {
                e.stopPropagation();
                var cfg = getLandmarks();
                var allChecked = items.every(function (it) { return cfg[it.key]; });
                items.forEach(function (it) { cfg[it.key] = !allChecked; });
                setLandmarks(cfg);
            });

            lmToggle.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
            lmToggle.addEventListener('click', function (e) {
                e.stopPropagation();
                var isOpen = !lmPanel.classList.contains('panel-hidden');
                lmPanel.classList.toggle('panel-hidden', isOpen);
                lmToggle.setAttribute('aria-expanded', String(!isOpen));
            });
            lmPanel.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
            lmPanel.addEventListener('click', function (e) { e.stopPropagation(); });

            document.addEventListener('pointerdown', function (e) {
                if (!lmPanel.contains(e.target) && e.target !== lmToggle) {
                    lmPanel.classList.add('panel-hidden');
                    lmToggle.setAttribute('aria-expanded', 'false');
                }
            });

            wrap.appendChild(lmToggle);
            wrap.appendChild(lmPanel);

            // display modes (Height / Color) — only for zones whose
            // SVG carries both real-terrain images
            var hImg = svg.querySelector('#zm-height');
            var cImg = svg.querySelector('#zm-color');
            var bar = null;
            if (hImg && cImg) {
                bar = document.createElement('div');
                bar.className = 'zonemap-modes';
                [['base', ui.zonemapModeBase || 'Base'],
                 ['height', ui.zonemapModeHeight || 'Height'],
                 ['color', ui.zonemapModeColor || 'Color']].forEach(function (m) {
                    var b = document.createElement('button');
                    b.type = 'button';
                    b.className = 'zonemap-mode';
                    b.textContent = m[1];
                    b.setAttribute('data-mode', m[0]);
                    b.addEventListener('click', function () {
                        setMode(m[0]);
                        applyMode(hImg, cImg, m[0], bar);
                        var wmap = document.querySelector('.zonemap-wrap .zonemap.is-worldmap');
                        if (wmap) applyWorldMode(wmap, m[0]);
                    });
                    bar.appendChild(b);
                });
                wrap.appendChild(bar);
            }
            wrap.appendChild(svg);
            // after the SVG is in its wrap, so the remembered choice can also
            // toggle the wrap's zm-color class / line emphasis
            if (hImg && cImg) applyMode(hImg, cImg, getMode(), bar);
            applyLandmarksToWrap(wrap, getLandmarks());

            // the <img> sits alone in a <p>; replace that paragraph so a
            // <div> is not nested in <p>
            var host = img.parentNode && img.parentNode.nodeName === 'P'
                ? img.parentNode
                : img;
            host.parentNode.replaceChild(wrap, host);
        }).catch(function () { /* keep the static <img> */ });
    }

    function scan() {
        var imgs = document.querySelectorAll('img[src*="/zonemaps/"]');
        for (var i = 0; i < imgs.length; i++) {
            if (imgs[i].getAttribute('data-zonetp-init')) continue;
            if (imgs[i].classList.contains('zone-card-thumb') || (imgs[i].closest && imgs[i].closest('.zone-card')) || imgs[i].getAttribute('src').indexOf('thumb.') !== -1) {
                continue;
            }
            imgs[i].setAttribute('data-zonetp-init', '1');
            upgrade(imgs[i]);
        }
        var worldMap = document.querySelector('.zonemap-wrap .zonemap');
        if (worldMap && !worldMap.closest('.zonetp-wrap')) {
            if (!worldMap.getAttribute('data-modes-init') && document.querySelector('.wm-height')) {
                worldMap.setAttribute('data-modes-init', '1');
                worldMap.classList.add('is-worldmap');
                var wrap = worldMap.closest('.zonemap-wrap');
                var ui = window.WIKI_UI || {};
                var bar = document.createElement('div');
                bar.className = 'zonemap-modes';
                [['base', ui.zonemapModeBase || 'Base'],
                 ['height', ui.zonemapModeHeight || 'Height'],
                 ['color', ui.zonemapModeColor || 'Color']].forEach(function (m) {
                    var b = document.createElement('button');
                    b.type = 'button';
                    b.className = 'zonemap-mode';
                    b.textContent = m[1];
                    b.setAttribute('data-mode', m[0]);
                    b.addEventListener('click', function () {
                        setMode(m[0]);
                        applyWorldMode(worldMap, m[0]);
                        document.querySelectorAll('.zonetp-wrap').forEach(function(zw) {
                            var hi = zw.querySelector('#zm-height');
                            var ci = zw.querySelector('#zm-color');
                            var bbar = zw.querySelector('.zonemap-modes');
                            if (hi && ci) applyMode(hi, ci, m[0], bbar);
                        });
                    });
                    bar.appendChild(b);
                });
                wrap.appendChild(bar);
            }
            if (worldMap.getAttribute('data-modes-init')) {
                applyWorldMode(worldMap, getMode() || 'base');
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scan);
    } else {
        scan();
    }
})();
