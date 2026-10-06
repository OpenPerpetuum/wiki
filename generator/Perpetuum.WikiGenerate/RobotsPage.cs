namespace Perpetuum.WikiGenerate;

public static class RobotsPage
{
    // Robot class bits encoded in the high part of categoryflags (see CategoryFlags:
    // cf_runner_head = 0x10150, cf_crawler_head = 0x20150, cf_mech_head = 0x30150,
    // cf_heavymech_head = 0x40150, cf_walker_head = 0x50150).
    private const long BitRunner = 0x10000, BitCrawler = 0x20000, BitMech = 0x30000,
                       BitHeavyMech = 0x40000, BitWalker = 0x50000;

    // (Bit, Name, Intro, Combat, Speed, Armor, Storage, Cost) — ratings 1–5
    private static readonly (long Bit, string Name, string Intro, int Combat, int Speed, int Armor, int Storage, int Cost)[] Archetypes =
    {
        (BitRunner, "Runners", "The fast, light class — the cheapest robots to build and pilot.", 1, 5, 1, 2, 1),
        (BitCrawler, "Crawlers", "The mid-size workhorse class.", 2, 3, 2, 4, 2),
        (BitMech, "Mechs", "The main combat class.", 4, 2, 3, 3, 3),
        (BitHeavyMech, "Heavy mechs", "The top-tier combat class.", 5, 1, 4, 3, 5),
        (BitWalker, "Walkers", "A rare heavy platform class.", 5, 1, 5, 4, 5),
    };

    public static string Build(Db db, Dictionary<int, DefRow> defs, Dictionary<int, List<string>> statsByDef)
    {
        var robots = db.Query("SELECT definition, definitionname, categoryflags, enabled, hidden, volume, mass, health, tiertype, tierlevel FROM entitydefaults WHERE definitionname LIKE '%_bot' AND enabled = 1 AND hidden = 0 AND definitionname NOT LIKE '%tutorial%' AND definitionname NOT LIKE '%spectator%' ORDER BY definitionname")
            .Select(r => new DefRow(r.Int("definition"), r.Str("definitionname"), 0, r.Lng("categoryflags"),
                "", "", r.Bit("enabled"), r.Bit("hidden"), r.Dbl("volume"), r.Dbl("mass"), r.Dbl("health"), 0, r.Int("tiertype"), r.Int("tierlevel")))
            .ToList();

        var purchasable = db.Query("SELECT definition, purchasable FROM entitydefaults WHERE definitionname LIKE '%_bot'")
            .ToDictionary(r => r.Int("definition"), r => r.Bit("purchasable"));

        var turrets = robots.Where(d => d.Name.Contains("turret")).ToList();
        var hybrids = robots.Where(d => d.Name.Contains("hybrid")).ToList();
        // "syndicate forces" entries are named fits (volume 0, no class bits): complete
        // loadouts unlocked through the tech tree rather than standalone chassis.
        var namedFits = robots.Where(d => d.Name.Contains("syndicate")).ToList();
        bool NotPurchasable(DefRow d) => !purchasable.TryGetValue(d.Definition, out var p) || !p;
        var npc = robots.Where(d => (!d.Name.Contains("turret") && !d.Name.Contains("hybrid") && NotPurchasable(d))
                                     || (namedFits.Contains(d) && NotPurchasable(d))).ToList();
        var player = robots.Where(d => !turrets.Contains(d) && !hybrids.Contains(d) && !namedFits.Contains(d) && !npc.Contains(d)).ToList();
        var playerNamedFits = namedFits.Where(d => !npc.Contains(d)).ToList();

        var classGroups = Archetypes
            .Select(a => (a.Bit, a.Name, a.Intro, a.Combat, a.Speed, a.Armor, a.Storage, a.Cost, Rows: player.Where(d => ClassOf(d) == a.Bit).ToList()))
            .ToList();
        var special = (Name: "Starter & special",
            Intro: "The starter bot, the flagship and limited/event models.",
            Rows: player.Where(d => ClassOf(d) == 0).ToList());

        var sb = new StringBuilder();
        sb.Append(Md.Header("Robots", "How a robot is built, the robot classes, and every robot: player, hybrid and NPC.",
            "entitydefaults (complete robot definitions, robot class part flags, purchasable flag)"));
        sb.Append("\n\n# Robots\n\n");
        sb.Append("Fitting, slots and in-game play are covered in the [Robot](/features/robots/) feature page; this page is the data reference.\n\n");

        // Robot classes with icon-based ratings
        sb.Append("## Robot classes\n\n");
        sb.Append("A robot's class comes from its parts. Ratings are 1–5 (more icons = higher).\n\n");
        sb.Append(RatingsTableHtml());
        sb.Append("\n");

        sb.Append("## Player robots\n\n");
        sb.Append($"Robots you can acquire and control yourself ({player.Count} models), grouped by class.\n\n");

        foreach (var (bit, name, intro, combat, speed, armor, storage, cost, rows) in classGroups)
        {
            if (rows.Count == 0) continue;
            sb.Append($"### {name} ({rows.Count})\n\n");
            sb.Append(intro + "\n\n");
            WriteFamilies(sb, rows, combat, speed, armor, storage, cost);
        }
        if (special.Rows.Count > 0)
        {
            sb.Append($"### {special.Name} ({special.Rows.Count})\n\n");
            sb.Append(special.Intro + "\n\n");
            WriteFamilies(sb, special.Rows, 3, 3, 3, 2, 3);
        }

        if (playerNamedFits.Count > 0)
        {
            sb.Append($"### Named fits ({playerNamedFits.Count})\n\n");
            sb.Append("Complete cult-designed loadouts unlocked through research — a finished fit rather than a standalone chassis (size comes from the parts it is built from).\n\n");
            Md.WriteTable(sb, new[] { "Robot", "Class" },
                playerNamedFits.Select(d => new[] { Md.DisplayName(d.Name), ClassName(ClassOf(d)) }).ToArray());
            sb.Append("\n*Strengths:* a ready-made combat build with its role in the name (main combat / main support).\n");
            sb.Append("*Weaknesses:* fixed by the design — you take the fit as it comes.\n\n");
        }

        if (hybrids.Count > 0)
        {
            sb.Append($"## Hybrid builds ({hybrids.Count})\n\n");
            sb.Append("Mixed-class builds assembled from parts of different robot classes rather than one pure class. They are built from parts, not sold as a finished robot; the finished size comes from the parts chosen.\n\n");
            Md.WriteTable(sb, new[] { "Robot" },
                hybrids.Select(d => new[] { Md.DisplayName(d.Name) }).ToArray());
            sb.Append("\n*Strengths:* mix the advantages of several classes in one build.\n");
            sb.Append("*Weaknesses:* you must assemble the parts yourself — no single finished product to buy.\n\n");
        }

        if (npc.Count > 0)
        {
            sb.Append($"## NPC units ({npc.Count})\n\n");
            sb.Append("Combat units fielded by the NPC factions (not acquirable by players).\n\n");
            Md.WriteTable(sb, new[] { "Unit" },
                npc.Select(d => new[] { Md.DisplayName(d.Name) }).ToArray());
            sb.Append('\n');
        }

        return sb.ToString();
    }

    /// <summary>Ratings 1-5 as repeated icon characters.</summary>
    private static string Rating(int n, string icon) => string.Concat(Enumerable.Repeat(icon, Math.Clamp(n, 0, 5)));

    /// <summary>HTML table of class ratings with icon columns.</summary>
    private static string RatingsTableHtml()
    {
        var sb = new StringBuilder();
        sb.Append("<table class=\"class-ratings\">\n");
        sb.Append("<thead><tr><th>Class</th><th>Combat</th><th>Speed</th><th>Armor</th><th>Storage</th><th>Cost</th></tr></thead>\n");
        sb.Append("<tbody>\n");
        foreach (var (_, name, _, combat, speed, armor, storage, cost) in Archetypes)
        {
            sb.Append($"<tr><td><b>{name}</b></td>");
            sb.Append($"<td class=\"rating\" title=\"{combat}/5\">{Rating(combat, "⚔")}</td>\n");
            sb.Append($"<td class=\"rating\" title=\"{speed}/5\">{Rating(speed, "»")}</td>\n");
            sb.Append($"<td class=\"rating\" title=\"{armor}/5\">{Rating(armor, "■")}</td>\n");
            sb.Append($"<td class=\"rating\" title=\"{storage}/5\">{Rating(storage, "□")}</td>\n");
            sb.Append($"<td class=\"rating\" title=\"{cost}/5\">{Rating(cost, "$")}</td>\n");
            sb.Append("</tr>\n");
        }
        sb.Append("</tbody></table>\n");
        return sb.ToString();
    }

    /// <summary>ID-card layout per model family: icon on the left, ratings + info on the right.</summary>
    private static void WriteFamilies(StringBuilder sb, List<DefRow> rows, int combat, int speed, int armor, int storage, int cost)
    {
        sb.Append("<div class=\"robot-cards\">\n");
        foreach (var family in rows.GroupBy(FamilyKey).OrderBy(f => f.Key, StringComparer.Ordinal))
        {
            var frows = family
                .OrderBy(d => d.Name.Contains("_mk2") ? 1 : d.Name.Contains("_reward") ? 2 : 0)
                .ThenBy(d => d.Name, StringComparer.Ordinal)
                .ToList();
            var title = Md.DisplayName(family.Key);
            var size = frows[0].Volume;

            var slug = family.Key.Replace("def_", "").Replace("_bot", "").Replace('_', '-').ToLowerInvariant();
            sb.Append($"<a class=\"robot-card\" href=\"/content/robots/{slug}/\">\n");
            // Left: icon
            sb.Append("<div class=\"robot-card-img\">\n");
            if (RobotIcons.TryGetValue(title, out var ic))
                sb.Append($"<img src=\"/img/robots/{ic}\" alt=\"{title}\">\n");
            else
                sb.Append($"<span class=\"robot-icon icon-mask\" role=\"img\" aria-label=\"{title} icon\"></span>\n");
            sb.Append("</div>\n");
            // Right: info
            sb.Append("<div class=\"robot-card-info\">\n");
            sb.Append("<div class=\"robot-card-header\">\n");
            sb.Append($"<div class=\"robot-card-name\">{title}</div>\n");
            sb.Append($"<div class=\"robot-card-size\">{size:0.#}</div>\n");
            sb.Append("</div>\n");
            sb.Append("<ul class=\"robot-card-stats\">\n");
            sb.Append($"<li><b>{Rating(combat, "⚔")}</b><span>Combat</span></li>\n");
            sb.Append($"<li><b>{Rating(speed, "»")}</b><span>Speed</span></li>\n");
            sb.Append($"<li><b>{Rating(armor, "■")}</b><span>Armor</span></li>\n");
            sb.Append($"<li><b>{Rating(storage, "□")}</b><span>Storage</span></li>\n");
            sb.Append($"<li><b>{Rating(cost, "$")}</b><span>Cost</span></li>\n");
            sb.Append("</ul>\n");
            sb.Append("</div>\n");
            sb.Append("</a>\n");
        }
        sb.Append("</div>\n\n");
    }

    /// <summary>Model family key: the definition name without generation/reward suffixes.</summary>
    private static string FamilyKey(DefRow d) => d.Name.Replace("_mk2", "").Replace("_reward1", "");

    /// <summary>Display name -> static icon file (static/img/robots/). Empty for
    /// now: the community-wiki icons were removed from the repo and the client
    /// archive is not an allowed source. Families with no entry fall back to
    /// placeholder.svg; add licensed icons here when available.</summary>
    private static readonly Dictionary<string, string> RobotIcons = new(StringComparer.OrdinalIgnoreCase)
    {
    };

    /// <summary>Class by priority (higher classes set the lower class bits too).</summary>
    private static long ClassOf(DefRow d)
    {
        if ((d.CatFlags & BitWalker) == BitWalker) return BitWalker;
        if ((d.CatFlags & BitHeavyMech) == BitHeavyMech) return BitHeavyMech;
        if ((d.CatFlags & BitMech) == BitMech) return BitMech;
        if ((d.CatFlags & BitCrawler) == BitCrawler) return BitCrawler;
        if ((d.CatFlags & BitRunner) == BitRunner) return BitRunner;
        return 0;
    }

    private static string ClassName(long c) => c switch
    {
        BitRunner => "Runner",
        BitCrawler => "Crawler",
        BitMech => "Mech",
        BitHeavyMech => "Heavy mech",
        BitWalker => "Walker",
        _ => "—",
    };
}
