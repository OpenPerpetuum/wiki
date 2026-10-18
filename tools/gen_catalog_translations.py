#!/usr/bin/env python3
"""Generate translated versions of the item catalog and components pages.

Reads the English catalog pages from content/content/catalog/ and
content/content/components.md, translates the prose/headers, adds
language-prefixed links, and writes to content/{lang}/content/catalog/
and content/{lang}/content/components.md.

Usage: python3 tools/gen_catalog_translations.py
"""

import re
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

REPO = Path(__file__).resolve().parent.parent
CATALOG_DIR = REPO / "content" / "content" / "catalog"
COMPONENTS_PAGE = REPO / "content" / "content" / "components.md"

LANGS = ["cs", "de", "es", "fr", "it", "ja", "ko", "nl", "pl", "pt", "ru", "zh-CN", "zh-TW"]

# Translations for catalog page titles and prose
T = {
    "en": {
        "items_word": "items",
        "catalog_title": "Item catalog",
        "catalog_body": "Browse all items grouped by category.",
    },
    "cs": {
        "items_word": "položek",
        "catalog_title": "Katalog položek",
        "catalog_body": "Prohledejte všechny položky podle kategorie.",
    },
    "de": {
        "items_word": "Artikel",
        "catalog_title": "Artikelkatalog",
        "catalog_body": "Durchsuche alle Artikel nach Kategorie.",
    },
    "es": {
        "items_word": "artículos",
        "catalog_title": "Catálogo de artículos",
        "catalog_body": "Explora todos los artículos por categoría.",
    },
    "fr": {
        "items_word": "articles",
        "catalog_title": "Catalogue d'articles",
        "catalog_body": "Parcourez tous les articles par catégorie.",
    },
    "it": {
        "items_word": "oggetti",
        "catalog_title": "Catalogo oggetti",
        "catalog_body": "Sfoglia tutti gli oggetti per categoria.",
    },
    "ja": {
        "items_word": "アイテム",
        "catalog_title": "アイテムカタログ",
        "catalog_body": "カテゴリ別にすべてのアイテムを閲覧します。",
    },
    "ko": {
        "items_word": "개 항목",
        "catalog_title": "아이템 카탈로그",
        "catalog_body": "카테고리별로 모든 항목을 탐색합니다.",
    },
    "nl": {
        "items_word": "artikelen",
        "catalog_title": "Artikelencatalogus",
        "catalog_body": "Blader door alle artikelen per categorie.",
    },
    "pl": {
        "items_word": "przedmiotów",
        "catalog_title": "Katalog przedmiotów",
        "catalog_body": "Przeglądaj wszystkie przedmioty według kategorii.",
    },
    "pt": {
        "items_word": "itens",
        "catalog_title": "Catálogo de itens",
        "catalog_body": "Navegue por todos os itens por categoria.",
    },
    "ru": {
        "items_word": "предметов",
        "catalog_title": "Каталог предметов",
        "catalog_body": "Обзор всех предметов по категориям.",
    },
    "zh-CN": {
        "items_word": "个项目",
        "catalog_title": "物品目录",
        "catalog_body": "按类别浏览所有物品。",
    },
    "zh-TW": {
        "items_word": "個項目",
        "catalog_title": "物品目錄",
        "catalog_body": "按類別瀏覽所有物品。",
    },
}

# Category name translations (for page titles)
CAT_TITLES = {
    "ammo": {"en": "Ammo", "cs": "Munice", "de": "Munition", "es": "Munición", "fr": "Munitions", "it": "Munizioni", "ja": "弾薬", "ko": "탄약", "nl": "Munitie", "pl": "Amunicja", "pt": "Munição", "ru": "Боеприпасы", "zh-CN": "弹药", "zh-TW": "彈藥"},
    "artifacts": {"en": "Artifacts", "cs": "Artefakty", "de": "Artefakte", "es": "Artefactos", "fr": "Artefacts", "it": "Artefatti", "ja": "アーティファクト", "ko": "아티팩트", "nl": "Artefacten", "pl": "Artefakty", "pt": "Artefatos", "ru": "Артефакты", "zh-CN": "神器", "zh-TW": "神器"},
    "decorations": {"en": "Decorations", "cs": "Dekory", "de": "Dekorationen", "es": "Decoraciones", "fr": "Décorations", "it": "Decorazioni", "ja": "装飾", "ko": "장식", "nl": "Decoraties", "pl": "Dekoracje", "pt": "Decorações", "ru": "Декорации", "zh-CN": "装饰", "zh-TW": "裝飾"},
    "materials": {"en": "Materials", "cs": "Materiály", "de": "Materialien", "es": "Materiales", "fr": "Matériaux", "it": "Materiali", "ja": "素材", "ko": "재료", "nl": "Materialen", "pl": "Materiały", "pt": "Materiais", "ru": "Материалы", "zh-CN": "材料", "zh-TW": "材料"},
    "mission-items": {"en": "Mission items", "cs": "Misní položky", "de": "Mission-Artikel", "es": "Artículos de misión", "fr": "Articles de mission", "it": "Oggetti di missione", "ja": "ミッションアイテム", "ko": "미션 아이템", "nl": "Missie-artikelen", "pl": "Przedmioty misyjne", "pt": "Itens de missão", "ru": "Миссионные предметы", "zh-CN": "任务物品", "zh-TW": "任務物品"},
    "modules": {"en": "Modules", "cs": "Moduly", "de": "Module", "es": "Módulos", "fr": "Modules", "it": "Moduli", "ja": "モジュール", "ko": "모듈", "nl": "Modulen", "pl": "Moduły", "pt": "Módulos", "ru": "Модули", "zh-CN": "模块", "zh-TW": "模組"},
    "production": {"en": "Production items", "cs": "Výrobní položky", "de": "Produktionsartikel", "es": "Artículos de producción", "fr": "Articles de production", "it": "Oggetti di produzione", "ja": "生産アイテム", "ko": "생산 아이템", "nl": "Productie-artikelen", "pl": "Przedmioty produkcyjne", "pt": "Itens de produção", "ru": "Производственные предметы", "zh-CN": "生产物品", "zh-TW": "生產物品"},
    "robot-parts": {"en": "Robot parts", "cs": "Díly robotů", "de": "Roboter-Teile", "es": "Piezas de robot", "fr": "Pièces de robot", "it": "Parti di robot", "ja": "ロボット部品", "ko": "로봇 부품", "nl": "Robotonderdelen", "pl": "Części robotów", "pt": "Partes de robô", "ru": "Детали роботов", "zh-CN": "机器人部件", "zh-TW": "機器人部件"},
    "special-other": {"en": "Special & other", "cs": "Speciální & ostatní", "de": "Spezial & Sonstiges", "es": "Especiales y otros", "fr": "Spécial & autres", "it": "Speciali & altri", "ja": "特殊＆その他", "ko": "특수 & 기타", "nl": "Speciaal & overig", "pl": "Specjalne i inne", "pt": "Especiais e outros", "ru": "Специальные и прочие", "zh-CN": "特殊及其他", "zh-TW": "特殊及其他"},
}

# Full sentence templates for the components page intro line.
# {n} = count, {link} = [label](url)
COMP_INTRO = {
    "en": "{n} items are used as components in {link}.",
    "cs": "{n} položek se používá jako komponenty v {link}.",
    "de": "{n} Artikel werden als Komponenten in {link} verwendet.",
    "es": "{n} artículos se utilizan como componentes en {link}.",
    "fr": "{n} articles sont utilisés comme composants dans {link}.",
    "it": "{n} oggetti sono utilizzati come componenti in {link}.",
    "ja": "{link}で{n}のアイテムがコンポーネントとして使用されています。",
    "ko": "{link}에서 {n}개의 항목이 구성 요소로 사용됩니다.",
    "nl": "{n} artikelen worden gebruikt als componenten in {link}.",
    "pl": "{n} przedmiotów jest używanych jako komponenty w {link}.",
    "pt": "{n} itens são usados como componentes em {link}.",
    "ru": "{n} предметов используются как компоненты в {link}.",
    "zh-CN": "共{n}个项目在{link}中作为组件使用。",
    "zh-TW": "共{n}個項目在{link}中作為組件使用。",
}

COMP_TITLES = {
    "en": "Components", "cs": "Komponenty", "de": "Komponenten", "es": "Componentes",
    "fr": "Composants", "it": "Componenti", "ja": "コンポーネント", "ko": "구성 요소",
    "nl": "Componenten", "pl": "Komponenty", "pt": "Componentes", "ru": "Компоненты",
    "zh-CN": "组件", "zh-TW": "組件",
}

# Translated link label for "production recipes"
RECIPES_LABEL = {
    "en": "production recipes", "cs": "výrobních receptech", "de": "Produktionsrezepturen",
    "es": "recetas de producción", "fr": "recettes de production", "it": "ricette di produzione",
    "ja": "生産レシピ", "ko": "생산 레시피", "nl": "productierecepten",
    "pl": " receptach produkcyjnych", "pt": "receitas de produção", "ru": "производственных рецептах",
    "zh-CN": "生产配方", "zh-TW": "生產配方",
}


def _load_lang_pages(lang: str) -> set:
    """Load the set of pages that exist in the given language."""
    import json
    lp_file = REPO / "static" / "lang-pages.json"
    if not lp_file.exists():
        return set()
    with open(lp_file) as f:
        data = json.load(f)
    return set(data.get(lang, []))


def prefix_links(content: str, lang: str) -> str:
    """Add language prefix to internal links that have a translated page."""
    lp = f"/{lang}"
    translated = _load_lang_pages(lang)

    def _has_translation(url: str) -> bool:
        # Manifest URLs have the lang prefix and no trailing slash
        check = f"{lp}{url}"
        if check.endswith('/'):
            check = check.rstrip('/')
        return check in translated

    def _prefix_href(m):
        url = m.group(1)
        if _has_translation(url):
            return f'href="{lp}{url}"'
        return m.group(0)

    content = re.sub(r'href="(/content/[^"]+)"', _prefix_href, content)

    def _prefix_md(m):
        url = m.group(1)
        if _has_translation(url):
            return f']({lp}{url})'
        return m.group(0)

    content = re.sub(r'\]\((/content/[^)]+)\)', _prefix_md, content)
    return content


def translate_catalog_page(content: str, lang: str, cat_slug: str) -> str:
    """Translate a catalog page."""
    t = T[lang]
    
    # Replace the item count line: "N items." -> "N {items_word}."
    content = re.sub(
        r'^(\d+) items\.$',
        rf'\1 {t["items_word"]}.',
        content,
        flags=re.MULTILINE
    )
    
    # Replace the title (H1) with translated category name
    if cat_slug in CAT_TITLES:
        translated_title = CAT_TITLES[cat_slug][lang]
        content = re.sub(r'^# .+$', f'# {translated_title}', content, flags=re.MULTILINE)
    
    # Replace frontmatter title
    if cat_slug in CAT_TITLES:
        content = re.sub(
            r'^title: ".+"$',
            f'title: "{CAT_TITLES[cat_slug][lang]}"',
            content,
            flags=re.MULTILINE
        )
    
    # Prefix links
    content = prefix_links(content, lang)
    
    return content


def translate_components_page(content: str, lang: str) -> str:
    """Translate the components page."""
    title = COMP_TITLES[lang]
    
    # Replace the intro line with the full translated sentence
    m = re.search(
        r'^(\d+) items are used as components in \[([^\]]+)\]\(([^)]+)\)\.$',
        content, re.MULTILINE
    )
    if m:
        n = m.group(1)
        link_url = m.group(3)
        new_line = COMP_INTRO[lang].format(n=n, link=f"[{RECIPES_LABEL[lang]}]({link_url})")
        content = content[:m.start()] + new_line + content[m.end():]
    
    # Replace title and H1
    content = re.sub(r'^# Components$', f'# {title}', content, flags=re.MULTILINE)
    content = re.sub(r'^title: ".+"$', f'title: "{title}"', content, flags=re.MULTILINE)
    
    # Prefix links
    content = prefix_links(content, lang)
    
    return content


def translate_index_page(content: str, lang: str) -> str:
    """Translate the catalog _index page."""
    t = T[lang]
    content = re.sub(r'^# Item catalog$', f'# {t["catalog_title"]}', content, flags=re.MULTILINE)
    content = re.sub(r'^title: ".+"$', f'title: "{t["catalog_title"]}"', content, flags=re.MULTILINE)
    content = re.sub(
        r'Browse all items grouped by category\.',
        t["catalog_body"],
        content
    )
    content = prefix_links(content, lang)
    return content


def process_one(args):
    """Process a single translation task."""
    lang, cat_slug, content = args
    out_dir = REPO / "content" / lang / "content" / "catalog"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if cat_slug == "_index":
        result = translate_index_page(content, lang)
        out_file = out_dir / "_index.md"
    elif cat_slug == "components":
        result = translate_components_page(content, lang)
        out_dir2 = REPO / "content" / lang / "content"
        out_dir2.mkdir(parents=True, exist_ok=True)
        out_file = out_dir2 / "components.md"
    else:
        result = translate_catalog_page(content, lang, cat_slug)
        out_file = out_dir / f"{cat_slug}.md"
    
    out_file.write_text(result)
    return str(out_file.relative_to(REPO))


def main():
    # Collect all pages to translate
    tasks = []
    
    # Catalog _index
    index_content = (CATALOG_DIR / "_index.md").read_text()
    for lang in LANGS:
        tasks.append((lang, "_index", index_content))
    
    # Catalog category pages
    for md_file in sorted(CATALOG_DIR.glob("*.md")):
        if md_file.name == "_index.md":
            continue
        cat_slug = md_file.stem
        content = md_file.read_text()
        for lang in LANGS:
            tasks.append((lang, cat_slug, content))
    
    # Components page
    if COMPONENTS_PAGE.exists():
        comp_content = COMPONENTS_PAGE.read_text()
        for lang in LANGS:
            tasks.append((lang, "components", comp_content))
    
    print(f"gen_catalog_translations: {len(tasks)} files to generate ({len(LANGS)} languages)")
    
    with ProcessPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(process_one, tasks))
    
    print(f"Done. {len(results)} files written.")


if __name__ == "__main__":
    main()
