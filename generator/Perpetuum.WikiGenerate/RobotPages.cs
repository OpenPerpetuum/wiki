using System.Text;

namespace Perpetuum.WikiGenerate;

/// <summary>Generates individual robot pages at /content/robots/&lt;slug&gt;/.</summary>
public static class RobotPages
{
    private const long BitRunner = 0x10000, BitCrawler = 0x20000, BitMech = 0x30000,
                       BitHeavyMech = 0x40000, BitWalker = 0x50000;

    private static (int Combat, int Speed, int Armor, int Storage, int Cost) ClassRating(long catFlags)
    {
        if ((catFlags & BitWalker) == BitWalker) return (5, 1, 5, 4, 5);
        if ((catFlags & BitHeavyMech) == BitHeavyMech) return (5, 1, 4, 3, 5);
        if ((catFlags & BitMech) == BitMech) return (4, 2, 3, 3, 3);
        if ((catFlags & BitCrawler) == BitCrawler) return (2, 3, 2, 4, 2);
        if ((catFlags & BitRunner) == BitRunner) return (1, 5, 1, 2, 1);
        return (3, 3, 3, 2, 3); // special/unknown
    }

    private static string Rating(int n, string icon) => string.Concat(Enumerable.Repeat(icon, Math.Clamp(n, 0, 5)));

    private static string Slug(string def) => def.Replace("def_", "").Replace("_bot", "").Replace('_', '-');

    public static List<(string File, string Md)> Build(Db db, Dictionary<int, DefRow> defs)
    {
        // Load all robot definitions
        var robots = db.Query("SELECT definition, definitionname, categoryflags, volume, mass, health, tiertype, tierlevel, purchasable FROM entitydefaults WHERE definitionname LIKE '%_bot' AND enabled = 1 AND hidden = 0 AND definitionname NOT LIKE '%tutorial%' AND definitionname NOT LIKE '%spectator%' ORDER BY definitionname")
            .Select(r => (
                Id: r.Int("definition"),
                Name: r.Str("definitionname"),
                CatFlags: r.Lng("categoryflags"),
                Volume: r.Dbl("volume"),
                Mass: r.Dbl("mass"),
                Health: r.Dbl("health"),
                Tier: r.Int("tiertype"),
                TierLevel: r.Int("tierlevel"),
                Purchasable: r.Bit("purchasable")))
            .ToList();

        // Load components (recipes)
        var components = db.Query("SELECT definition, componentdefinition, componentamount FROM components WHERE definition IN (SELECT definition FROM entitydefaults WHERE definitionname LIKE '%_bot')")
            .Select(r => (Def: r.Int("definition"), Comp: r.Int("componentdefinition"), Amount: r.Int("componentamount")))
            .ToList();

        // Load shop entries
        var shop = db.Query("SELECT targetdefinition, tmcoin, icscoin, asicoin, credit FROM itemshop WHERE targetdefinition IN (SELECT definition FROM entitydefaults WHERE definitionname LIKE '%_bot')")
            .GroupBy(r => r.Int("targetdefinition"))
            .ToDictionary(g => g.Key, g => g.First());

        var pages = new List<(string, string)>();

        foreach (var bot in robots)
        {
            var slug = Slug(bot.Name);
            var display = Md.DisplayName(bot.Name);
            var (combat, speed, armor, storage, cost) = ClassRating(bot.CatFlags);
            var cls = ClassName(bot.CatFlags);
            var botComps = components.Where(c => c.Def == bot.Id).ToList();
            var shopEntry = shop.TryGetValue(bot.Id, out var s) ? s : null;

            // Find variants (same family)
            var baseName = bot.Name.Replace("_mk2", "").Replace("_mk3", "").Replace("_reward1", "");
            var variants = robots.Where(r => r.Name.Replace("_mk2", "").Replace("_mk3", "").Replace("_reward1", "") == baseName && r.Id != bot.Id).ToList();

            var sb = new StringBuilder();
            sb.Append(Md.Header(display, $"{display} — robot stats, production and availability.",
                "entitydefaults, components, itemshop"));
            sb.Append($"\n\n# {display}\n\n");

            // Top row: card (left) + property table (right)
            sb.Append("<div class=\"robot-page-top\">\n");
            sb.Append("<div class=\"robot-card robot-page-card\">\n");
            sb.Append("<div class=\"robot-card-img\">\n");
            sb.Append($"<span class=\"robot-icon icon-mask\" role=\"img\" aria-label=\"{display} icon\"></span>\n");
            sb.Append("</div>\n");
            sb.Append("<div class=\"robot-card-info\">\n");
            sb.Append("<div class=\"robot-card-header\">\n");
            sb.Append($"<div class=\"robot-card-name\">{display}</div>\n");
            sb.Append($"<div class=\"robot-card-size\">{bot.Volume:0.#}</div>\n");
            sb.Append("</div>\n");
            sb.Append($"<ul class=\"robot-card-stats\">\n");
            sb.Append($"<li><b>{Rating(combat, "⚔")}</b><span>Combat</span></li>\n");
            sb.Append($"<li><b>{Rating(speed, "»")}</b><span>Speed</span></li>\n");
            sb.Append($"<li><b>{Rating(armor, "■")}</b><span>Armor</span></li>\n");
            sb.Append($"<li><b>{Rating(storage, "□")}</b><span>Storage</span></li>\n");
            sb.Append($"<li><b>{Rating(cost, "$")}</b><span>Cost</span></li>\n");
            sb.Append($"</ul>\n");
            sb.Append("</div>\n");
            sb.Append("</div>\n");
            sb.Append("<div class=\"robot-page-props\">\n");
            sb.Append("<table class=\"robot-props-table\">\n");
            sb.Append($"<tr><td>Class</td><td>{cls}</td></tr>\n");
            sb.Append($"<tr><td>Size</td><td>{bot.Volume:0.#}</td></tr>\n");
            sb.Append($"<tr><td>Mass</td><td>{bot.Mass:0.#}</td></tr>\n");
            sb.Append($"<tr><td>Health</td><td>{bot.Health:0.#}</td></tr>\n");
            if (bot.Tier > 0)
                sb.Append($"<tr><td>Tier</td><td>T{bot.TierLevel}</td></tr>\n");
            sb.Append($"<tr><td>Purchasable</td><td>{(bot.Purchasable ? "Yes" : "No")}</td></tr>\n");
            sb.Append("</table>\n");
            sb.Append("</div>\n");
            sb.Append("</div>\n\n");

            // Variants (before production)
            if (variants.Count > 0)
            {
                sb.Append("## Variants\n\n");
                sb.Append("| Variant | Link |\n|---|---|\n");
                foreach (var v in variants)
                {
                    var vSlug = Slug(v.Name);
                    var vName = Md.DisplayName(v.Name);
                    sb.Append($"| {vName} | [/{vSlug}/](/content/robots/{vSlug}/) |\n");
                }
                sb.Append('\n');
            }

            // Production / Recipe
            if (botComps.Count > 0)
            {
                sb.Append("## Production\n\n");
                sb.Append("Components required to build this robot:\n\n");
                sb.Append("| Component | Amount |\n|---|---|\n");
                foreach (var c in botComps.OrderBy(c => c.Comp))
                {
                    var compDef = defs.TryGetValue(c.Comp, out var cd) ? cd.Name : $"def_{c.Comp}";
                    var compName = Md.DisplayName(compDef);
                    string link;
                    if (compDef.Contains("_bot"))
                        link = $"/content/robots/{Slug2(compDef)}/";
                    else if (compDef.Contains("_ore"))
                        link = $"/content/ores/{Slug2(compDef)}/";
                    else if (compDef.Contains("_plant"))
                        link = $"/content/plants/{Slug2(compDef)}/";
                    else
                        link = $"/content/items/{Slug2(compDef)}/";
                    sb.Append($"| [{compName}]({link}) | {c.Amount:N0} |\n");
                }
                sb.Append('\n');
            }

            // Vendor / Shop
            if (shopEntry != null)
            {
                sb.Append("## NPC Vendor\n\n");
                sb.Append("Available from the NPC vendor:\n\n");
                var prices = new List<string>();
                if (shopEntry["tmcoin"] is int tm && tm > 0) prices.Add($"{tm:N0} TM Coins");
                if (shopEntry["icscoin"] is int ics && ics > 0) prices.Add($"{ics:N0} ICS Coins");
                if (shopEntry["asicoin"] is int asi && asi > 0) prices.Add($"{asi:N0} ASI Coins");
                if (shopEntry["credit"] is double credit && credit > 0) prices.Add($"{credit:N0} ¤");
                sb.Append($"**Price:** {string.Join(" + ", prices)}\n\n");
            }

            pages.Add(($"robots/{slug}.md", sb.ToString()));
        }

        return pages;
    }

    private static string Slug2(string def)
    {
        // Zola URL slug: lowercase, underscores become hyphens, strip _bot suffix
        return def.Replace("def_", "").Replace("_bot", "").Replace('_', '-');
    }

    private static string ClassName(long c)
    {
        if ((c & BitWalker) == BitWalker) return "Walker";
        if ((c & BitHeavyMech) == BitHeavyMech) return "Heavy mech";
        if ((c & BitMech) == BitMech) return "Mech";
        if ((c & BitCrawler) == BitCrawler) return "Crawler";
        if ((c & BitRunner) == BitRunner) return "Runner";
        return "Special";
    }
}
