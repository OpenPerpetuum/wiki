namespace Perpetuum.WikiGenerate;

/// <summary>
/// The zone map page: every zone drawn at its real grid coordinates
/// (zones.x/y) with the same design as its index card — the coastline-only
/// thumb.png (tools/gen_zone_teleport_maps.py) in the family color over a
/// dark plate, outlined by galaxy family — plus the teleport and rift gate
/// connections recorded in the server database: inter-zone TPs as dashed
/// lines gradient-colored from the source family color to the destination's,
/// exit gates as the classic dashed link lines. Rendered as inline SVG so it
/// themes with the site; map.js adds zoom (wheel) and pan (drag), and every
/// island links to a zone page. The sub-category sections below the map are
/// card grids (the same thumb.png) instead of stat tables.
/// </summary>
public static class ZonesMapPage
{
    internal sealed record Zone(string Name, int Type, double X, double Y, int W, int H, bool Protected, bool Terraformable, int TpCount);

    /// <summary>Nullable double read (AVG over an all-NULL column is NULL).</summary>
    private static object? NulDbl(Dictionary<string, object?> r, string k)
        => r.TryGetValue(k, out var v) && v is not null ? Convert.ToDouble(v) : null;

    internal sealed record Group(string Id, string Label, string Blurb, List<Zone> Zones);

    public static string Build(Db db)
    {
        var zones = db.Query("""
            SELECT z.id, z.name, z.zonetype, z.x, z.y, z.width, z.height, z.protected, z.terraformable, z.enabled,
                   (SELECT COUNT(*) FROM zoneentities ze WHERE ze.zoneid = z.id AND LOWER(ze.ename) LIKE 'teleport_column%') AS tpcount
            FROM zones z ORDER BY z.id
            """)
            .Select(r => new Zone(r.Str("name"), r.Int("zonetype"), r.Dbl("x"), r.Dbl("y"),
                r.Int("width"), r.Int("height"), r.Bit("protected"), r.Bit("terraformable"), r.Int("tpcount")))
            .ToList();

        // Teleport column positions per zone (tile coords within the zone grid).
        var tpPos = db.Query("""
            SELECT z.name AS zonename, ze.x AS tx, ze.y AS ty, ze.ename
            FROM zoneentities ze
            JOIN zones z ON z.id = ze.zoneid
            WHERE LOWER(ze.ename) LIKE 'teleport_column%' AND z.x < 49000 AND z.y < 49000
            """)
            .GroupBy(r => r.Str("zonename"))
            .ToDictionary(g => g.Key, g => g.Select(r => (r.Dbl("tx"), r.Dbl("ty"), r.Str("ename"))).ToList());

        // The zones table can hold several rows with the same name (e.g. zone_TM has
        // three — the extra rows sit at 50000/51000 sentinel coordinates). The map
        // plots one node per zone name, keeping the first (lowest id) row.
        var byName = zones.GroupBy(z => z.Name).ToDictionary(g => g.Key, g => g.First());
        var all = byName.Values.ToList();

        // Viewbox from the real coordinates only: the 50000/51000 sentinel rows must
        // not stretch the canvas (they would leave the real map as a sliver in a
        // corner). Every plotted zone's primary row has a real coordinate, so
        // excluding the sentinels never drops a node.
        var real = all.Where(z => z.X < 49000 && z.Y < 49000).ToList();
        var minX = real.Min(z => z.X);
        var maxX = real.Max(z => z.X);
        var minY = real.Min(z => z.Y);
        var maxY = real.Max(z => z.Y);
        var w = Math.Max(1, maxX - minX);
        var h = Math.Max(1, maxY - minY);
        const double vbW = 1000;
        const double padFrac = 0.10; // extra room: islands have extent and labels sit outside
        var vbH = vbW * (h + 2 * padFrac * h) / (w + 2 * padFrac * w);
        double Px(double x) => (x - minX + padFrac * w) / (w + 2 * padFrac * w) * vbW;
        // The game's grid coordinates grow downward (the zone teleport maps
        // plot them directly on the terrain PNGs and everything aligns), so
        // the world map must NOT flip the axis: gamma sits at the top of the
        // map, the starter islands (TM/ASI/ICS + training) at the bottom.
        double Py(double y) => (y - minY + padFrac * h) / (h + 2 * padFrac * h) * vbH;

        // Known gate connections from the DB: stronghold/arena exits and their
        // destinations (grouped — a zone can have several exit configs to the same
        // destination). The gate positions (se.x/se.y) anchor the line to the
        // gate's real spot in the source zone.
        var links = db.Query("""
            SELECT sz.name AS src, dz.name AS dst, rc.name AS rift,
                   AVG(se.x) AS gx, AVG(se.y) AS gy
            FROM strongholdexitconfig se
            JOIN zones sz ON sz.id = se.zoneid
            JOIN riftconfigs rc ON rc.id = se.riftConfigId
            JOIN riftdestinations rd ON rd.groupId = rc.destinationGroupId
            JOIN zones dz ON dz.id = rd.zoneId
            GROUP BY sz.name, dz.name, rc.name
            """)
            .Select(r => (Src: r.Str("src"), Dst: r.Str("dst"), Rift: r.Str("rift"),
                Gx: (double?)NulDbl(r, "gx"), Gy: (double?)NulDbl(r, "gy")))
            .GroupBy(l => (l.Src, l.Dst))
            .Select(g => g.First())
            .OrderBy(l => l.Src).ThenBy(l => l.Dst)
            .ToList();

        // Inter-zone teleport points: teleportdescriptions records every TP column
        // (sourcezone -> targetzone); most of the 365 rows are intra-zone, the
        // inter-zone ones (1-4 per zone pair) are the real travel network. The
        // column positions (zoneentities x/y) and the landing spots
        // (targetx/targety) anchor each line to the REAL spots in both zones,
        // not their centers.
        var tps = db.Query("""
            SELECT zs.name AS src, zd.name AS dst, COUNT(*) AS tps,
                   AVG(ze.x) AS sx, AVG(ze.y) AS sy,
                   AVG(td.targetx) AS tx, AVG(td.targety) AS ty
            FROM teleportdescriptions td
            JOIN zones zs ON zs.id = td.sourcezone
            JOIN zones zd ON zd.id = td.targetzone
            JOIN zoneentities ze ON ze.eid = td.sourcecolumn
            WHERE td.sourcezone <> td.targetzone AND td.active = 1
            GROUP BY zs.name, zd.name
            """)
            .Select(r => (Src: r.Str("src"), Dst: r.Str("dst"), Tps: r.Int("tps"),
                Sx: (double?)NulDbl(r, "sx"), Sy: (double?)NulDbl(r, "sy"),
                Tx: (double?)NulDbl(r, "tx"), Ty: (double?)NulDbl(r, "ty")))
            .OrderBy(l => l.Src).ThenBy(l => l.Dst)
            .ToList();

        var sb = new StringBuilder();
        sb.Append(Md.Header("World", "Every zone drawn with its real terrain at its grid position, outlined by galaxy, with the teleport and gate connections from the database.",
            "zones (x/y, width, protected, terraformable), teleportdescriptions, zoneentities, strongholdexitconfig + riftconfigs + riftdestinations"));
        sb.Append("\n\n# World\n\n");
        sb.Append("<div class=\"zonemap-wrap\">\n");
        sb.Append("<button type=\"button\" class=\"zonemap-reset\" title=\"Reset the zoom\">⟲</button>\n");
        sb.Append(Svg(all, byName, links, tps, tpPos, vbW, vbH, Px, Py));
        sb.Append(LegendHtml());
        sb.Append("</div>\n\n");
        sb.Append("<div class=\"zonemap-legend\">Island sizes (tiles): ");
        foreach (var (lab, px) in LegendSizes())
        {
            var style = $"width:{px * 0.5:0.#}px;min-width:6px";
            sb.Append($"<span class=\"legend-isle\" style=\"{style}\"></span> {lab};&ensp; ");
        }
        sb.Append("</div>\n\n");
        // The per-family zone listings live on their own pages (see
        // FamilyPages) — the map page only links to them.
        sb.Append("Zone listings: [Alpha](/zones/alpha/) · [Beta](/zones/beta/) · [Gamma](/zones/gamma/) — ");
        sb.Append("[Zone index](/zones/zone-index/) · [Protection levels](/zones/protection/)\n");
        return sb.ToString();
    }

    /// <summary>The per-family zone-listing pages (/zones/alpha/, /zones/beta/,
    /// /zones/gamma/). Each family gets its own page with the card grid that
    /// used to be a section at the bottom of the world map page — the world
    /// map stays the map, the listings get a URL of their own (and the nav
    /// highlights the matching entry on every zone page of that family).
    /// The gamma page splits the frontier belt into its T0–T4 sections.
    /// (filename, markdown) pairs, ready to write next to map.md.</summary>
    public static List<(string File, string Md)> FamilyPages(Db db)
    {
        var zones = db.Query("""
            SELECT z.id, z.name, z.zonetype, z.x, z.y, z.width, z.height, z.protected, z.terraformable, z.enabled,
                   (SELECT COUNT(*) FROM zoneentities ze WHERE ze.zoneid = z.id AND LOWER(ze.ename) LIKE 'teleport_column%') AS tpcount
            FROM zones z ORDER BY z.id
            """)
            .Select(r => new Zone(r.Str("name"), r.Int("zonetype"), r.Dbl("x"), r.Dbl("y"),
                r.Int("width"), r.Int("height"), r.Bit("protected"), r.Bit("terraformable"), r.Int("tpcount")))
            .ToList();
        var byName = zones.GroupBy(z => z.Name).ToDictionary(g => g.Key, g => g.First());
        var all = byName.Values.ToList();
        var groups = Groups(all);

        var pages = new List<(string, string)>();
        foreach (var g in groups.Where(g => g.Id != "training"))
        {
            var sb = new StringBuilder();
            var gamma = g.Id.StartsWith("t", StringComparison.Ordinal);
            var title = gamma ? "Gamma" : g.Label;
            var file = (gamma ? "gamma" : g.Id) + ".md";
            var desc = gamma
                ? "Every frontier-belt zone: the tc transit zones and the T1–T4 tier islands, each with its page."
                : $"Every {g.Id} zone — {(g.Id == "alpha" ? "the protected main islands and their PvE companions" : "the open-PvP islands")}, each with its own page.";
            sb.Append(Md.Header(title, desc, "zones (name, zonetype, width, height, protected, terraformable)",
                "family: " + (gamma ? "gamma" : g.Id)));
            sb.Append($"\n# {title}\n\n");
            if (gamma)
            {
                sb.Append("The frontier belt, split by the server-recorded tier (zones.note): the six tc transit zones (T0) and the tier islands T1–T4 — open PvP and terraformable, see [Protection levels](/zones/protection/).\n\n");
            }
            else
            {
                sb.Append(g.Blurb + "\n\n");
            }
            if (gamma)
            {
                // the tier groups are exactly the two-letter "t0"-"t4" ids —
                // "training" also starts with "t" and must NOT be a tier
                foreach (var t in groups.Where(IsTier))
                {
                    sb.Append($"<a id=\"{t.Id}\"></a>\n\n## {t.Label}\n\n{t.Blurb}\n\n");
                    sb.Append(Cards(t.Zones));
                }
            }
            else
            {
                sb.Append(Cards(g.Zones));
            }
            sb.Append("\n[World map](/zones/map/) · [Zone index](/zones/zone-index/) · [Protection levels](/zones/protection/)\n");
            pages.Add((file, sb.ToString()));
        }
        return pages;
    }

    /// <summary>A tier group (the gamma page's T0–T4 split). "training" starts
    /// with "t" too — it is not a tier.</summary>
    internal static bool IsTier(Group g) => g.Id.Length == 2 && g.Id[0] == 't';

    /// <summary>A zone-card grid (thumb.png per zone) — the same cards the
    /// family pages and the zone index use.</summary>
    internal static string Cards(List<Zone> zones)
    {
        var sb = new StringBuilder();
        sb.Append("<div class=\"zone-cards\">\n");
        foreach (var z in zones)
        {
            var slug = z.Name.ToLowerInvariant().Replace("_", "-");
            sb.Append($"<a class=\"zone-card\" href=\"/zones/{slug}/\">\n");
            sb.Append($"<img class=\"zone-card-thumb\" src=\"/zonemaps/{slug}/thumb.png\" alt=\"\" loading=\"lazy\">\n");
            sb.Append($"<span class=\"zone-card-name\">{Escape(ZoneName(z.Name))}</span>\n");
            sb.Append($"<span class=\"zone-card-meta\">{TypeLabel(z.Type)} · {z.W}×{z.H}</span>\n");
            sb.Append("</a>\n");
        }
        sb.Append("</div>\n\n");
        return sb.ToString();
    }

    /// <summary>Island size in viewbox units for a zone's real width.</summary>
    private static double Size(double w) => w switch
    {
        >= 1800 => 38,
        >= 800 => 24,
        >= 380 => 15,
        _ => 10,
    };

    private static IEnumerable<(string Lab, double Px)> LegendSizes()
    {
        yield return ("2048 (main islands)", 38);
        yield return ("1024 (training)", 24);
        yield return ("512 (stronghold)", 15);
        yield return ("256 (tc zones)", 10);
    }

    /// <summary>The interactive legend overlay inside the map wrapper.</summary>
    private static string LegendHtml()
    {
        var sb = new StringBuilder();
        sb.Append("<button type=\"button\" class=\"map-legend-toggle\" id=\"map-legend-toggle\" aria-expanded=\"true\">Legend</button>\n");
        sb.Append("<div class=\"map-legend\" id=\"map-legend\">\n");
        // Protection level section (top)
        sb.Append("  <div class=\"map-legend-group\">\n");
        sb.Append("    <button type=\"button\" class=\"map-legend-head\" aria-expanded=\"true\">Protection</button>\n");
        sb.Append("    <ul class=\"map-legend-items\">\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:transparent;border:2px solid #41d3ff\"></span>Alpha (PvE)</li>\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:transparent;border:2px solid #fbbf24\"></span>Beta (PvP)</li>\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:transparent;border:2px solid #ef4444\"></span>Gamma (PvP + Terraforming)</li>\n");
        sb.Append("    </ul>\n");
        sb.Append("  </div>\n");
        // Zones section
        sb.Append("  <div class=\"map-legend-group\">\n");
        sb.Append("    <button type=\"button\" class=\"map-legend-head\" aria-expanded=\"true\">Galaxies</button>\n");
        sb.Append("    <ul class=\"map-legend-items\">\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:#41d3ff\"></span>TM (The Matriarkh)</li>\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:#6ee7a0\"></span>ICS (Interstellar Coalition)</li>\n");
        sb.Append("      <li><span class=\"legend-swatch\" style=\"background:#f5a05a\"></span>ASI (Ascension)</li>\n");
        sb.Append("    </ul>\n");
        sb.Append("  </div>\n");
        // Landmarks section
        sb.Append("  <div class=\"map-legend-group\">\n");
        sb.Append("    <button type=\"button\" class=\"map-legend-head\" aria-expanded=\"true\">Landmarks</button>\n");
        sb.Append("    <ul class=\"map-legend-items\">\n");
        sb.Append("      <li><span class=\"legend-icon\">Aa</span>Labels</li>\n");
        sb.Append("      <li><span class=\"legend-icon\">◉</span>Base</li>\n");
        sb.Append("      <li><span class=\"legend-icon\">▽</span>Field terminal</li>\n");
        sb.Append("      <li><span class=\"legend-icon\">⬡</span>Teleport</li>\n");
        sb.Append("      <li><span class=\"legend-icon\">╌</span>Teleport path</li>\n");
        sb.Append("      <li><span class=\"legend-icon\" style=\"color:#a78bfa\">◉</span>Gamma gateway teleport</li>\n");
        sb.Append("    </ul>\n");
        sb.Append("  </div>\n");
        sb.Append("</div>\n");
        sb.Append("<script>" +
            "document.querySelectorAll('.map-legend-head').forEach(function(b){b.addEventListener('click',function(){var g=b.parentElement;var items=g.querySelector('.map-legend-items');var open=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!open));items.classList.toggle('collapsed',open);});});" +
            "var lt=document.getElementById('map-legend-toggle');" +
            "if(lt){lt.addEventListener('click',function(){var lg=document.getElementById('map-legend');var hidden=lg.classList.toggle('legend-hidden');lt.setAttribute('aria-expanded',String(!hidden));});}" +
            "document.querySelectorAll('.map-legend-items li').forEach(function(li) { li.addEventListener('click', function() { var group = li.closest('.map-legend-group').querySelector('.map-legend-head').textContent.trim(); if (group === 'Landmarks') return; var text = li.textContent.trim(); var titleIncludes = ''; var selector = ''; if (text.includes('Alpha')) titleIncludes = 'protected (alpha)'; else if (text.includes('Beta')) titleIncludes = 'open (beta)'; else if (text.includes('Gamma (PvP')) titleIncludes = 'open (gamma)'; else if (text.includes('TM (The')) selector = '.zonemap-node-tm'; else if (text.includes('ICS (Inter')) selector = '.zonemap-node-ics'; else if (text.includes('ASI (Asce')) selector = '.zonemap-node-asi'; else if (text.includes('Gamma') && !text.includes('gateway')) selector = '.zonemap-node-gamma'; else return; var nodes = []; if (selector) { document.querySelectorAll(selector).forEach(function(n) { nodes.push(n.closest('a') || n); }); } else if (titleIncludes) { document.querySelectorAll('.zonemap a title').forEach(function(t) { if (t.textContent.includes(titleIncludes)) nodes.push(t.closest('a')); }); } if (!nodes.length) return; var svg = document.querySelector('svg.zonemap'); var wrap = svg.closest('.zonemap-wrap'); var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity; nodes.forEach(function(n) { var shape = n.tagName === 'a' ? n.querySelector('circle,rect') : n; if (!shape) return; var cx = parseFloat(shape.getAttribute('cx') || shape.getAttribute('x')); var cy = parseFloat(shape.getAttribute('cy') || shape.getAttribute('y')); var r = parseFloat(shape.getAttribute('r') || shape.getAttribute('width')) || 0; if (!isNaN(cx) && !isNaN(cy)) { minX = Math.min(minX, cx - r); minY = Math.min(minY, cy - r); maxX = Math.max(maxX, cx + r); maxY = Math.max(maxY, cy + r); } }); if (minX === Infinity) return; var pad = 40; minX -= pad; minY -= pad; maxX += pad; maxY += pad; var bw = maxX - minX; var bh = maxY - minY; var rect = wrap.getBoundingClientRect(); var vb = svg.getAttribute('viewBox').split(' '); var vw = parseFloat(vb[2]), vh = parseFloat(vb[3]); var base_s = Math.min(rect.width / vw, rect.height / vh); var cx = minX + bw / 2; var cy = minY + bh / 2; var ox = (rect.width - vw * base_s) / 2; var oy = (rect.height - vh * base_s) / 2; var px = ox + cx * base_s; var py = oy + cy * base_s; var s = Math.min(rect.width / (bw * base_s), rect.height / (bh * base_s)); if (s > 4) s = 4; var tx = (rect.width / 2 - px) * s; var ty = (rect.height / 2 - py) * s; if (!wrap._zoomState) wrap._zoomState = { s: 1, tx: 0, ty: 0 }; wrap._zoomState.s = s; wrap._zoomState.tx = tx; wrap._zoomState.ty = ty; svg.style.transition = 'transform 0.5s ease'; svg.style.transform = 'translate3d(' + tx + 'px,' + ty + 'px,0) scale(' + s + ')'; setTimeout(function() { svg.style.transition = ''; }, 500); nodes.forEach(function(n) { var shape = n.tagName === 'a' ? n.querySelector('circle,rect') : n; if (!shape) return; var oldStroke = shape.style.stroke || ''; var oldWidth = shape.style.strokeWidth || ''; shape.style.transition = 'stroke 0.2s, stroke-width 0.2s'; shape.style.stroke = '#fff'; shape.style.strokeWidth = '4px'; setTimeout(function() { shape.style.stroke = oldStroke; shape.style.strokeWidth = oldWidth; setTimeout(function() { shape.style.transition = ''; }, 200); }, 1000); }); }); });</script>
");
        return sb.ToString();
    }

    /// <summary>The menu sub-categories, in the order the side menu lists them.
    /// The gamma frontier belt is split into T0 (the tc transit zones) and T1–T4
    /// by zone number (the server stores no per-zone tier field; the split is a
    /// navigation grouping, noted on the page).</summary>
    internal static List<Group> Groups(List<Zone> all)
    {
        bool Is(string n, params string[] parts) =>
            parts.Any(p => n.Contains(p, System.StringComparison.OrdinalIgnoreCase));
        Zone? ByName(string n) => all.FirstOrDefault(z => z.Name == n);
        int GammaTier(Zone z)
        {
            if (!z.Name.StartsWith("zone_gamma_z", StringComparison.Ordinal)) return -1;
            if (!int.TryParse(z.Name["zone_gamma_z".Length..], out var n)) return -1;
            return n is >= 106 and <= 140 ? (n - 106) / 9 + 1 : -1;
        }
        string GammaBlurb(int t) => "Frontier belt islands with the server-recorded tier " +
            $"**T{t}** (zones.note). Open PvP and terraformable — see [Protection levels](/zones/protection/). " +
            "Each island's page has its ore configuration and TP connections.";;
        return new List<Group>
        {
            new("training", "Training",
                "The virtual [training island](/zones/zone-training/) — where new characters start and learn the basics before entering the main galaxies.",
                new List<Zone> { ByName("zone_training")! }),
            new("alpha", "Alpha",
                "The main protected islands and their second-wave PvE companions — the safe starter economy (see [Protection levels](/zones/protection/)).",
                all.Where(z => z.Name == "zone_TM" || z.Name == "zone_ICS" || z.Name == "zone_ASI"
                    || z.Name == "zone_TM_pve" || z.Name == "zone_ICS_pve" || z.Name == "zone_ASI_pve")
                    .OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("beta", "Beta",
                "The open-PvP islands: the three main islands' PvP twins (the \"_real\" names), the eight gate islands of each galaxy, " +
                "and the special zones (the [PvP arena](/zones/zone-pvp-arena/) and the strongholds — protected instances, listed here for completeness).",
                all.Where(z => z.Name != "zone_training" && !Is(z.Name, "gamma")
                    && (z.Protected == false || z.Type == 4))
                    .OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("t0", "Gamma T0 — tc transit",
                "The six small (256-tile) transit zones of the frontier belt. No ore configuration — pure travel nodes between the main galaxies and the belt.",
                all.Where(z => z.Name.Contains("tc", StringComparison.OrdinalIgnoreCase))
                    .OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("t1", "Gamma T1", GammaBlurb(1),
                all.Where(z => GammaTier(z) == 1).OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("t2", "Gamma T2", GammaBlurb(2),
                all.Where(z => GammaTier(z) == 2).OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("t3", "Gamma T3", GammaBlurb(3),
                all.Where(z => GammaTier(z) == 3).OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
            new("t4", "Gamma T4", GammaBlurb(4),
                all.Where(z => GammaTier(z) == 4).OrderBy(z => z.Name, StringComparer.Ordinal).ToList()),
        };
    }

    private static string Svg(
        List<Zone> all,
        Dictionary<string, Zone> byName,
        List<(string Src, string Dst, string Rift, double? Gx, double? Gy)> links,
        List<(string Src, string Dst, int Tps, double? Sx, double? Sy, double? Tx, double? Ty)> tps,
        Dictionary<string, List<(double Tx, double Ty, string Name)>> tpCols,
        double vbW, double vbH, Func<double, double> Px, Func<double, double> Py)
    {
        // A connection line's endpoint sits at the real spot in the zone —
        // the TP column's / landing's tile position mapped into the island
        // node's rectangle (zone-local y grows downward, like the screen).
        (double X, double Y) End(Zone z, double? tx, double? ty)
        {
            var size = Size(z.W);
            var cx = Px(z.X);
            var cy = Py(z.Y);
            if (tx is null || ty is null || z.W == 0 || z.H == 0) return (cx, cy);
            return (cx + (tx.Value / z.W - 0.5) * size, cy + (ty.Value / z.H - 0.5) * size);
        }

        var sb = new StringBuilder();
        // All zones are plotted (including those without TP connections like
        // training, strongholds, PvP arena) to mirror the in-game map.
        // Sentinel rows (x/y >= 49000) are excluded.
        // ASI_/TM_ zones with no TP links are removed (isolated duplicates).
        var tpConnected = new HashSet<string>(
            tps.Select(t => t.Src).Concat(tps.Select(t => t.Dst)),
            StringComparer.OrdinalIgnoreCase);
        var plotted = all.Where(z => z.X < 49000 && z.Y < 49000)
            .Where(z => {
                // Remove ASI/TM zones that have no TP connections (isolated duplicates)
                var n = z.Name.ToLowerInvariant();
                if ((n.Contains("asi") || n.Contains("tm")) && !n.Contains("gamma") && !tpConnected.Contains(z.Name))
                    return false;
                return true;
            }).ToList();
        var plottedSet = new HashSet<string>(plotted.Select(z => z.Name), StringComparer.Ordinal);
        sb.Append($"<svg viewBox=\"0 0 {vbW:0} {vbH:0}\" role=\"img\" aria-label=\"Map of all game zones with teleport connections, at their grid positions, coastline outlines colored by galaxy family\" class=\"zonemap\" xmlns=\"http://www.w3.org/2000/svg\">\n");
        sb.Append("  <title>Map of all game zones with teleport connections, at their grid positions</title>\n");
        // Dark ocean background (matches the in-game world map)
        sb.Append($"  <rect width=\"{vbW:0}\" height=\"{vbH:0}\" fill=\"#0a1628\"/>\n");
        // Inter-zone TP lines, dashed and gradient-colored from the source
        // island's family color to the destination's (one gradient per line,
        // anchored in userSpace so the gradient follows the line direction).
        sb.Append("  <defs>\n");
        for (var i = 0; i < tps.Count; i++)
        {
            var l = tps[i];
            if (!plottedSet.Contains(l.Src) || !plottedSet.Contains(l.Dst)) continue;
            if (!byName.TryGetValue(l.Src, out var s) || !byName.TryGetValue(l.Dst, out var d)) continue;
            var (ax, ay) = End(s, l.Sx, l.Sy);
            var (bx, by) = End(d, l.Tx, l.Ty);
            sb.Append($"    <linearGradient id=\"tpg{i}\" gradientUnits=\"userSpaceOnUse\" x1=\"{ax:0.#}\" y1=\"{ay:0.#}\" x2=\"{bx:0.#}\" y2=\"{by:0.#}\">\n");
            sb.Append($"      <stop offset=\"0\" stop-color=\"{FamilyColor(l.Src)}\"/>\n");
            sb.Append($"      <stop offset=\"1\" stop-color=\"{FamilyColor(l.Dst)}\"/>\n");
            sb.Append("    </linearGradient>\n");
        }
        sb.Append("  </defs>\n");
        // Small islands first so the big-island labels draw on top. The
        // connection lines come AFTER the nodes: they run over the islands and
        // touch the columns'/landing spots' real positions inside them.
        foreach (var z in plotted.OrderBy(z => Size(z.W)).ThenBy(z => z.Name, StringComparer.Ordinal))
        {
            var f = Family(z.Name);
            var size = Size(z.W);
            var x1 = Px(z.X);
            var y1 = Py(z.Y);
            var tip = $"{z.Name} — {ProtectionLabel(z)} · {TypeLabel(z.Type)} ({z.X:0} / {z.Y:0})";
            var slug = z.Name.ToLowerInvariant().Replace("_", "-");
            // Same design as the index cards: the coastline-only thumbnail
            // (thumb.png — family-color island border on the dark plate) over
            // the family-outlined shape.
            // Protection border: the shape is slightly larger than the terrain
            // image. Its fill is the protection color (visible border for PvP)
            // or the background color (invisible border for PVE/Alpha).
            var shape = $"<circle cx=\"{x1:0.#}\" cy=\"{y1:0.#}\" r=\"{size / 2:0.#}\" fill=\"#10151f\" class=\"zonemap-node-{f}\"><title>{tip}</title></circle>";
            var image = $"<image href=\"/zonemaps/{slug}/thumb.png\" x=\"{x1 - size / 2:0.#}\" y=\"{y1 - size / 2:0.#}\" width=\"{size:0.#}\" height=\"{size:0.#}\" preserveAspectRatio=\"none\"/>";
            // Landmark icons at real positions: base (dot) at center + teleports at tile coords.
            var iconR = Math.Max(0.4, size * 0.02);
            var baseIcon = $"<circle cx=\"{x1:0.#}\" cy=\"{y1:0.#}\" r=\"{iconR:0.#}\" fill=\"#c8d2e0\" class=\"zm-icon\"><title>{DisplayName(z.Name)} — Base</title></circle>";
            var tpIcons = "";
            if (tpCols.TryGetValue(z.Name, out var cols) && cols.Count > 0)
            {
                var zw = (double)z.W;
                var zh = (double)z.H;
                foreach (var col in cols)
                {
                    var tpx = x1 + (col.Tx / zw - 0.5) * size;
                    var tpy = y1 + (col.Ty / zh - 0.5) * size;
                    var label = col.Name.Replace("teleport_column_", "").Replace('_', ' ');
                    tpIcons += $"<polygon points=\"{HexPoints(tpx, tpy, iconR * 1.2)}\" fill=\"none\" stroke=\"#c8d2e0\" stroke-width=\"0.5\" class=\"zm-icon\"><title>{DisplayName(z.Name)} — {label}</title></polygon>";
                }
            }
            var icons = baseIcon + tpIcons;
            // Label ABOVE the island, centered, scaled down so it never
            // overhangs the island's own width (the map stays readable at
            // rest; zoom in for the small islands).
            var displayName = DisplayName(z.Name);
            var fontSize = Math.Min(7, size / (0.62 * displayName.Length));
            if (fontSize < 0.9) fontSize = 0.9;
            var text = $"<text x=\"{x1:0.#}\" y=\"{y1 - size / 2 - 1.2:0.#}\" text-anchor=\"middle\" font-size=\"{fontSize:0.##}\" class=\"zonemap-label\">{displayName}</text>";
            var href = PageLink(z.Name);
            sb.Append($"  <a href=\"{href}\"><g>{shape}{image}{icons}{text}</g></a>\n");
        }
        for (var i = 0; i < tps.Count; i++)
        {
            var l = tps[i];
            if (!plottedSet.Contains(l.Src) || !plottedSet.Contains(l.Dst)) continue;
            if (!byName.TryGetValue(l.Src, out var s) || !byName.TryGetValue(l.Dst, out var d)) continue;
            var (ax, ay) = End(s, l.Sx, l.Sy);
            var (bx, by) = End(d, l.Tx, l.Ty);
            sb.Append($"  <line x1=\"{ax:0.#}\" y1=\"{ay:0.#}\" x2=\"{bx:0.#}\" y2=\"{by:0.#}\" class=\"zonemap-tp\" stroke=\"url(#tpg{i})\" data-tps=\"{l.Src}\" data-tpd=\"{l.Dst}\">" +
                      $"<title>{l.Src} — {l.Dst} ({l.Tps} TP point{(l.Tps > 1 ? "s" : "")})</title></line>\n");
        }

        sb.Append("</svg>\n");
        return sb.ToString();
    }

    /// <summary>Case-insensitive: the main zones are uppercase (zone_TM) while the gate
    private static readonly System.Collections.Generic.Dictionary<string, string> GammaFam = new()
    {
        {"zone_gamma_tc_z100", "tm"}, {"zone_gamma_tc_z101", "tm"}, {"zone_gamma_tc_z102", "asi"},
        {"zone_gamma_tc_z103", "asi"}, {"zone_gamma_tc_z104", "ics"}, {"zone_gamma_tc_z105", "ics"},
        {"zone_gamma_z106", "tm"}, {"zone_gamma_z107", "asi"}, {"zone_gamma_z108", "asi"},
        {"zone_gamma_z109", "asi"}, {"zone_gamma_z110", "asi"}, {"zone_gamma_z111", "ics"},
        {"zone_gamma_z112", "tm"}, {"zone_gamma_z113", "tm"}, {"zone_gamma_z114", "asi"},
        {"zone_gamma_z115", "asi"}, {"zone_gamma_z116", "asi"}, {"zone_gamma_z117", "asi"},
        {"zone_gamma_z118", "asi"}, {"zone_gamma_z119", "asi"}, {"zone_gamma_z120", "asi"},
        {"zone_gamma_z121", "asi"}, {"zone_gamma_z122", "asi"}, {"zone_gamma_z123", "asi"},
        {"zone_gamma_z124", "tm"}, {"zone_gamma_z125", "tm"}, {"zone_gamma_z126", "tm"},
        {"zone_gamma_z127", "tm"}, {"zone_gamma_z128", "tm"}, {"zone_gamma_z129", "tm"},
        {"zone_gamma_z130", "tm"}, {"zone_gamma_z131", "tm"}, {"zone_gamma_z132", "ics"},
        {"zone_gamma_z133", "ics"}, {"zone_gamma_z134", "ics"}, {"zone_gamma_z135", "ics"},
        {"zone_gamma_z136", "ics"}, {"zone_gamma_z137", "ics"}, {"zone_gamma_z138", "ics"},
        {"zone_gamma_z139", "asi"}, {"zone_gamma_z140", "asi"}
    };

    private static string Family(string name)
    {
        var n = name.ToLowerInvariant();
        if (GammaFam.TryGetValue(n, out var f)) return f;
        return n.Contains("tm") ? "tm"
             : n.Contains("ics") ? "ics"
             : n.Contains("asi") ? "asi"
             : "special";
    }

    /// <summary>Same family colors as the zone teleport maps (ZoneMapSvg).</summary>
    private static string FamilyColor(string name) =>
        Family(name) switch
        {
            "tm" => "#41d3ff",
            "ics" => "#6ee7a0",
            "asi" => "#f5a05a",
            _ => "#c8d2e0",
        };

    /// <summary>SVG polygon points for a regular hexagon centered at (cx,cy) with radius r.</summary>
    private static string HexPoints(double cx, double cy, double r)
    {
        var pts = new System.Text.StringBuilder();
        for (var i = 0; i < 6; i++)
        {
            var angle = Math.PI / 3 * i - Math.PI / 6;
            var px = cx + r * Math.Cos(angle);
            var py = cy + r * Math.Sin(angle);
            if (i > 0) pts.Append(' ');
            pts.Append($"{px:0.#},{py:0.#}");
        }
        return pts.ToString();
    }

    private static string Escape(string s) => s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt>");

    /// <summary>Human form of a zone definition name for the map labels —
    /// the DB carries no client display names, so derive one: tokens are
    /// space-joined, short tokens uppercased (tc, pve, z, g), the rest
    /// title-cased, existing acronyms kept (ASI, TM). zone_gamma_tc_z106
    /// -> "Gamma TC Z106"; zone_asi_a_real -> "ASI A Real".</summary>
    private static string DisplayName(string name)
    {
        var n = name.StartsWith("zone_", StringComparison.Ordinal) ? name[5..] : name;
        var sb = new System.Text.StringBuilder();
        foreach (var token in n.Split('_'))
        {
            if (token.Length == 0) continue;
            int letters = 0;
            while (letters < token.Length && char.IsLetter(token[letters])) letters++;
            var letterPart = token[..letters];
            var rest = token[letters..];
            string part;
            if (letterPart == letterPart.ToUpperInvariant())
                part = letterPart; // already an acronym (ASI, TM, ICS)
            else if (letterPart.Length <= 3)
                part = letterPart.ToUpperInvariant(); // tc -> TC, pve -> PVE, z -> Z
            else
                part = char.ToUpperInvariant(letterPart[0]) + letterPart[1..].ToLowerInvariant();
            if (sb.Length > 0) sb.Append(' ');
            sb.Append(part).Append(rest);
        }
        return sb.ToString();
    }

    /// <summary>Protection level straight from the zones flags
    /// (ZoneConfiguration.IsAlpha/IsBeta/IsGamma): alpha = protected,
    /// gamma = terraformable, beta = the open rest.</summary>
    private static string ProtectionLabel(Zone z)
    {
        if (z.Protected) return "protected (alpha)";
        if (z.Name.EndsWith("_real", System.StringComparison.OrdinalIgnoreCase)) return "protected (alpha)";
        if (z.Name.EndsWith("_pve", System.StringComparison.OrdinalIgnoreCase)) return "protected (alpha)";
        if (z.Name.Contains("gamma", System.StringComparison.OrdinalIgnoreCase)) return "open (gamma)";
        if (z.Name.EndsWith("_pvp", System.StringComparison.OrdinalIgnoreCase)) return "open (beta)";
        return z.Terraformable ? "open (gamma)" : "open (beta)";
    }

    /// <summary>Outer outline color by protection level.
    /// PVE: null (no extra outline). PvP Beta + Gamma TC: yellow. PvP Gamma: red.</summary>
    private static string? ProtectionColor(Zone z)
    {
        // PVE zones: no extra outline
        if (z.Protected) return null;
        if (z.Name.Contains("_pve")) return null;
        if (z.Name.Contains("training")) return null;
        if (z.Type == 1) return null; // PvE type
        // Gamma TC zones: gamma color (treated as Gamma for color)
        if (z.Name.Contains("gamma_tc")) return "#a78bfa";
        // Gamma zones: red
        if (z.Name.Contains("gamma_z")) return "#ef4444";
        // Beta zones (g_1 through g_8): yellow
            z.Name.Contains("_g3") || z.Name.Contains("_g4") || z.Name.Contains("_g5") ||
            z.Name.Contains("_g6") || z.Name.Contains("_g7") || z.Name.Contains("_g8"))
            return "#fbbf24";
        // Other PvP (alpha PVP zones, arenas, strongholds): yellow
        return "#fbbf24";
    }

    private static string TypeLabel(int t) => t switch
    {
        1 => "PvE",
        2 => "PvP",
        3 => "Training",
        4 => "Stronghold",
        _ => "Undefined",
    };

    internal static string ZoneName(string n)
    {
        if (Md.ClientStrings.TryGetValue(n, out var d) && d != n) return d;
        return n.StartsWith("zone_", StringComparison.Ordinal) ? n[5..] : n;
    }

    /// <summary>Page for a zone — every zone has its own page (the three worked
    /// examples are hand-written, the rest generated; same slug scheme).</summary>
    private static string PageLink(string name) =>
        "/zones/" + name.ToLowerInvariant().Replace("_", "-") + "/";
}
