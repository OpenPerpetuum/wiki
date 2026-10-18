#!/usr/bin/env python3
"""Generate translated item pages for all 13 languages.

Reads the 1504 item pages from content/content/items/ that have the
`production:generated` marker, translates the fixed UI strings (section
headers, table labels, prose), and writes to content/{lang}/content/items/.

Game item names, definition IDs, stat values, and mermaid diagrams are kept
as-is (matching the pattern from ore/recipe translations).
"""
import os
import re
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

REPO = Path(__file__).resolve().parent.parent
ITEMS_DIR = REPO / "content" / "content" / "items"

LANGS = ["cs", "de", "es", "fr", "it", "ja", "ko", "nl", "pl", "pt", "ru", "zh-CN", "zh-TW"]

# ─── Translations for fixed UI strings ───────────────────────────────────────

T = {
    "cs": {
        "definition": "Definice",
        "tier": "Třída",
        "health": "Zdraví",
        "volume": "Objem",
        "mass": "Hmotnost",
        "category": "Kategorie",
        "note": "Poznámka",
        "no_stats": "_Žádné statistiky — tento předmět nenese žádné agregované hodnoty._",
        "stats": "## Statistiky",
        "field": "Pole",
        "value": "Hodnota",
        "production": "## Výroba",
        "produced_from": "**Vyráběn z {n} {comp}{rl}** — sestavte komponenty pro jeho výrobu (celkový seznam najdete v [Receptury](/cs/content/recipes/)):",
        "comp_one": "komponentě",
        "comp_many": "komponentách",
        "research_level": ", výzkumná úroveň {rl}",
        "blueprint": "**Výkres:**",
        "required": "potřebné: <b>{n}</b>",
        "used_in": "## Použito ve výrobě",
        "component_of": "**Komponentou {n} předmětů** — ukázka toho, co se s ním dá vyrobit (celkový seznam je v [Receptury](/cs/content/recipes/)).",
        "component_of_all": "**Komponentou {n} předmětů** — vše, co ho ve výrobě používá:",
        "where_to_buy": "## Kde koupit",
        "transport_capsule": "## Transportní kapsle",
        "all_recipes": "Všechny receptury",
    },
    "de": {
        "definition": "Definition",
        "tier": "Stufe",
        "health": "Häufigkeit",
        "volume": "Volumen",
        "mass": "Masse",
        "category": "Kategorie",
        "note": "Hinweis",
        "no_stats": "_Keine Statistiken — dieses Element trägt keine aggregierten Werte._",
        "stats": "## Statistiken",
        "field": "Feld",
        "value": "Wert",
        "production": "## Produktion",
        "produced_from": "**Hergestellt aus {n} {comp}{rl}** — baue die Komponenten zusammen, um es herzustellen (vollständige Liste in [Rezepte](/de/content/recipes/)):",
        "comp_one": "Komponente",
        "comp_many": "Komponenten",
        "research_level": ", Forschungsebene {rl}",
        "blueprint": "**Bauplan:**",
        "required": "benötigt: <b>{n}</b>",
        "used_in": "## Verwendet in Produktion",
        "component_of": "**Komponente von {n} Artikeln** — eine Auswahl dessen, was damit produziert werden kann (vollständige Liste in [Rezepte](/de/content/recipes/)).",
        "component_of_all": "**Komponente von {n} Artikeln** — alles, was es in der Produktion verwendet:",
        "where_to_buy": "## Wo kaufen",
        "transport_capsule": "## Transportkapsel",
        "all_recipes": "Alle Rezepte",
    },
    "es": {
        "definition": "Definición",
        "tier": "Nivel",
        "health": "Salud",
        "volume": "Volumen",
        "mass": "Masa",
        "category": "Categoría",
        "note": "Nota",
        "no_stats": "_Sin estadísticas — este elemento no porta valores agregados._",
        "stats": "## Estadísticas",
        "field": "Campo",
        "value": "Valor",
        "production": "## Producción",
        "produced_from": "**Producido desde {n} {comp}{rl}** — ensambla los componentes para construirlo (lista completa en [Recetas](/es/content/recipes/)):",
        "comp_one": "componente",
        "comp_many": "componentes",
        "research_level": ", nivel de investigación {rl}",
        "blueprint": "**Planos:**",
        "required": "requerido: <b>{n}</b>",
        "used_in": "## Usado en producción",
        "component_of": "**Componente de {n} elementos** — una muestra de lo que se puede producir con él (lista completa en [Recetas](/es/content/recipes/)).",
        "component_of_all": "**Componente de {n} elementos** — todo lo que lo usa en producción:",
        "where_to_buy": "## Dónde comprar",
        "transport_capsule": "## Cápsula de transporte",
        "all_recipes": "Todas las recetas",
    },
    "fr": {
        "definition": "Définition",
        "tier": "Niveau",
        "health": "Points de vie",
        "volume": "Volume",
        "mass": "Masse",
        "category": "Catégorie",
        "note": "Note",
        "no_stats": "_Aucune statistique — cet article ne porte aucune valeur agrégée._",
        "stats": "## Statistiques",
        "field": "Champ",
        "value": "Valeur",
        "production": "## Production",
        "produced_from": "**Produit à partir de {n} {comp}{rl}** — assemblez les composants pour le fabriquer (liste complète dans [Recettes](/fr/content/recipes/)):",
        "comp_one": "composant",
        "comp_many": "composants",
        "research_level": ", niveau de recherche {rl}",
        "blueprint": "**Plan :**",
        "required": "requis : <b>{n}</b>",
        "used_in": "## Utilisé en production",
        "component_of": "**Composant de {n} articles** — un aperçu de ce qui peut être produit avec (liste complète dans [Recettes](/fr/content/recipes/)).",
        "component_of_all": "**Composant de {n} articles** — tout ce qui l'utilise en production :",
        "where_to_buy": "## Où acheter",
        "transport_capsule": "## Capsule de transport",
        "all_recipes": "Toutes les recettes",
    },
    "it": {
        "definition": "Definizione",
        "tier": "Livello",
        "health": "Salute",
        "volume": "Volume",
        "mass": "Massa",
        "category": "Categoria",
        "note": "Nota",
        "no_stats": "_Nessuna statistica — questo oggetto non porta valori aggregati._",
        "stats": "## Statistiche",
        "field": "Campo",
        "value": "Valore",
        "production": "## Produzione",
        "produced_from": "**Prodotto da {n} {comp}{rl}** — assembra i componenti per costruirlo (lista completa in [Ricette](/it/content/recipes/)):",
        "comp_one": "componente",
        "comp_many": "componenti",
        "research_level": ", livello di ricerca {rl}",
        "blueprint": "**Piano:**",
        "required": "richiesto: <b>{n}</b>",
        "used_in": "## Usato in produzione",
        "component_of": "**Componente di {n} oggetti** — un campione di ciò che si può produrre con esso (lista completa in [Ricette](/it/content/recipes/)).",
        "component_of_all": "**Componente di {n} oggetti** — tutto ciò che lo usa in produzione:",
        "where_to_buy": "## Dove acquistare",
        "transport_capsule": "## Capsula di trasporto",
        "all_recipes": "Tutte le ricette",
    },
    "ja": {
        "definition": "定義",
        "tier": "ティア",
        "health": "耐久",
        "volume": "容量",
        "mass": "質量",
        "category": "カテゴリ",
        "note": "備考",
        "no_stats": "_統計なし — このアイテムには集約値がありません。_",
        "stats": "## 統計",
        "field": "フィールド",
        "value": "値",
        "production": "## 製造",
        "produced_from": "**{comp}{n}個から製造 {rl}** — コンポーネントを組立てて製造します（全リストは[レシピ](/ja/content/recipes/)を参照）:",
        "comp_one": "コンポーネント",
        "comp_many": "コンポーネント",
        "research_level": "、研究レベル {rl}",
        "blueprint": "**設計図:**",
        "required": "必要: <b>{n}</b>",
        "used_in": "## 製造に使用",
        "component_of": "**{n}個のアイテムのコンポーネント** — これを使って製造できるものの例（全リストは[レシピ](/ja/content/recipes/)を参照）。",
        "component_of_all": "**{n}個のアイテムのコンポーネント** — これを使用して生産するすべて:",
        "where_to_buy": "## 購入場所",
        "transport_capsule": "## 輸送カプセル",
        "all_recipes": "全レシピ",
    },
    "ko": {
        "definition": "정의",
        "tier": "티어",
        "health": "내구도",
        "volume": "용량",
        "mass": "질량",
        "category": "카테고리",
        "note": "비고",
        "no_stats": "_통계 없음 — 이 아이템에는 집계 값이 없습니다._",
        "stats": "## 통계",
        "field": "필드",
        "value": "값",
        "production": "## 생산",
        "produced_from": "**{comp} {n}개로 생산 {rl}** — 구성 요소를 조립하여 제작합니다 (전체 목록은 [레시피](/ko/content/recipes/) 참조):",
        "comp_one": "구성 요소",
        "comp_many": "구성 요소",
        "research_level": ", 연구 레벨 {rl}",
        "blueprint": "**제작도:**",
        "required": "필요: <b>{n}</b>",
        "used_in": "## 생산에 사용",
        "component_of": "**{n}개 아이템의 구성 요소** — 이를 이용해 생산할 수 있는 것의 예시 (전체 목록은 [레시피](/ko/content/recipes/) 참조).",
        "component_of_all": "**{n}개 아이템의 구성 요소** — 이를 생산에 사용하는 모든 것:",
        "where_to_buy": "## 구매 장소",
        "transport_capsule": "## 운송 캡슐",
        "all_recipes": "전체 레시피",
    },
    "nl": {
        "definition": "Definitie",
        "tier": "Tier",
        "health": "Levenspunten",
        "volume": "Volume",
        "mass": "Massa",
        "category": "Categorie",
        "note": "Opmerking",
        "no_stats": "_Geen statistieken — dit item draagt geen geaggregeerde waarden._",
        "stats": "## Statistieken",
        "field": "Veld",
        "value": "Waarde",
        "production": "## Productie",
        "produced_from": "**Geproduceerd uit {n} {comp}{rl}** — monteer de componenten om het te bouwen (volledige lijst in [Recepten](/nl/content/recipes/)):",
        "comp_one": "component",
        "comp_many": "componentën",
        "research_level": ", onderzoekslevel {rl}",
        "blueprint":"**Bouwtekening:**",
        "required": "vereist: <b>{n}</b>",
        "used_in": "## Gebruikt in productie",
        "component_of": "**Component van {n} items** — een voorbeeld van wat ermee geproduceerd kan worden (volledige lijst in [Recepten](/nl/content/recipes/)).",
        "component_of_all": "**Component van {n} items** — alles dat het in productie gebruikt:",
        "where_to_buy": "## Waar te kopen",
        "transport_capsule": "## Transporthoeft",
        "all_recipes": "Alle recepten",
    },
    "pl": {
        "definition": "Definicja",
        "tier": "Poziom",
        "health": "Zdrowie",
        "volume": "Objętość",
        "mass": "Masa",
        "category": "Kategoria",
        "note": "Uwaga",
        "no_stats": "_Brak statystyk — ten przedmiot nie niesie żadnych wartości agregowanych._",
        "stats": "## Statystyki",
        "field": "Pole",
        "value": "Wartość",
        "production": "## Produkcja",
        "produced_from": "**Produkcja z {n} {comp}{rl}** — zmontuj komponenty, aby go zbudować (pełna lista w [Przepisy](/pl/content/recipes/)):",
        "comp_one": "komponentu",
        "comp_many": "komponentów",
        "research_level": ", poziom badań {rl}",
        "blueprint":"**Nakładka:**",
        "required": "wymagane: <b>{n}</b>",
        "used_in": "## Użyte w produkcji",
        "component_of": "**Komponentem {n} przedmiotów** — przykład tego, co można z niego wyprodukować (pełna lista w [Przepisy](/pl/content/recipes/)).",
        "component_of_all": "**Komponentem {n} przedmiotów** — wszystko, co go używa w produkcji:",
        "where_to_buy": "## Gdzie kupić",
        "transport_capsule": "## Kapsuła transportowa",
        "all_recipes": "Wszystkie przepisy",
    },
    "pt": {
        "definition": "Definição",
        "tier": "Nível",
        "health": "Vida",
        "volume": "Volume",
        "mass": "Massa",
        "category": "Categoria",
        "note": "Nota",
        "no_stats": "_Sem estatísticas — este item não carrega valores agregados._",
        "stats": "## Estatísticas",
        "field": "Campo",
        "value": "Valor",
        "production": "## Produção",
        "produced_from": "**Produzido a partir de {n} {comp}{rl}** — monte os componentes para construí-lo (lista completa em [Receitas](/pt/content/recipes/)):",
        "comp_one": "componente",
        "comp_many": "componentes",
        "research_level": ", nível de pesquisa {rl}",
        "blueprint": "**Plano:**",
        "required": "necessário: <b>{n}</b>",
        "used_in": "## Usado em produção",
        "component_of": "**Componente de {n} itens** — uma amostra do que pode ser produzido com ele (lista completa em [Receitas](/pt/content/recipes/)).",
        "component_of_all": "**Componente de {n} itens** — tudo que o usa na produção:",
        "where_to_buy": "## Onde comprar",
        "transport_capsule": "## Cápsula de transporte",
        "all_recipes": "Todas as receitas",
    },
    "ru": {
        "definition": "Определение",
        "tier": "Тир",
        "health": "Прочность",
        "volume": "Объём",
        "mass": "Масса",
        "category": "Категория",
        "note": "Примечание",
        "no_stats": "_Нет статистики — этот предмет не имеет агрегированных значений._",
        "stats": "## Статистика",
        "field": "Поле",
        "value": "Значение",
        "production": "## Производство",
        "produced_from": "**Производится из {n} {comp}{rl}** — соберите компоненты для изготовления (полный список в [Рецепты](/ru/content/recipes/)):",
        "comp_one": "компоненте",
        "comp_many": "компонентах",
        "research_level": ", уровень исследований {rl}",
        "blueprint": "**Чертёж:**",
        "required": "нужно: <b>{n}</b>",
        "used_in": "## Используется в производстве",
        "component_of": "**Компонент {n} предметов** — пример того, что можно произвести с ним (полный список в [Рецепты](/ru/content/recipes/)).",
        "component_of_all": "**Компонент {n} предметов** — всё, что использует его в производстве:",
        "where_to_buy": "## Где купить",
        "transport_capsule": "## Транспортная капсула",
        "all_recipes": "Все рецепты",
    },
    "zh-CN": {
        "definition": "定义",
        "tier": "阶级",
        "health": "耐久",
        "volume": "容量",
        "mass": "质量",
        "category": "分类",
        "note": "备注",
        "no_stats": "_无统计 — 此物品没有聚合值。_",
        "stats": "## 统计",
        "field": "字段",
        "value": "值",
        "production": "## 生产",
        "produced_from": "**由{comp} {n}个生产 {rl}** — 组装组件来制造它（完整列表见[配方](/zh-CN/content/recipes/)）:",
        "comp_one": "组件",
        "comp_many": "组件",
        "research_level": "，研究等级 {rl}",
        "blueprint": "**蓝图:**",
        "required": "需要: <b>{n}</b>",
        "used_in": "## 用于生产",
        "component_of": "**{n}个物品的组件** — 使用它可以生产的内容示例（完整列表见[配方](/zh-CN/content/recipes/)）。",
        "component_of_all": "**{n}个物品的组件** — 所有在制造中使用它的物品:",
        "where_to_buy": "## 购买地点",
        "transport_capsule": "## 运输舱",
        "all_recipes": "所有配方",
    },
    "zh-TW": {
        "definition": "定義",
        "tier": "階級",
        "health": "耐久",
        "volume": "容量",
        "mass": "質量",
        "category": "分類",
        "note": "備註",
        "no_stats": "_無統計 — 此物品沒有聚合值。_",
        "stats": "## 統計",
        "field": "欄位",
        "value": "值",
        "production": "## 生產",
        "produced_from": "**由{comp} {n}個生產 {rl}** — 組裝組件來製造它（完整列表見[配方](/zh-TW/content/recipes/)）:",
        "comp_one": "組件",
        "comp_many": "組件",
        "research_level": "，研究等級 {rl}",
        "blueprint":"**藍圖:**",
        "required": "需要: <b>{n}</b>",
        "used_in": "## 用於生產",
        "component_of": "**{n}個物品的組件** — 使用它可以生產的內容示例（完整列表見[配方](/zh-TW/content/recipes/)）。",
        "component_of_all": "**{n}個物品的組件** — 所有在製造中使用它的物品:",
        "where_to_buy": "## 購買地點",
        "transport_capsule": "## 運輸艙",
        "all_recipes": "所有配方",
    },
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


def slug_from_filename(fname: str) -> str:
    """Convert filename to URL slug: ammo_cruisemissile_a.md → ammo-cruisemissile-a"""
    return fname.replace("_", "-").removesuffix(".md")


def translate_item(content: str, lang: str, slug: str) -> str:
    """Translate the fixed UI strings in an item page."""
    t = T[lang]
    lp = f"/{lang}"

    # ── Frontmatter: keep title, translate description if it's a category ──
    # (description stays as-is since categories are game terms)

    # ── Info table headers ──
    content = content.replace("| Definition |", f"| {t['definition']} |")
    content = content.replace("| Tier |", f"| {t['tier']} |")
    content = content.replace("| Health |", f"| {t['health']} |")
    content = content.replace("| Volume |", f"| {t['volume']} |")
    content = content.replace("| Mass |", f"| {t['mass']} |")
    content = content.replace("| Category |", f"| {t['category']} |")
    content = content.replace("| Note |", f"| {t['note']} |")

    # ── No stats line ──
    content = content.replace(
        "_No stats — this item carries no aggregate values._",
        t["no_stats"]
    )

    # ── Section headers ──
    content = content.replace("## Stats", t["stats"])
    content = content.replace("## Production", t["production"])
    content = content.replace("## Used in production", t["used_in"])
    content = content.replace("## Where to buy", t["where_to_buy"])
    content = content.replace("## Transport capsule", t["transport_capsule"])

    # ── Stats table: | Field | Value | ──
    content = content.replace("| Field | Value |", f"| {t['field']} | {t['value']} |")

    # ── Production section ──
    # Pattern: **Produced from N components, research level X** — assemble...
    def replace_produced(m):
        n = m.group(1)
        rl = m.group(2)  # may be None
        # Determine singular/plural
        comp = t["comp_one"] if n == "1" else t["comp_many"]
        rl_str = t["research_level"].format(rl=rl) if rl else ""
        return t["produced_from"].format(n=n, comp=comp, rl=rl_str)

    content = re.sub(
        r"\*\*Produced from (\d+(?:\.\d+)?[km]?) components?, research level (\d+)\*\* — assemble the components to build it \(see \[Recipes\]\(/content/recipes/\) for the full list\):",
        replace_produced,
        content
    )
    # Pattern without research level: **Produced from N components** — assemble...
    def replace_produced_norl(m):
        n = m.group(1)
        comp = t["comp_one"] if n == "1" else t["comp_many"]
        result = t["produced_from"].format(n=n, comp=comp, rl="")
        return result.replace(" **", "**")

    content = re.sub(
        r"\*\*Produced from (\d+(?:\.\d+)?[km]?) components?\*\* — assemble the components to build it \(see \[Recipes\]\(/content/recipes/\) for the full list\):",
        replace_produced_norl,
        content
    )

    # ── Blueprint line ──
    content = content.replace("**Blueprint:**", t["blueprint"])

    # ── "required: N" in prod-card-body ──
    def replace_required(m):
        return t["required"].format(n=m.group(1))
    content = re.sub(r"required: <b>([^<]+)</b>", replace_required, content)

    # ── "Component of N items" ──
    def replace_component_of(m):
        return t["component_of"].format(n=m.group(1))
    content = re.sub(
        r"\*\*Component of (\d+(?:\.\d+)?[km]?) items\*\* — a sample of what can be produced with it \(the full list is in \[Recipes\]\(/content/recipes/\)\).",
        replace_component_of,
        content
    )
    def replace_component_of_all(m):
        return t["component_of_all"].format(n=m.group(1))
    content = re.sub(
        r"\*\*Component of (\d+(?:\.\d+)?[km]?) items\*\* — everything that uses it in production:",
        replace_component_of_all,
        content
    )

    # ── Links: add language prefix to internal links (only if translated) ──
    translated_pages = _load_lang_pages(lang)

    def _has_trans(url):
        check = f"{lp}{url}"
        if check.endswith('/'):
            check = check.rstrip('/')
        return check in translated_pages

    def _prefix_href(m):
        url = m.group(1)
        if _has_trans(url):
            return f'href="{lp}{url}"'
        return m.group(0)

    content = re.sub(r'href="(/(?:content|zones|features|formats)/[^"]*)"', _prefix_href, content)
    content = re.sub(r'\]\((/(?:content|zones|features)/[^)]*)\)', lambda m: f']({lp}{m.group(1)})' if _has_trans(m.group(1)) else m.group(0), content)
    content = re.sub(r'"(/(?:content|zones)/[^"]*)"', lambda m: f'"{lp}{m.group(1)}"' if _has_trans(m.group(1)) else m.group(0), content)

    return content


def process_one(args):
    """Process a single (lang, slug, filepath) tuple. Returns (lang, slug, success)."""
    lang, slug, filepath = args
    try:
        content = Path(filepath).read_text(encoding="utf-8")
        translated = translate_item(content, lang, slug)
        out_dir = REPO / "content" / lang / "content" / "items"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{slug.replace('-', '_')}.md"
        out_path.write_text(translated, encoding="utf-8")
        return (lang, slug, True)
    except Exception as e:
        return (lang, slug, False)


def main():
    # Find all item pages with the production:generated marker
    item_files = []
    for f in sorted(ITEMS_DIR.glob("*.md")):
        if f.name == "_index.md":
            continue
        content = f.read_text(encoding="utf-8")
        if "production:generated" in content:
            slug = slug_from_filename(f.name)
            item_files.append((slug, str(f)))

    print(f"Found {len(item_files)} item pages with production data")

    # Build task list: (lang, slug, filepath)
    tasks = []
    for lang in LANGS:
        for slug, filepath in item_files:
            tasks.append((lang, slug, filepath))

    print(f"Total files to generate: {len(tasks)}")
    print(f"Languages: {', '.join(LANGS)}")
    print()

    # Process in parallel
    done = 0
    errors = 0
    with ProcessPoolExecutor(max_workers=32) as pool:
        futures = {pool.submit(process_one, t): t for t in tasks}
        for fut in as_completed(futures):
            lang, slug, ok = fut.result()
            done += 1
            if not ok:
                errors += 1
                print(f"  ERROR: {lang}/{slug}")
            if done % 2000 == 0:
                print(f"  Progress: {done}/{len(tasks)}")

    print(f"\nDone. {done} files written, {errors} errors.")


if __name__ == "__main__":
    main()
