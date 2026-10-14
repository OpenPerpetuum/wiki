#!/usr/bin/env python3
"""Generate static/menu_tree.json from the sidenav in templates/base.html.

The sidenav (id="sidenav") is the single source of truth for the menu tree.
Each link becomes one entry:

    {"l": <label>, "u": <href>, "p": [<ancestor labels>, ...]}

  l — the link's data-i18n key when present (e.g. "nav_research"), otherwise
      the literal text (e.g. "Ammo", "Common 1" — proper nouns that stay
      English). The runtime resolves nav_* keys through window.WIKI_I18N, so
      the same file serves every language.
  u — the href, fragment included ("/zones/gamma/#t0").
  p — ancestor link labels (group heads / sub-heads), innermost last; used
      by search.js as the result breadcrumb.

search.js merges these entries into the page index (static/search_index.json):
a fragmentless menu link that matches a page URL adds its label to that
page's search space (no duplicate rows); anchor links (and links to pages
missing from the index) become their own result rows, so clicking a result
lands on the right page/section.

Pure standard library. Usage: python3 tools/gen_menu_tree.py [repo-root]
"""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path


class SidenavParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_nav = False
        self.entries = []
        self.ancestors = []
        self.li_stack = []   # per <li>: {'label': ..., 'pushed': bool}
        self.in_link = False
        self.cur_href = None
        self.cur_i18n = None
        self.cur_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "nav" and a.get("id") == "sidenav":
            self.in_nav = True
            return
        if not self.in_nav:
            return
        if tag == "li":
            self.li_stack.append({"label": None, "pushed": False})
        elif tag == "a":
            self.in_link = True
            self.cur_href = a.get("href")
            self.cur_i18n = a.get("data-i18n")
            self.cur_text = []
        elif self.in_link:
            # group-head links carry data-i18n on the inner <span>, not the <a>
            if a.get("data-i18n"):
                self.cur_i18n = a.get("data-i18n")
        elif tag == "ul" and self.li_stack:
            # A <ul> directly under a <li> whose first link is its head:
            # that link becomes the ancestor of everything inside.
            top = self.li_stack[-1]
            if top["label"] is not None and not top["pushed"]:
                self.ancestors.append(top["label"])
                top["pushed"] = True

    def handle_data(self, data):
        if self.in_nav and self.in_link:
            self.cur_text.append(data)

    def handle_endtag(self, tag):
        if tag == "nav" and self.in_nav:
            self.in_nav = False
            return
        if not self.in_nav:
            return
        if tag == "a" and self.in_link:
            self.in_link = False
            label = self.cur_i18n or " ".join("".join(self.cur_text).split())
            if self.cur_href and label:
                self.entries.append(
                    {"l": label, "u": self.cur_href, "p": list(self.ancestors)}
                )
                if self.li_stack and self.li_stack[-1]["label"] is None:
                    self.li_stack[-1]["label"] = label
        elif tag == "li" and self.li_stack:
            top = self.li_stack.pop()
            if top["pushed"]:
                self.ancestors.pop()


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    template = root / "templates" / "base.html"
    parser = SidenavParser()
    parser.feed(template.read_text(encoding="utf-8"))
    if not parser.entries:
        print("gen_menu_tree: no links found in templates/base.html sidenav",
              file=sys.stderr)
        sys.exit(1)
    out = root / "static" / "menu_tree.json"
    out.write_text(json.dumps(parser.entries, separators=(",", ":")) + "\n",
                   encoding="utf-8")
    print(f"gen_menu_tree: {len(parser.entries)} menu entries -> {out}")


if __name__ == "__main__":
    main()
