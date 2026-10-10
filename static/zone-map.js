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
    var ROOT = (document.body && document.body.getAttribute('data-root')) || '/';
    var ROOT_PATH = ROOT.replace(/^https?:\/\/[^/]+/, '').replace(/\/+$/, ''); // "" | "/Wiki"
    function withRoot(h) {
        if (!h || h.charAt(0) !== '/') return h;
        if (ROOT_PATH && h.indexOf(ROOT_PATH + '/') === 0) return h;
        return ROOT_PATH + h;
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
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'zonemap-reset';
            btn.title = 'Reset the zoom';
            btn.textContent = '⟲';
            wrap.appendChild(btn);

            // display modes (Height / Color) — only for zones whose
            // SVG carries both real-terrain images
            var hImg = svg.querySelector('#zm-height');
            var cImg = svg.querySelector('#zm-color');
            var bar = null;
            if (hImg && cImg) {
                var ui = window.WIKI_UI || {};
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
