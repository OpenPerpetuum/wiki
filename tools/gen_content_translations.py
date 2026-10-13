#!/usr/bin/env python3
"""Generate localized content pages in content/<lang>/content/ for all 13 supported languages.

Generates:
- content/<lang>/content/_index.md
- content/<lang>/content/ores.md + content/<lang>/content/ores/*.md (19 files)
- content/<lang>/content/plants.md
- content/<lang>/content/missions.md
- content/<lang>/content/deployables.md + content/<lang>/content/deployables/*.md (220 files)
- content/<lang>/content/robots.md + content/<lang>/content/robots/*.md (117 files)
- content/<lang>/content/recipes.md
- content/<lang>/content/techtree/_index.md + content/<lang>/content/techtree/groups/*.md (7 files)
- content/<lang>/content/extensions.md
- content/<lang>/content/stat-reference.md
- content/<lang>/content/shop.md + content/<lang>/content/shop/*.md (11 files)

All internal markdown/HTML links are rewritten to their /{lang}/ routes,
except /content/items/ and /zones/ which remain global.
"""
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from zones_i18n_data import PROTECTION_DATA, ZONES_INDEX_DATA
except ImportError:
    from tools.zones_i18n_data import PROTECTION_DATA, ZONES_INDEX_DATA

LANGUAGES = [
    "cs", "de", "es", "fr", "it", "ja", "ko",
    "nl", "pl", "pt", "ru", "zh-CN", "zh-TW"
]

I18N = {
    # Robot card stats
    "Combat": {
        "cs": "Boj", "de": "Kampf", "es": "Combate", "fr": "Combat", "it": "Combattimento",
        "ja": "戦闘", "ko": "전투", "nl": "Gevecht", "pl": "Walka", "pt": "Combate",
        "ru": "Бой", "zh-CN": "战斗", "zh-TW": "戰鬥"
    },
    "Speed": {
        "cs": "Rychlost", "de": "Geschwindigkeit", "es": "Velocidad", "fr": "Vitesse", "it": "Velocità",
        "ja": "速度", "ko": "속도", "nl": "Snelheid", "pl": "Prędkość", "pt": "Velocidade",
        "ru": "Скорость", "zh-CN": "速度", "zh-TW": "速度"
    },
    "Armor": {
        "cs": "Pancíř", "de": "Panzerung", "es": "Blindaje", "fr": "Blindage", "it": "Corazza",
        "ja": "装甲", "ko": "장갑", "nl": "Pantser", "pl": "Pancerz", "pt": "Blindagem",
        "ru": "Броня", "zh-CN": "装甲", "zh-TW": "裝甲"
    },
    "Storage": {
        "cs": "Úložiště", "de": "Frachtraum", "es": "Almacenamiento", "fr": "Stockage", "it": "Stiva",
        "ja": "積載量", "ko": "적재량", "nl": "Opslag", "pl": "Ładownia", "pt": "Armazenamento",
        "ru": "Груз", "zh-CN": "货舱", "zh-TW": "貨艙"
    },
    "Cost": {
        "cs": "Cena", "de": "Kosten", "es": "Coste", "fr": "Coût", "it": "Costo",
        "ja": "コスト", "ko": "비용", "nl": "Kosten", "pl": "Koszt", "pt": "Custo",
        "ru": "Стоимость", "zh-CN": "成本", "zh-TW": "成本"
    },
    # Common table labels
    "Class": {
        "cs": "Třída", "de": "Klasse", "es": "Clase", "fr": "Classe", "it": "Classe",
        "ja": "クラス", "ko": "클래스", "nl": "Klasse", "pl": "Klasa", "pt": "Classe",
        "ru": "Класс", "zh-CN": "级别", "zh-TW": "級別"
    },
    "Size": {
        "cs": "Velikost", "de": "Größe", "es": "Tamaño", "fr": "Taille", "it": "Dimensioni",
        "ja": "サイズ", "ko": "크기", "nl": "Grootte", "pl": "Rozmiar", "pt": "Tamanho",
        "ru": "Размер", "zh-CN": "尺寸", "zh-TW": "尺寸"
    },
    "Mass": {
        "cs": "Hmotnost", "de": "Masse", "es": "Masa", "fr": "Masse", "it": "Massa",
        "ja": "質量", "ko": "질량", "nl": "Massa", "pl": "Masa", "pt": "Massa",
        "ru": "Масса", "zh-CN": "质量", "zh-TW": "質量"
    },
    "Health": {
        "cs": "Zdraví", "de": "Struktur", "es": "Salud", "fr": "Santé", "it": "Integrità",
        "ja": "耐久値", "ko": "내구도", "nl": "Gezondheid", "pl": "Wytrzymałość", "pt": "Integridade",
        "ru": "Прочность", "zh-CN": "耐久度", "zh-TW": "耐久度"
    },
    "Purchasable": {
        "cs": "Lze koupit", "de": "Kaufbar", "es": "Comprable", "fr": "Achetable", "it": "Acquistabile",
        "ja": "購入可能", "ko": "구매 가능", "nl": "Koopbaar", "pl": "Kupny", "pt": "Comprável",
        "ru": "Доступен к покупке", "zh-CN": "可购买", "zh-TW": "可購買"
    },
    "Yes": {
        "cs": "Ano", "de": "Ja", "es": "Sí", "fr": "Oui", "it": "Sì",
        "ja": "はい", "ko": "예", "nl": "Ja", "pl": "Tak", "pt": "Sim",
        "ru": "Да", "zh-CN": "是", "zh-TW": "是"
    },
    "No": {
        "cs": "Ne", "de": "Nein", "es": "No", "fr": "Non", "it": "No",
        "ja": "いいえ", "ko": "아니오", "nl": "Nee", "pl": "Nie", "pt": "Não",
        "ru": "Нет", "zh-CN": "否", "zh-TW": "否"
    },
    "Category": {
        "cs": "Kategorie", "de": "Kategorie", "es": "Categoría", "fr": "Catégorie", "it": "Categoria",
        "ja": "カテゴリー", "ko": "카테고리", "nl": "Categorie", "pl": "Kategoria", "pt": "Categoria",
        "ru": "Категория", "zh-CN": "类别", "zh-TW": "類別"
    },
    "Tier": {
        "cs": "Úroveň", "de": "Stufe", "es": "Nivel", "fr": "Palier", "it": "Livello",
        "ja": "ティア", "ko": "티어", "nl": "Niveau", "pl": "Poziom", "pt": "Nível",
        "ru": "Тир", "zh-CN": "等级", "zh-TW": "等級"
    },
    "Volume": {
        "cs": "Objem", "de": "Volumen", "es": "Volumen", "fr": "Volume", "it": "Volume",
        "ja": "体積", "ko": "부피", "nl": "Volume", "pl": "Objętość", "pt": "Volume",
        "ru": "Объём", "zh-CN": "体积", "zh-TW": "體積"
    },
    "Definition": {
        "cs": "Definice", "de": "Definition", "es": "Definición", "fr": "Définition", "it": "Definizione",
        "ja": "定義", "ko": "정의", "nl": "Definitie", "pl": "Definicja", "pt": "Definição",
        "ru": "Определение", "zh-CN": "定义", "zh-TW": "定義"
    },
    "Field": {
        "cs": "Pole", "de": "Feld", "es": "Campo", "fr": "Champ", "it": "Campo",
        "ja": "フィールド", "ko": "필드", "nl": "Veld", "pl": "Pole", "pt": "Campo",
        "ru": "Поле", "zh-CN": "字段", "zh-TW": "欄位"
    },
    "Value": {
        "cs": "Hodnota", "de": "Wert", "es": "Valor", "fr": "Valeur", "it": "Valore",
        "ja": "値", "ko": "값", "nl": "Waarde", "pl": "Wartość", "pt": "Valor",
        "ru": "Значение", "zh-CN": "数值", "zh-TW": "數值"
    },
    "Stats": {
        "cs": "Statistiky", "de": "Werte", "es": "Estadísticas", "fr": "Statistiques", "it": "Statistiche",
        "ja": "性能パラメータ", "ko": "능력치", "nl": "Statistieken", "pl": "Statystyki", "pt": "Atributos",
        "ru": "Параметры", "zh-CN": "属性参数", "zh-TW": "屬性參數"
    },
    # Robot sections
    "Variants": {
        "cs": "Varianty", "de": "Varianten", "es": "Variantes", "fr": "Variantes", "it": "Varianti",
        "ja": "バリアント", "ko": "파생형", "nl": "Varianten", "pl": "Warianty", "pt": "Variantes",
        "ru": "Модификации", "zh-CN": "变体", "zh-TW": "變體"
    },
    "Variant": {
        "cs": "Varianta", "de": "Variante", "es": "Variante", "fr": "Variante", "it": "Variante",
        "ja": "バリアント", "ko": "파생형", "nl": "Variant", "pl": "Wariant", "pt": "Variante",
        "ru": "Модификация", "zh-CN": "变体", "zh-TW": "變體"
    },
    "Link": {
        "cs": "Odkaz", "de": "Link", "es": "Enlace", "fr": "Lien", "it": "Collegamento",
        "ja": "リンク", "ko": "링크", "nl": "Link", "pl": "Link", "pt": "Link",
        "ru": "Ссылка", "zh-CN": "链接", "zh-TW": "連結"
    },
    "Production": {
        "cs": "Výroba", "de": "Produktion", "es": "Producción", "fr": "Production", "it": "Produzione",
        "ja": "製造", "ko": "생산", "nl": "Productie", "pl": "Produkcja", "pt": "Produção",
        "ru": "Производство", "zh-CN": "制造", "zh-TW": "製造"
    },
    "Components required to build this robot:": {
        "cs": "Komponenty potřebné k sestavení tohoto robota:",
        "de": "Für den Bau dieses Roboters erforderliche Komponenten:",
        "es": "Componentes necesarios para construir este robot:",
        "fr": "Composants requis pour construire ce robot :",
        "it": "Componenti necessari per costruire questo robot:",
        "ja": "このロボットの製造に必要な部品:",
        "ko": "이 로봇을 제작하는 데 필요한 부품:",
        "nl": "Benodigde componenten om deze robot te bouwen:",
        "pl": "Komponenty wymagane do zbudowania tego robota:",
        "pt": "Componentes necessários para construir este robô:",
        "ru": "Компоненты, необходимые для сборки этого робота:",
        "zh-CN": "制造此机器人所需的组件：",
        "zh-TW": "製造此機器人所需的組件："
    },
    "Component": {
        "cs": "Komponenta", "de": "Komponente", "es": "Componente", "fr": "Composant", "it": "Componente",
        "ja": "部品", "ko": "부품", "nl": "Component", "pl": "Komponent", "pt": "Componente",
        "ru": "Компонент", "zh-CN": "组件", "zh-TW": "組件"
    },
    "Amount": {
        "cs": "Množství", "de": "Menge", "es": "Cantidad", "fr": "Quantité", "it": "Quantità",
        "ja": "数量", "ko": "수량", "nl": "Aantal", "pl": "Ilość", "pt": "Quantidade",
        "ru": "Количество", "zh-CN": "数量", "zh-TW": "數量"
    },
    "NPC Vendor": {
        "cs": "NPC Prodejce", "de": "NPC-Händler", "es": "Vendedor PNJ", "fr": "Vendeur PNJ", "it": "Venditore PNG",
        "ja": "NPCベンダー", "ko": "NPC 상인", "nl": "NPC-verkoper", "pl": "Sprzedawca NPC", "pt": "Vendedor NPC",
        "ru": "NPC-торговец", "zh-CN": "NPC 商人", "zh-TW": "NPC 商人"
    },
    "Available from the NPC vendor:": {
        "cs": "K dispozici u NPC prodejce:",
        "de": "Erhältlich beim NPC-Händler:",
        "es": "Disponible en el vendedor PNJ:",
        "fr": "Disponible auprès du vendeur PNJ :",
        "it": "Disponibile dal venditore PNG:",
        "ja": "NPCベンダーから購入可能:",
        "ko": "NPC 상인에게서 구매 가능:",
        "nl": "Verkrijgbaar bij de NPC-verkoper:",
        "pl": "Dostępne u sprzedawcy NPC:",
        "pt": "Disponível no vendedor NPC:",
        "ru": "Доступно у NPC-торговца:",
        "zh-CN": "可从 NPC 商人处购买：",
        "zh-TW": "可從 NPC 商人處購買："
    },
    "Price:": {
        "cs": "Cena:", "de": "Preis:", "es": "Precio:", "fr": "Prix :", "it": "Prezzo:",
        "ja": "価格:", "ko": "가격:", "nl": "Prijs:", "pl": "Cena:", "pt": "Preço:",
        "ru": "Цена:", "zh-CN": "售价：", "zh-TW": "售價："
    },
    # Recipe & Mission card strings
    "Research level": {
        "cs": "Úroveň výzkumu", "de": "Forschungsstufe", "es": "Nivel de investigación",
        "fr": "Niveau de recherche", "it": "Livello di ricerca", "ja": "研究レベル",
        "ko": "연구 레벨", "nl": "Onderzoeksniveau", "pl": "Poziom badań",
        "pt": "Nível de pesquisa", "ru": "Уровень исследования", "zh-CN": "研发等级", "zh-TW": "研發等級"
    },
    "Level": {
        "cs": "Úroveň", "de": "Stufe", "es": "Nivel", "fr": "Niveau", "it": "Livello",
        "ja": "レベル", "ko": "레벨", "nl": "Niveau", "pl": "Poziom", "pt": "Nível",
        "ru": "Уровень", "zh-CN": "等级", "zh-TW": "等級"
    },
    "Reward fee": {
        "cs": "Odměna", "de": "Belohnung", "es": "Recompensa", "fr": "Récompense", "it": "Ricompensa",
        "ja": "報酬", "ko": "보상금", "nl": "Beloning", "pl": "Nagroda", "pt": "Recompensa",
        "ru": "Вознаграждение", "zh-CN": "报酬", "zh-TW": "報酬"
    },
    "Duration": {
        "cs": "Doba trvání", "de": "Dauer", "es": "Duración", "fr": "Durée", "it": "Durata",
        "ja": "制限時間", "ko": "소요 시간", "nl": "Duur", "pl": "Czas trwania", "pt": "Duração",
        "ru": "Время выполнения", "zh-CN": "持续时间", "zh-TW": "持續時間"
    },
    "min": {
        "cs": "min", "de": "Min.", "es": "min", "fr": "min", "it": "min",
        "ja": "分", "ko": "분", "nl": "min", "pl": "min", "pt": "min",
        "ru": "мин", "zh-CN": "分钟", "zh-TW": "分鐘"
    },
    "chance": {
        "cs": "šance", "de": "Chance", "es": "probabilidad", "fr": "chance", "it": "probabilità",
        "ja": "確率", "ko": "확률", "nl": "kans", "pl": "szansa", "pt": "chance",
        "ru": "шанс", "zh-CN": "概率", "zh-TW": "機率"
    },
    # Deployable badges
    "no tier": {
        "cs": "bez úrovně", "de": "keine Stufe", "es": "sin nivel", "fr": "sans palier", "it": "senza livello",
        "ja": "ティアなし", "ko": "티어 없음", "nl": "geen niveau", "pl": "brak poziomu", "pt": "sem nível",
        "ru": "без тира", "zh-CN": "无等级", "zh-TW": "無等級"
    },
    # Extensions card labels
    "rank": {
        "cs": "úroveň", "de": "Rang", "es": "rango", "fr": "rang", "it": "rango",
        "ja": "ランク", "ko": "랭크", "nl": "rang", "pl": "ranga", "pt": "posto",
        "ru": "ранг", "zh-CN": "等级", "zh-TW": "等級"
    },
    "bonus": {
        "cs": "bonus", "de": "Bonus", "es": "bonificación", "fr": "bonus", "it": "bonus",
        "ja": "ボーナス", "ko": "보너스", "nl": "bonus", "pl": "bonus", "pt": "bônus",
        "ru": "бонус", "zh-CN": "加成", "zh-TW": "加成"
    },
    "inactive": {
        "cs": "neaktivní", "de": "inaktiv", "es": "inactivo", "fr": "inactif", "it": "inattivo",
        "ja": "非アクティブ", "ko": "비활성", "nl": "inactief", "pl": "nieaktywny", "pt": "inativo",
        "ru": "неактивно", "zh-CN": "未启用", "zh-TW": "未啟用"
    },
    "no prerequisites": {
        "cs": "bez prerekvizit", "de": "keine Voraussetzungen", "es": "sin requisitos previos",
        "fr": "sans prérequis", "it": "nessun prerequisito", "ja": "前提条件なし", "ko": "선행 조건 없음",
        "nl": "geen vereisten", "pl": "brak wymagań wstępnych", "pt": "sem pré-requisitos",
        "ru": "без предварительных требований", "zh-CN": "无前置要求", "zh-TW": "無前置要求"
    },
    # Shop table headers
    "Item": {
        "cs": "Předmět", "de": "Gegenstand", "es": "Objeto", "fr": "Objet", "it": "Oggetto",
        "ja": "アイテム", "ko": "아이템", "nl": "Item", "pl": "Przedmiot", "pt": "Item",
        "ru": "Предмет", "zh-CN": "物品", "zh-TW": "物品"
    },
    "Qty": {
        "cs": "Množství", "de": "Menge", "es": "Cant.", "fr": "Qté", "it": "Q.tà",
        "ja": "数量", "ko": "수량", "nl": "Aantal", "pl": "Ilość", "pt": "Qtd",
        "ru": "Кол-во", "zh-CN": "数量", "zh-TW": "數量"
    },
    "Vendors": {
        "cs": "Prodejci", "de": "Händler", "es": "Vendedores", "fr": "Vendeurs", "it": "Venditori",
        "ja": "ベンダー", "ko": "판매처", "nl": "Verkopers", "pl": "Sprzedawcy", "pt": "Vendedores",
        "ru": "Продавцы", "zh-CN": "商人", "zh-TW": "商人"
    },
    # Ore extraction table
    "Amount / extraction": {
        "cs": "Množství na těžbu", "de": "Menge / Förderung", "es": "Cantidad / extracción",
        "fr": "Quantité / extraction", "it": "Quantità / estrazione", "ja": "1回あたりの採掘量",
        "ko": "채굴당 획득량", "nl": "Aantal / extractie", "pl": "Ilość / wydobycie",
        "pt": "Quantidade / extração", "ru": "Количество за цикл", "zh-CN": "单次开采量", "zh-TW": "單次開採量"
    },
    "Extraction type": {
        "cs": "Typ těžby", "de": "Förderungsart", "es": "Tipo de extracción", "fr": "Type d'extraction",
        "it": "Tipo di estrazione", "ja": "採掘タイプ", "ko": "채굴 유형", "nl": "Extractietype",
        "pl": "Typ wydobycia", "pt": "Tipo de extração", "ru": "Тип добычи", "zh-CN": "开采方式", "zh-TW": "開採方式"
    },
    "Enabler effect": {
        "cs": "Aktivační efekt", "de": "Aktivierungseffekt", "es": "Efecto activador",
        "fr": "Effet d'activation", "it": "Effetto attivatore", "ja": "必須エフェクト",
        "ko": "필요 효과", "nl": "Inschakeleffect", "pl": "Efekt aktywujący",
        "pt": "Efeito habilitador", "ru": "Требуемый эффект", "zh-CN": "触发效果", "zh-TW": "觸發效果"
    },
    "Geo-scan doc": {
        "cs": "Geologický skenovací dokument", "de": "Geo-Scan-Dokument", "es": "Doc. geo-escaneo",
        "fr": "Doc géo-scan", "it": "Doc. geo-scansione", "ja": "地質スキャン文書",
        "ko": "지질 탐사 문서", "nl": "Geoscan-document", "pl": "Dokument geoskanowania",
        "pt": "Doc. geo-varredura", "ru": "Документ геосканирования", "zh-CN": "地质扫描文档", "zh-TW": "地質掃描文檔"
    },
    "Geo-scan document": {
        "cs": "Geologický skenovací dokument", "de": "Geo-Scan-Dokument", "es": "Documento de geo-escaneo",
        "fr": "Document de géo-scan", "it": "Documento di geo-scansione", "ja": "地質スキャン文書",
        "ko": "지질 탐사 문서", "nl": "Geoscan-document", "pl": "Dokument geoskanowania",
        "pt": "Documento de geo-varredura", "ru": "Документ геосканирования", "zh-CN": "地质扫描文档", "zh-TW": "地質掃描文檔"
    },
    "Extraction": {
        "cs": "Těžba", "de": "Förderung", "es": "Extracción", "fr": "Extraction", "it": "Estrazione",
        "ja": "採掘", "ko": "채굴", "nl": "Extractie", "pl": "Wydobycie", "pt": "Extração",
        "ru": "Добыча", "zh-CN": "开采", "zh-TW": "開採"
    },
    "Where it spawns": {
        "cs": "Kde se vyskytuje", "de": "Fundorte", "es": "Dónde aparece", "fr": "Où le trouver",
        "it": "Dove compare", "ja": "出現場所", "ko": "출현 지역", "nl": "Waar het verschijnt",
        "pl": "Występowanie", "pt": "Onde surge", "ru": "Месторождения", "zh-CN": "生成区域", "zh-TW": "生成區域"
    },
    "Made from it": {
        "cs": "Vyrábí se z něj", "de": "Daraus hergestellt", "es": "Fabricado con esto",
        "fr": "Fabriqué à partir de", "it": "Fabbricato da questo", "ja": "加工物・製品",
        "ko": "가공품", "nl": "Gemaakt hiervan", "pl": "Wytwarzane z tego",
        "pt": "Fabricado a partir disso", "ru": "Производится из этого", "zh-CN": "制造产物", "zh-TW": "製造產物"
    },
    "not required": {
        "cs": "není vyžadován", "de": "nicht erforderlich", "es": "no requerido", "fr": "non requis",
        "it": "non richiesto", "ja": "不要", "ko": "불필요", "nl": "niet vereist",
        "pl": "niewymagany", "pt": "não necessário", "ru": "не требуется", "zh-CN": "不需要", "zh-TW": "不需要"
    },
    "required": {
        "cs": "vyžadován", "de": "erforderlich", "es": "requerido", "fr": "requis",
        "it": "richiesto", "ja": "必須", "ko": "필요", "nl": "vereist",
        "pl": "wymagany", "pt": "necessário", "ru": "требуется", "zh-CN": "需要", "zh-TW": "需要"
    },
    "liquid (pumped continuously)": {
        "cs": "kapalná (kontinuální čerpání)", "de": "flüssig (kontinuierlich gepumpt)",
        "es": "líquido (bombeo continuo)", "fr": "liquide (pompage continu)",
        "it": "liquido (pompaggio continuo)", "ja": "液体 (ポンプによる継続吸引)",
        "ko": "액체 (펌프로 연속 추출)", "nl": "vloeibaar (continu gepompt)",
        "pl": "płynny (ciągłe pompowanie)", "pt": "líquido (bombeamento contínuo)",
        "ru": "жидкая (непрерывная откачка)", "zh-CN": "液态 (连续泵取)", "zh-TW": "液態 (連續泵取)"
    },
    "solid (tile-by-tile drill)": {
        "cs": "pevná (vrtání po polích)", "de": "fest (Feld für Feld mit Bohrer)",
        "es": "sólido (taladro casilla por casilla)", "fr": "solide (forage case par case)",
        "it": "solido (trivella casella per casella)", "ja": "固体 (ドリルによるタイル採掘)",
        "ko": "고체 (드릴로 타일별 채굴)", "nl": "vast (tegel voor tegel met boor)",
        "pl": "stały (wiercenie pole po polu)", "pt": "sólido (perfuração casa a casa)",
        "ru": "твёрдая (бурение по клеткам)", "zh-CN": "固态 (单格钻探开采)", "zh-TW": "固態 (單格鑽探開採)"
    },
    # Tech tree nodes labels
    "Parent node": {
        "cs": "Rodičovský uzel", "de": "Übergeordneter Knoten", "es": "Nodo padre",
        "fr": "Nœud parent", "it": "Nodo genitore", "ja": "親ノード", "ko": "상위 노드",
        "nl": "Bovenliggend knooppunt", "pl": "Węzeł nadrzędny", "pt": "Nó pai",
        "ru": "Родительский узел", "zh-CN": "父节点", "zh-TW": "父節點"
    },
    "Unlocks": {
        "cs": "Odemkne", "de": "Schaltet frei", "es": "Desbloquea", "fr": "Déverrouille",
        "it": "Sblocca", "ja": "解放項目", "ko": "잠금 해제", "nl": "Ontgrendelt",
        "pl": "Odblokowuje", "pt": "Desbloqueia", "ru": "Открывает", "zh-CN": "解锁", "zh-TW": "解鎖"
    },
    "Unlocks next": {
        "cs": "Odemkne dále", "de": "Schaltet als Nächstes frei", "es": "Desbloquea a continuación",
        "fr": "Déverrouille ensuite", "it": "Sblocca successivamente", "ja": "次期解放項目",
        "ko": "다음 잠금 해제", "nl": "Ontgrendelt vervolgens", "pl": "Odblokowuje dalej",
        "pt": "Desbloqueia a seguir", "ru": "Следующие открытия", "zh-CN": "后续解锁", "zh-TW": "後續解鎖"
    },
    "Enabler extension": {
        "cs": "Aktivační rozšíření", "de": "Freischalter-Erweiterung", "es": "Extensión habilitadora",
        "fr": "Extension requise", "it": "Estensione abilitante", "ja": "必須拡張機能",
        "ko": "필요 익스텐션", "nl": "Inschakelende extensie", "pl": "Rozszerzenie aktywujące",
        "pt": "Extensão habilitadora", "ru": "Требуемое расширение", "zh-CN": "前置技能", "zh-TW": "前置技能"
    },
    "Point prices": {
        "cs": "Bodové ceny", "de": "Punktkosten", "es": "Precios en puntos", "fr": "Coûts en points",
        "it": "Costo in punti", "ja": "必要ポイント", "ko": "포인트 가격", "nl": "Puntkosten",
        "pl": "Koszt w punktach", "pt": "Preço em pontos", "ru": "Стоимость в очках",
        "zh-CN": "点数消耗", "zh-TW": "點數消耗"
    },
    "All tech tree nodes": {
        "cs": "Všechny uzly technologického stromu", "de": "Alle Technologiebaum-Knoten",
        "es": "Todos los nodos del árbol tecnológico", "fr": "Tous les nœuds de l'arborescence tech",
        "it": "Tutti i nodi dell'albero tecnologico", "ja": "すべての技術ツリーノード",
        "ko": "모든 기술 트리 노드", "nl": "Alle technologieboom-knooppunten",
        "pl": "Wszystkie węzły drzewa technologii", "pt": "Todos os nós da árvore tecnológica",
        "ru": "Все узлы дерева технологий", "zh-CN": "所有科技树节点", "zh-TW": "所有科技樹節點"
    },
    "Ore": {
        "cs": "Ruda", "de": "Erz", "es": "Mineral", "fr": "Minerai", "it": "Minerale",
        "ja": "鉱石", "ko": "광석", "nl": "Erts", "pl": "Ruda", "pt": "Minério",
        "ru": "Руда", "zh-CN": "矿石", "zh-TW": "礦石"
    },
    "Ore types": {
        "cs": "Typy rud", "de": "Erzarten", "es": "Tipos de mineral", "fr": "Types de minerai",
        "it": "Tipi di minerale", "ja": "鉱石の種類", "ko": "광석 종류", "nl": "Soorten erts",
        "pl": "Typy rud", "pt": "Tipos de minério", "ru": "Типы руд", "zh-CN": "矿石种类", "zh-TW": "礦石種類"
    },
    "Categories": {
        "cs": "Kategorie", "de": "Kategorien", "es": "Categorías", "fr": "Catégories",
        "it": "Categorie", "ja": "カテゴリー", "ko": "카테고리", "nl": "Categorieën",
        "pl": "Kategorie", "pt": "Categorias", "ru": "Категории", "zh-CN": "分类", "zh-TW": "分類"
    },
    "Catalog": {
        "cs": "Katalog", "de": "Katalog", "es": "Catálogo", "fr": "Catalogue",
        "it": "Catalogo", "ja": "カタログ", "ko": "카탈로그", "nl": "Catalogus",
        "pl": "Katalog", "pt": "Catálogo", "ru": "Каталог", "zh-CN": "目录", "zh-TW": "目錄"
    },
    "Robot classes": {
        "cs": "Třídy robotů", "de": "Roboterklassen", "es": "Clases de robots", "fr": "Classes de robots",
        "it": "Classi di robot", "ja": "ロボットクラス", "ko": "로봇 클래스", "nl": "Robotklassen",
        "pl": "Klasy robotów", "pt": "Classes de robôs", "ru": "Классы роботов", "zh-CN": "机器人级别", "zh-TW": "機器人級別"
    },
    "Player robots": {
        "cs": "Roboti hráčů", "de": "Spieler-Roboter", "es": "Robots de jugador", "fr": "Robots de joueur",
        "it": "Robot del giocatore", "ja": "プレイヤーロボット", "ko": "플레이어 로봇", "nl": "Spelerrobots",
        "pl": "Roboty graczy", "pt": "Robôs de jogador", "ru": "Роботы игроков", "zh-CN": "玩家机器人", "zh-TW": "玩家機器人"
    },
    "Hybrid robots": {
        "cs": "Hybridní roboti", "de": "Hybrid-Roboter", "es": "Robots híbridos", "fr": "Robots hybrides",
        "it": "Robot ibridi", "ja": "ハイブリッドロボット", "ko": "하이브리드 로봇", "nl": "Hybride robots",
        "pl": "Roboty hybrydowe", "pt": "Robôs híbridos", "ru": "Гибридные роботы", "zh-CN": "混合型机器人", "zh-TW": "混合型機器人"
    },
    "NPC robots": {
        "cs": "NPC roboti", "de": "NPC-Roboter", "es": "Robots PNJ", "fr": "Robots PNJ",
        "it": "Robot PNG", "ja": "NPCロボット", "ko": "NPC 로봇", "nl": "NPC-robots",
        "pl": "Roboty NPC", "pt": "Robôs NPC", "ru": "NPC-роботы", "zh-CN": "NPC 机器人", "zh-TW": "NPC 機器人"
    },
    "{Robot} — robot stats, production and availability.": {
        "cs": "{Robot} — statistiky robota, výroba a dostupnost.",
        "de": "{Robot} – Roboterwerte, Produktion und Verfügbarkeit.",
        "es": "{Robot}: estadísticas del robot, producción y disponibilidad.",
        "fr": "{Robot} — statistiques du robot, production et disponibilité.",
        "it": "{Robot}: statistiche del robot, produzione e disponibilità.",
        "ja": "{Robot} — ロボットの性能、製造および入手方法。",
        "ko": "{Robot} — 로봇 능력치, 생산 및 획득 방법.",
        "nl": "{Robot} — robotstatistieken, productie en beschikbaarheid.",
        "pl": "{Robot} — statystyki robota, produkcja i dostępność.",
        "pt": "{Robot} — atributos do robô, produção e disponibilidade.",
        "ru": "{Robot} — параметры робота, производство и доступность.",
        "zh-CN": "{Robot} — 机器人属性、制造与获取途径。",
        "zh-TW": "{Robot} — 機器人屬性、製造與獲取途徑。"
    },
    "How a robot is built, the robot classes, and every robot: player, hybrid and NPC.": {
        "cs": "Jak se robot staví, třídy robotů a všichni roboti: hráčští, hybridní a NPC.",
        "de": "Wie ein Roboter aufgebaut ist, die Roboterklassen und alle Roboter: Spieler-, Hybrid- und NPC-Einheiten.",
        "es": "Cómo se construye un robot, las clases de robots y todos los robots: de jugador, híbridos y PNJ.",
        "fr": "Comment un robot est construit, les classes de robots et tous les robots : joueur, hybride et PNJ.",
        "it": "Come è costruito un robot, le classi di robot e tutti i robot: giocatore, ibridi e PNG.",
        "ja": "ロボットの構造、ロボットクラス、そして全ロボット一覧：プレイヤー、ハイブリッド、NPC。",
        "ko": "로봇 구성 방식, 로봇 클래스 및 모든 로봇 목록: 플레이어, 하이브리드, NPC.",
        "nl": "Hoe een robot is gebouwd, de robotklassen en alle robots: speler, hybride en NPC.",
        "pl": "Budowa robotów, klasy robotów i wszystkie roboty: gracza, hybrydowe oraz NPC.",
        "pt": "Como um robô é construído, as classes de robôs e todos os robôs: jogador, híbrido e NPC.",
        "ru": "Конструкция роботов, классы роботов и все роботы: игрока, гибридные и NPC.",
        "zh-CN": "机器人的构造、机器人级别以及所有机器人：玩家、混合型和NPC。",
        "zh-TW": "機器人的構造、機器人級別以及所有機器人：玩家、混合型和NPC。"
    },
    "Fitting, slots and in-game play are covered in the [Robot](/features/robots/) feature page; this page is the data reference.": {
        "cs": "Vybavení, sloty a hraní ve hře jsou popsány na stránce funkce [Robot](/{lang}/features/robots/); tato stránka slouží jako datový přehled.",
        "de": "Fitting, Slots und Gameplay werden auf der Feature-Seite [Roboter](/{lang}/features/robots/) behandelt; diese Seite dient als Datenreferenz.",
        "es": "El ensamblaje, las ranuras y la mecánica del juego se describen en la página de características de [Robot](/{lang}/features/robots/); esta página es la referencia de datos.",
        "fr": "L'équipement, les emplacements et le jeu en jeu sont traités sur la page de fonctionnalité [Robot](/{lang}/features/robots/) ; cette page est la référence de données.",
        "it": "Equipaggiamento, slot e meccaniche di gioco sono trattati nella pagina della funzionalità [Robot](/{lang}/features/robots/); questa pagina è il riferimento dei dati.",
        "ja": "艤装、スロット、ゲーム内での操作については機能ページ[ロボット](/{lang}/features/robots/)で解説しています。このページはデータ一覧です。",
        "ko": "피팅, 슬롯 및 게임 내 플레이는 [로봇](/{lang}/features/robots/) 기능 페이지에서 다루며, 이 페이지는 데이터 참조용입니다。",
        "nl": "Fitting, slots en gameplay worden behandeld op de featurepagina [Robot](/{lang}/features/robots/); deze pagina is de gegevensreferentie.",
        "pl": "Dopasowanie, sloty i rozgrywka są opisane na stronie funkcji [Robot](/{lang}/features/robots/); ta strona stanowi zestawienie danych.",
        "pt": "Ajuste, slots e jogabilidade são abordados na página de recursos [Robô](/{lang}/features/robots/); esta página é a referência de dados.",
        "ru": "Оснащение, слоты и игровой процесс описаны на странице механики [Робот](/{lang}/features/robots/); эта страница представляет собой справочник данных.",
        "zh-CN": "装配、槽位与游戏内玩法已在 [机器人](/{lang}/features/robots/) 功能页面中介绍；本页面为数据参考。",
        "zh-TW": "裝配、槽位與遊戲內玩法已在 [機器人](/{lang}/features/robots/) 功能頁面中介紹；本頁面為數據參考。"
    },
    "A robot's class comes from its parts. Ratings are 1–5 (more icons = higher).": {
        "cs": "Třída robota vychází z jeho částí. Hodnocení je 1–5 (více ikon = vyšší).",
        "de": "Die Klasse eines Roboters ergibt sich aus seinen Teilen. Bewertungen reichen von 1 bis 5 (mehr Symbole = höher).",
        "es": "La clase de un robot proviene de sus piezas. Las calificaciones son de 1 a 5 (más iconos = mayor).",
        "fr": "La classe d'un robot provient de ses pièces. Les évaluations vont de 1 à 5 (plus d'icônes = plus élevé).",
        "it": "La classe di un robot deriva dai suoi componenti. Le valutazioni vanno da 1 a 5 (più icone = più alto).",
        "ja": "ロボットのクラスはパーツ構成によって決まります。評価は1〜5（アイコンが多いほど高評価）です。",
        "ko": "로봇의 클래스는 부품에 의해 결정됩니다. 등급은 1~5점입니다(아이콘이 많을수록 높음).",
        "nl": "De klasse van een robot komt voort uit zijn onderdelen. Beoordelingen zijn 1–5 (meer pictogrammen = hoger).",
        "pl": "Klasa robota wynika z jego części. Oceny wynoszą 1–5 (więcej ikon = wyższa wartość).",
        "pt": "A classe de um robô vem de suas peças. As classificações vão de 1 a 5 (mais ícones = maior).",
        "ru": "Класс робота определяется его деталями. Рейтинг от 1 до 5 (больше значков = выше показатель).",
        "zh-CN": "机器人的级别由其部件决定。评级为 1–5（图标越多表示数值越高）。",
        "zh-TW": "機器人的級別由其部件決定。評級為 1–5（圖標越多表示數值越高）。"
    },
    "Robots you can acquire and control yourself (80 models), grouped by class.": {
        "cs": "Roboti, které můžete získat a sami ovládat (80 modelů), seskupení podle třídy.",
        "de": "Roboter, die Sie selbst erwerben und steuern können (80 Modelle), gruppiert nach Klasse.",
        "es": "Robots que puedes adquirir y controlar tú mismo (80 modelos), agrupados por clase.",
        "fr": "Robots que vous pouvez acquérir et piloter vous-même (80 modèles), regroupés par classe.",
        "it": "Robot che puoi acquisire e controllare personalmente (80 modelli), raggruppati per classe.",
        "ja": "プレイヤー自身が入手・操縦できるロボット（80モデル）、クラス別に分類。",
        "ko": "직접 획득하고 조종할 수 있는 로봇(80종 모델), 클래스별 분류.",
        "nl": "Robots die je zelf kunt verwerven en besturen (80 modellen), gegroepeerd per klasse.",
        "pl": "Roboty, które możesz zdobyć i kontrolować osobiście (80 modeli), pogrupowane według klas.",
        "pt": "Robôs que você pode adquirir e controlar pessoalmente (80 modelos), agrupados por classe.",
        "ru": "Роботы, которых вы можете приобрести и пилотировать самостоятельно (80 моделей), сгруппированные по классам.",
        "zh-CN": "您可以自行获取并控制的机器人（80 种型号），按级别分组。",
        "zh-TW": "您可以自行獲取並控制的機器人（80 種型號），按級別分組。"
    },
    "Runners": {
        "cs": "Běžci", "de": "Läufer", "es": "Corredores", "fr": "Coureurs", "it": "Corridori",
        "ja": "ランナー", "ko": "러너", "nl": "Runners", "pl": "Biegacze", "pt": "Corredores",
        "ru": "Бегуны", "zh-CN": "跑者", "zh-TW": "跑者"
    },
    "Crawlers": {
        "cs": "Lezci", "de": "Kriecher", "es": "Rastreros", "fr": "Rampants", "it": "Striscianti",
        "ja": "クローラー", "ko": "크롤러", "nl": "Crawlers", "pl": "Pełzacze", "pt": "Rastejadores",
        "ru": "Ползуны", "zh-CN": "爬行者", "zh-TW": "爬行者"
    },
    "Mechs": {
        "cs": "Mechové", "de": "Mechs", "es": "Mechs", "fr": "Mechs", "it": "Mech",
        "ja": "メック", "ko": "메카", "nl": "Mechs", "pl": "Mechy", "pt": "Mechs",
        "ru": "Мехи", "zh-CN": "机甲", "zh-TW": "機甲"
    },
    "Heavy mechs": {
        "cs": "Těžcí mechové", "de": "Schwere Mechs", "es": "Mechs pesados", "fr": "Mechs lourds", "it": "Mech pesanti",
        "ja": "ヘビーメック", "ko": "헤비 메카", "nl": "Zware mechs", "pl": "Ciężkie mechy", "pt": "Mechs pesados",
        "ru": "Тяжёлые мехи", "zh-CN": "重型机甲", "zh-TW": "重型機甲"
    },
    "Walkers": {
        "cs": "Kráčející", "de": "Walker", "es": "Caminantes", "fr": "Marcheurs", "it": "Camminatori",
        "ja": "ウォーカー", "ko": "워커", "nl": "Walkers", "pl": "Kroczące", "pt": "Andadores",
        "ru": "Шагоходы", "zh-CN": "步行机", "zh-TW": "步行機"
    },
    "Starter & special": {
        "cs": "Startovní a speciální", "de": "Starter & Spezial", "es": "Iniciales y especiales", "fr": "Initiaux et spéciaux", "it": "Iniziali e speciali",
        "ja": "スターター＆特殊", "ko": "스타터 및 특수", "nl": "Starter & speciaal", "pl": "Początkowe i specjalne", "pt": "Iniciais e especiais",
        "ru": "Стартовые и специальные", "zh-CN": "初始与特殊", "zh-TW": "初始與特殊"
    },
    "Named fits": {
        "cs": "Pojmenované konfigurace", "de": "Benannte Fits", "es": "Equipamientos específicos", "fr": "Configurations nommées", "it": "Configurazioni nominate",
        "ja": "特製フィット", "ko": "네임드 핏", "nl": "Benoemde fits", "pl": "Dedykowane konfiguracje", "pt": "Ajustes nomeados",
        "ru": "Именные сборки", "zh-CN": "特定配置", "zh-TW": "特定配置"
    },
    "Hybrid builds": {
        "cs": "Hybridní stavby", "de": "Hybrid-Builds", "es": "Construcciones híbridas", "fr": "Châssis hybrides", "it": "Configurazioni ibride",
        "ja": "ハイブリッド機体", "ko": "하이브리드 빌드", "nl": "Hybride builds", "pl": "Zestawy hybrydowe", "pt": "Montagens híbridas",
        "ru": "Гибридные сборки", "zh-CN": "混合型配装", "zh-TW": "混合型配裝"
    },
    "NPC units": {
        "cs": "Jednotky NPC", "de": "NPC-Einheiten", "es": "Unidades PNJ", "fr": "Unités PNJ", "it": "Unità PNG",
        "ja": "NPCユニット", "ko": "NPC 유닛", "nl": "NPC-eenheden", "pl": "Jednostki NPC", "pt": "Unidades NPC",
        "ru": "Боевые единицы NPC", "zh-CN": "NPC 单位", "zh-TW": "NPC 單位"
    },
    "The fast, light class — the cheapest robots to build and pilot.": {
        "cs": "Rychlá, lehká třída — nejlevnější roboti na výrobu a pilotáž.",
        "de": "Die schnelle, leichte Klasse – die am günstigsten zu bauenden und zu fliegenden Roboter.",
        "es": "La clase rápida y ligera: los robots más baratos de construir y pilotar.",
        "fr": "La classe rapide et légère — les robots les moins chers à construire et à piloter.",
        "it": "La classe rapida e leggera: i robot più economici da costruire e pilotare.",
        "ja": "高速かつ軽量なクラス。最も安価に製造・操縦できます。",
        "ko": "빠르고 가벼운 클래스 — 제작과 조종 비용이 가장 저렴합니다.",
        "nl": "De snelle, lichte klasse — de goedkoopste robots om te bouwen en te besturen.",
        "pl": "Szybka, lekka klasa — najtańsze roboty w budowie i pilotowaniu.",
        "pt": "A classe rápida e leve — os robôs mais baratos de construir e pilotar.",
        "ru": "Быстрый и лёгкий класс — самые дешёвые в постройке и пилотировании роботы.",
        "zh-CN": "轻快型级别 — 制造和驾驶成本最低的机器人。",
        "zh-TW": "輕快型級別 — 製造和駕駛成本最低的機器人。"
    },
    "The mid-size workhorse class.": {
        "cs": "Středně velká pracovní třída.", "de": "Die mittelgroße Arbeitstier-Klasse.",
        "es": "La clase de trabajo de tamaño mediano.", "fr": "La classe polyvalente de taille moyenne.",
        "it": "La classe instancabile di taglia media.", "ja": "中型の主力実用クラス。",
        "ko": "중형 실용 중심 클래스.", "nl": "De middelgrote werkpaardklasse.",
        "pl": "Średniej wielkości klasa robocza.", "pt": "A classe trabalhadora de tamanho médio.",
        "ru": "Средний класс рабочих лошадок.", "zh-CN": "中型主力多用途级别。", "zh-TW": "中型主力多用途級別。"
    },
    "The main combat class.": {
        "cs": "Hlavní bojová třída.", "de": "Die Hauptkampfklasse.",
        "es": "La clase de combate principal.", "fr": "La classe de combat principale.",
        "it": "La classe principale da combattimento.", "ja": "主力戦闘クラス。",
        "ko": "주력 전투 클래스.", "nl": "De belangrijkste gevechtsklasse.",
        "pl": "Główna klasa bojowa.", "pt": "A principal classe de combate.",
        "ru": "Основной боевой класс.", "zh-CN": "主要战斗级别。", "zh-TW": "主要戰鬥級別。"
    },
    "The top-tier combat class.": {
        "cs": "Špičková bojová třída.", "de": "Die Spitzen-Kampfklasse.",
        "es": "La clase de combate de primer nivel.", "fr": "La classe de combat de premier ordre.",
        "it": "La classe da combattimento di alto级别.", "ja": "最高峰の戦闘クラス。",
        "ko": "최고 등급 전투 클래스.", "nl": "De topklasse gevechtsklasse.",
        "pl": "Najwyższa klasa bojowa.", "pt": "A classe de combate de alto nível.",
        "ru": "Боевой класс высшего уровня.", "zh-CN": "顶级战斗级别。", "zh-TW": "頂級戰鬥級別。"
    },
    "A rare heavy platform class.": {
        "cs": "Vzácná těžká platformová třída.", "de": "Eine seltene schwere Plattformklasse.",
        "es": "Una rara clase de plataforma pesada.", "fr": "Une rare classe de plateforme lourde.",
        "it": "Una rara classe di piattaforma pesante.", "ja": "希少な重装プラットフォームクラス。",
        "ko": "희귀한 중형 플랫폼 클래스.", "nl": "Een zeldzame zware platformklasse.",
        "pl": "Rzadka klasa ciężkich platform.", "pt": "Uma classe rara de plataforma pesada.",
        "ru": "Редкий класс тяжёлых платформ.", "zh-CN": "罕见的重型平台级别。", "zh-TW": "罕見的重型平台級別。"
    },
    "The starter bot, the flagship and limited/event models.": {
        "cs": "Startovní robot, vlajková loď a limitované/událostní modely.",
        "de": "Der Starter-Bot, das Flaggschiff und limitierte/Event-Modelle.",
        "es": "El robot inicial, el buque insignia y los modelos limitados o de evento.",
        "fr": "Le robot de départ, le vaisseau amiral et les modèles limités ou d'événement.",
        "it": "Il bot iniziale, l'ammiraglia e i modelli limitati o di eventi.",
        "ja": "初期ボット、旗艦、および限定/イベントモデル。",
        "ko": "스타터 봇, 기함 및 한정/이벤트 모델.",
        "nl": "De starterbot, het vlaggenschip en gelimiteerde/evenementmodellen.",
        "pl": "Początkowy robot, okręt flagowy oraz modele limitowane i eventowe.",
        "pt": "O robô inicial, a nau-capitânia e os modelos limitados/de eventos.",
        "ru": "Стартовый бот, флагман и ограниченные/событийные модели.",
        "zh-CN": "初始机器人、旗舰以及限定/活动型号。",
        "zh-TW": "初始機器人、旗艦以及限定/活動型號。"
    },
    "Complete cult-designed loadouts unlocked through research — a finished fit rather than a standalone chassis (size comes from the parts it is built from).": {
        "cs": "Kompletní konfigurace navržené kulty odemčené výzkumem — hotová výbava spíše než samostatný podvozek (velikost vychází z použitých dílů).",
        "de": "Komplette, von Kulten entworfene Ausrüstungen, die durch Forschung freigeschaltet werden – ein fertiger Fit statt eines einzelnen Chassis (die Größe ergibt sich aus den verwendeten Teilen).",
        "es": "Equipamientos completos diseñados por cultos y desbloqueados mediante investigación: una configuración lista en lugar de un chasis independiente (el tamaño proviene de las piezas utilizadas).",
        "fr": "Équipements complets conçus par les cultes débloqués par la recherche — une configuration prête à l'emploi plutôt qu'un châssis autonome (la taille dépend des pièces choisies).",
        "it": "Dotazioni complete progettate dai culti sbloccate tramite ricerca: una configurazione pronta anziché un telaio autonomo (le dimensioni dipendono dalle parti con cui è costruita).",
        "ja": "研究によって解放されるカルト設計の完全装備 — 単体のシャーシではなく完成された艤装（サイズは構成パーツによって決まります）。",
        "ko": "연구를 통해 해금되는 컬트 설계의 완성형 구성 — 독립 섀시가 아닌 사전 완성형 핏(크기는 조립 부품에 따름).",
        "nl": "Complete door sekten ontworpen uitrustingen ontgrendeld via onderzoek — een kant-en-klare fit in plaats van een los chassis (grootte komt voort uit de gebruikte onderdelen).",
        "pl": "Kompletne zestawy zaprojektowane przez kulty odblokowywane badaniami — gotowa konfiguracja zamiast samodzielnego kadłuba (rozmiar wynika z zamontowanych części).",
        "pt": "Equipamentos completos projetados por seitas desbloqueados por pesquisa — um ajuste pronto em vez de um chassi avulso (o tamanho vem das peças que o compõem).",
        "ru": "Полные сборки культов, открываемые через исследования — готовая сборка, а не отдельное шасси (размер определяется используемыми деталями).",
        "zh-CN": "通过研究解锁的邪教设计完整装备 — 预设好的成品配置而非单独底盘（尺寸由构成部件决定）。",
        "zh-TW": "透過研究解鎖的邪教設計完整裝備 — 預設好的成品配置而非單獨底盤（尺寸由構成部件決定）。"
    },
    "*Strengths:* a ready-made combat build with its role in the name (main combat / main support).": {
        "cs": "*Přednosti:* hotová bojová sestava s rolí přímo v názvu (hlavní boj / hlavní podpora).",
        "de": "*Stärken:* ein vorgefertigter Kampf-Build mit seiner Rolle direkt im Namen (Hauptkampf / Hauptunterstützung).",
        "es": "*Puntos fuertes:* una configuración de combate prediseñada con su función en el nombre (combate principal / apoyo principal).",
        "fr": "*Points forts :* une configuration de combat prête à l'emploi avec son rôle dans le nom (combat principal / soutien principal).",
        "it": "*Punti di forza:* una configurazione da combattimento pronta all'uso con il suo ruolo nel nome (combattimento principale / supporto principale).",
        "ja": "*長所：* 名前に役割（主力戦闘 / 主力支援）が明記された完成済みの戦闘ビルド。",
        "ko": "*장점:* 이름에 역할(주력 전투 / 주력 지원)이 명시된 완성형 전투 빌드.",
        "nl": "*Sterke punten:* een kant-en-klare gevechtsbuild met zijn rol direct in de naam (hoofdgevecht / hoofdondersteuning).",
        "pl": "*Mocne strony:* gotowa konfiguracja bojowa z rolą określoną w nazwie (walka główna / wsparcie główne).",
        "pt": "*Pontos fortes:* uma montagem de combate pronta com sua função no nome (combate principal / suporte principal).",
        "ru": "*Преимущества:* готовая боевая сборка с указанием роли в названии (основной бой / основная поддержка).",
        "zh-CN": "*优势：* 预设好的现成战斗配置，其定位直接体现在名称中（主力战斗 / 主力支援）。",
        "zh-TW": "*優勢：* 預設好的現成戰鬥配置，其定位直接體現在名稱中（主力戰鬥 / 主力支援）。"
    },
    "*Weaknesses:* fixed by the design — you take the fit as it comes.": {
        "cs": "*Slabiny:* dané konstrukcí — konfiguraci musíte přijmout takovou, jaká je.",
        "de": "*Schwächen:* durch das Design festgelegt – Sie müssen die Ausrüstung so übernehmen, wie sie ist.",
        "es": "*Debilidades:* fijadas por el diseño: debes aceptar el equipamiento tal como viene.",
        "fr": "*Points faibles :* fixes de par leur conception — vous devez utiliser la configuration telle qu'elle est.",
        "it": "*Punti deboli:* vincolati dal design: la configurazione va utilizzata così com'è.",
        "ja": "*短所：* 設計が固定されており、変更できずそのまま使用する必要があります。",
        "ko": "*단점:* 설계 고정 — 사전 정의된 구성 그대로 사용해야 합니다.",
        "nl": "*Zwakke punten:* vastgelegd door het ontwerp — je neemt de fit zoals hij is.",
        "pl": "*Słabe strony:* ustalone konstrukcyjnie — konfiguracja musi być używana bez zmian.",
        "pt": "*Pontos fracos:* fixados pelo projeto — você precisa usar a montagem exatamente como vem.",
        "ru": "*Недостатки:* фиксированная конструкция — сборка используется строго в исходном виде.",
        "zh-CN": "*劣势：* 设计固定 — 必须按原样接受其配置。",
        "zh-TW": "*劣勢：* 設計固定 — 必須按原樣接受其配置。"
    },
    "Mixed-class builds assembled from parts of different robot classes rather than one pure class. They are built from parts, not sold as a finished robot; the finished size comes from the parts chosen.": {
        "cs": "Smíšené sestavy složené z dílů různých tříd robotů namísto jedné čisté třídy. Staví se z dílů, neprodávají se jako hotoví roboti; konečná velikost vychází ze zvolených dílů.",
        "de": "Gemischte Klassen-Builds, die aus Teilen verschiedener Roboterklassen zusammengesetzt sind, anstatt aus einer reinen Klasse. Sie werden aus Teilen gebaut und nicht als fertiger Roboter verkauft; die endgültige Größe ergibt sich aus den gewählten Teilen.",
        "es": "Construcciones de clases mixtas ensambladas a partir de piezas de diferentes clases de robots en lugar de una clase pura. Se construyen a partir de piezas, no se venden como un robot terminado; el tamaño final proviene de las piezas elegidas.",
        "fr": "Châssis mixtes assemblés à partir de pièces de différentes classes de robots plutôt que d'une seule classe pure. Ils sont construits à partir de pièces et ne sont pas vendus comme robots finis ; la taille finale dépend des pièces choisies.",
        "it": "Configurazioni a classi miste assemblate con componenti di diverse classi di robot anziché di una sola pura. Vengono costruite a partire dai pezzi e non vendute come robot completi; le dimensioni finali dipendono dalle parti scelte.",
        "ja": "単一の純粋なクラスではなく、異なるロボットクラスのパーツを組み合わせて作られた混合クラスの機体。完成品としては販売されずパーツから組み立てられ、サイズは選択したパーツによって決まります。",
        "ko": "단일 순수 클래스가 아닌 여러 로봇 클래스의 부품을 조합하여 조립한 복합 클래스 빌드입니다. 완성형 로봇으로 판매되지 않고 부품으로 조립하며, 완성 크기는 선택한 부품에 따릅니다.",
        "nl": "Gemengde klasse-builds samengesteld uit onderdelen van verschillende robotklassen in plaats van één pure klasse. Ze worden gebouwd uit onderdelen, niet verkocht als een voltooide robot; de uiteindelijke grootte hangt af van de gekozen onderdelen.",
        "pl": "Zestawy mieszane składane z części różnych klas robotów zamiast jednej czystej klasy. Są budowane z części i niesprzedawane jako gotowy robot; ostateczny rozmiar wynika z wybranych elementów.",
        "pt": "Montagens de classes mistas montadas a partir de peças de diferentes classes de robôs em vez de uma classe pura. Elas são construídas a partir de peças, não vendidas como um robô pronto; o tamanho final vem das peças escolhidas.",
        "ru": "Сборки смешанных классов, собранные из компонентов разных классов роботов, а не одного чистого класса. Они собираются из деталей, а не продаются готовыми; итоговый размер определяется выбранными компонентами.",
        "zh-CN": "由不同机器人级别的部件组合而成的混合级别机型，而非单一纯级别。它们由零部件组装而成，不作为成品机器人销售；最终尺寸由所选部件决定。",
        "zh-TW": "由不同機器人級別的部件組合而成的混合級別機型，而非單一純級別。它們由零部件組裝而成，不作為成品機器人銷售；最終尺寸由所選部件決定。"
    },
    "*Strengths:* mix the advantages of several classes in one build.": {
        "cs": "*Přednosti:* kombinace výhod několika tříd v jedné sestavě.",
        "de": "*Stärken:* vereinen die Vorteile mehrerer Klassen in einem Build.",
        "es": "*Puntos fuertes:* combina las ventajas de varias clases en una sola configuración.",
        "fr": "*Points forts :* combinent les avantages de plusieurs classes en un seul châssis.",
        "it": "*Punti di forza:* combinano i vantaggi di più classi in una sola configurazione.",
        "ja": "*長所：* 複数のクラスの長所を1つのビルドに融合。",
        "ko": "*장점:* 여러 클래스의 장점을 하나의 빌드에 조합.",
        "nl": "*Sterke punten:* combineer de voordelen van verschillende klassen in één build.",
        "pl": "*Mocne strony:* łączenie zalet kilku klas w jednej konstrukcji.",
        "pt": "*Pontos fortes:* combina as vantagens de várias classes em uma única montagem.",
        "ru": "*Преимущества:* сочетание достоинств нескольких классов в одной сборке.",
        "zh-CN": "*优势：* 在单次配装中融合多个级别的优势。",
        "zh-TW": "*優勢：* 在單次配裝中融合多個級別的優勢。"
    },
    "*Weaknesses:* you must assemble the parts yourself — no single finished product to buy.": {
        "cs": "*Slabiny:* díly musíte sestavit sami — nelze koupit jako jeden hotový výrobek.",
        "de": "*Schwächen:* Sie müssen die Teile selbst zusammenbauen – kein einzelnes fertiges Produkt zum Kauf.",
        "es": "*Debilidades:* debes ensamblar las piezas tú mismo: no hay un producto terminado único para comprar.",
        "fr": "*Points faibles :* vous devez assembler les pièces vous-même — aucun produit fini unique à acheter.",
        "it": "*Punti deboli:* devi assemblare i componenti da solo: nessun prodotto finito acquistabile direttamente.",
        "ja": "*短所：* パーツを自身で組み立てる必要があり、単一の完成品を購入することはできません。",
        "ko": "*단점:* 부품을 직접 조립해야 함 — 단일 완제품으로 구매 불가.",
        "nl": "*Zwakke punten:* je moet de onderdelen zelf in elkaar zetten — geen enkel afgewerkt product te koop.",
        "pl": "*Słabe strony:* części musisz złożyć samodzielnie — brak gotowego pojedynczego produktu do kupienia.",
        "pt": "*Pontos fracos:* você mesmo deve montar as peças — nenhum produto acabado avulso para compra.",
        "ru": "*Недостатки:* компоненты необходимо собирать самостоятельно — готовое изделие купить нельзя.",
        "zh-CN": "*劣势：* 必须自行组装部件 — 没有可直接购买的单一成品。",
        "zh-TW": "*劣勢：* 必須自行組裝部件 — 沒有可直接購買的單一成品。"
    },
    "Combat units fielded by the NPC factions (not acquirable by players).": {
        "cs": "Bojové jednotky nasazené frakcemi NPC (hráči je nemohou získat).",
        "de": "Kampfeinheiten der NPC-Fraktionen (nicht von Spielern erwerbbar).",
        "es": "Unidades de combate desplegadas por las facciones PNJ (no adquiribles por los jugadores).",
        "fr": "Unités de combat déployées par les factions PNJ (non acquérables par les joueurs).",
        "it": "Unità da combattimento schierate dalle fazioni PNG (non acquisibili dai giocatori).",
        "ja": "NPC勢力が展開する戦闘ユニット（プレイヤーは入手不可）。",
        "ko": "NPC 세력이 배치한 전투 유닛(플레이어 획득 불가).",
        "nl": "Gevechtseenheden ingezet door de NPC-facties (niet verkrijgbaar door spelers).",
        "pl": "Jednostki bojowe wystawiane przez frakcje NPC (niedostępne dla graczy).",
        "pt": "Unidades de combate empregadas pelas facções NPC (não adquiríveis por jogadores).",
        "ru": "Боевые единицы фракций NPC (недоступны для игроков).",
        "zh-CN": "NPC 势力部署的战斗单位（玩家不可获取）。",
        "zh-TW": "NPC 勢力部署的戰鬥單位（玩家不可獲取）。"
    },
    "Stats vary by parts": {
        "cs": "Statistiky se liší podle dílů", "de": "Werte variieren je nach Teilen", "es": "Las estadísticas varían según las piezas", "fr": "Les statistiques varient selon les pièces", "it": "Le statistiche variano in base ai componenti",
        "ja": "パーツにより性能が変化", "ko": "부품에 따라 능력치 변동", "nl": "Statistieken variëren per onderdeel", "pl": "Statystyki zależą od części", "pt": "Os atributos variam conforme as peças",
        "ru": "Параметры зависят от деталей", "zh-CN": "属性因部件而异", "zh-TW": "屬性因部件而異"
    },
    "NPC unit — not player-acquirable": {
        "cs": "Jednotka NPC — hráč ji nemůže získat", "de": "NPC-Einheit – nicht von Spielern erwerbbar", "es": "Unidad PNJ: no adquirible por jugadores", "fr": "Unité PNJ — non acquérable par les joueurs", "it": "Unità PNG — non acquisibile dai giocatori",
        "ja": "NPCユニット — プレイヤー入手不可", "ko": "NPC 유닛 — 플레이어 획득 불가", "nl": "NPC-eenheid — niet verkrijgbaar door spelers", "pl": "Jednostka NPC — niedostępna dla graczy", "pt": "Unidade NPC — não adquirível por jogadores",
        "ru": "Единица NPC — недоступна для игроков", "zh-CN": "NPC 单位 — 玩家不可获取", "zh-TW": "NPC 單位 — 玩家不可獲取"
    },
    "Robot": {
        "cs": "Robot", "de": "Roboter", "es": "Robot", "fr": "Robot", "it": "Robot",
        "ja": "ロボット", "ko": "로봇", "nl": "Robot", "pl": "Robot", "pt": "Robô",
        "ru": "Робот", "zh-CN": "机器人", "zh-TW": "機器人"
    },
}

UI_STRINGS = {}
translations_dir = Path("translations")
if translations_dir.exists():
    import json
    for tf in translations_dir.glob("*.json"):
        try:
            with open(tf, "r", encoding="utf-8") as fh:
                d = json.load(fh)
                if "lang" in d and "ui" in d:
                    UI_STRINGS[d["lang"]] = d["ui"]
        except Exception:
            pass


def get_ui(lang, key, default=None):
    return UI_STRINGS.get(lang, {}).get(key, default or key)


TRANSLATED_CONTENT_SECTIONS = [
    "ores", "plants", "missions", "deployables", "robots",
    "recipes", "techtree", "extensions", "stat-reference", "shop"
]


def tr(key, lang, default=None):
    if key in I18N and lang in I18N[key]:
        return I18N[key][lang]
    return default if default is not None else key


def rewrite_links(text, lang):
    """Rewrite absolute links to include the language prefix for translated sections."""
    # Pattern for markdown links: [text](/path/)
    # and HTML links: href="/path/"

    def repl_href(m):
        prefix = m.group(1)  # 'href="' or ']('
        path = m.group(2)
        suffix = m.group(3)  # '"' or ')'

        # Exclude anchor-only or full URLs
        if path.startswith("http://") or path.startswith("https://") or path.startswith("#"):
            return m.group(0)

        # Localized zones routes
        if path in ("/zones/", "/zones/protection/", "/zones/protection"):
            return f"{prefix}/{lang}{path}{suffix}"

        # Exclude unlocalized global paths
        if path.startswith("/content/items/") or path.startswith("/zones/"):
            return m.group(0)

        # Features, formats, menu routes
        for sec in ("features", "formats", "menu"):
            if path == f"/{sec}/" or path.startswith(f"/{sec}/"):
                return f"{prefix}/{lang}{path}{suffix}"

        # Root content index
        if path == "/content/":
            return f"{prefix}/{lang}/content/{suffix}"

        # Subsections in content
        for sec in TRANSLATED_CONTENT_SECTIONS:
            if path == f"/content/{sec}/" or path.startswith(f"/content/{sec}/"):
                return f"{prefix}/{lang}{path}{suffix}"

        # Root or other pages
        if path == "/":
            return f"{prefix}/{lang}/{suffix}"

        return m.group(0)

    # Replace href="..."
    text = re.sub(r'(href=["\'])(/[^"\']*)(["\'])', repl_href, text)
    # Replace markdown links: ](/path/)
    text = re.sub(r'(\]\()(/[^)\s]+)(\))', repl_href, text)
    return text


def translate_frontmatter(text, lang, title_prefix=None):
    """Translate YAML frontmatter title and description."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    new_lines = []
    in_fm = False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_fm and i == 0:
                in_fm = True
                new_lines.append(line)
                continue
            elif in_fm:
                in_fm = False
                new_lines.append(line)
                continue

        if in_fm:
            # We preserve frontmatter or adjust specific known fields
            new_lines.append(line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def process_robot_file(content, lang):
    """Translate an individual robot page."""
    c = rewrite_links(content, lang)

    # Translate card stats
    for stat in ["Combat", "Speed", "Armor", "Storage", "Cost"]:
        stat_tr = tr(stat, lang)
        c = re.sub(rf'<span>{stat}</span>', f'<span>{stat_tr}</span>', c)

    # Translate properties table
    for prop in ["Class", "Size", "Mass", "Health", "Purchasable"]:
        prop_tr = tr(prop, lang)
        c = re.sub(rf'<td>{prop}</td>', f'<td>{prop_tr}</td>', c)

    yes_tr = tr("Yes", lang)
    no_tr = tr("No", lang)
    c = re.sub(r'<td>Yes</td>', f'<td>{yes_tr}</td>', c)
    c = re.sub(r'<td>No</td>', f'<td>{no_tr}</td>', c)

    # Translate section headers & production
    c = c.replace("## Variants", f"## {tr('Variants', lang)}")
    c = c.replace("| Variant | Link |", f"| {tr('Variant', lang)} | {tr('Link', lang)} |")
    c = c.replace("## Production", f"## {tr('Production', lang)}")
    c = c.replace("Components required to build this robot:", tr("Components required to build this robot:", lang))
    c = c.replace("| Component | Amount |", f"| {tr('Component', lang)} | {tr('Amount', lang)} |")

    c = c.replace("## NPC Vendor", f"## {tr('NPC Vendor', lang)}")
    c = c.replace("Available from the NPC vendor:", tr("Available from the NPC vendor:", lang))
    c = c.replace("**Price:**", f"**{tr('Price:', lang)}**")

    # Frontmatter description: "{Name} — robot stats, production and availability."
    m = re.search(r'title:\s*"([^"]+)"', c)
    if m:
        bot_name = m.group(1)
        desc_tr = tr("{Robot} — robot stats, production and availability.", lang).replace("{Robot}", bot_name).replace("{name}", bot_name)
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{desc_tr}"', c)

    return c


def process_ore_file(content, lang):
    """Translate an individual ore page."""
    c = rewrite_links(content, lang)

    c = c.replace("## Extraction", f"## {tr('Extraction', lang)}")
    c = c.replace("| Property | Value |", f"| {tr('Property', lang)} | {tr('Value', lang)} |")
    c = c.replace("| Amount / extraction |", f"| {tr('Amount / extraction', lang)} |")
    c = c.replace("| Extraction type |", f"| {tr('Extraction type', lang)} |")
    c = c.replace("| Enabler effect |", f"| {tr('Enabler effect', lang)} |")
    c = c.replace("| Geo-scan document |", f"| {tr('Geo-scan document', lang)} |")

    c = c.replace("liquid (pumped continuously)", tr("liquid (pumped continuously)", lang))
    c = c.replace("solid (tile-by-tile drill)", tr("solid (tile-by-tile drill)", lang))
    c = c.replace("not required", tr("not required", lang))
    c = c.replace("| required |", f"| {tr('required', lang)} |")

    c = c.replace("## Where it spawns", f"## {tr('Where it spawns', lang)}")
    c = c.replace(
        "| Zone | Max nodes | Max tiles / node | Total amount / node | Min threshold |",
        f"| {tr('Zone', lang, 'Zone')} | {tr('Max nodes', lang, 'Max nodes')} | {tr('Max tiles / node', lang, 'Max tiles / node')} | {tr('Total amount / node', lang, 'Total amount / node')} | {tr('Min threshold', lang, 'Min threshold')} |"
    )

    c = c.replace("## Made from it", f"## {tr('Made from it', lang)}")
    c = c.replace("| Item | Amount |", f"| {tr('Item', lang)} | {tr('Amount', lang)} |")

    return c


def process_deployable_file(content, lang):
    """Translate an individual deployable page."""
    c = rewrite_links(content, lang)

    for field in ["Definition", "Category", "Tier", "Health", "Volume", "Mass"]:
        f_tr = tr(field, lang)
        c = re.sub(rf'\|\s*{field}\s*\|', f'| {f_tr} |', c)

    c = c.replace("## Stats", f"## {tr('Stats', lang)}")
    c = c.replace("| Field | Value |", f"| {tr('Field', lang)} | {tr('Value', lang)} |")

    all_dep = tr("All deployables", lang, "All deployables")
    dep_f = tr("Deployable fields", lang, "Deployable fields")
    c = re.sub(r'\[All deployables\]\([^)]+\)', f'[{all_dep}](/{lang}/content/deployables/)', c)
    c = re.sub(r'\[Deployable fields\]\([^)]+\)', f'[{dep_f}](/{lang}/formats/deployable-fields/)', c)

    return c


def process_shop_file(content, lang):
    """Translate an individual shop category page."""
    c = rewrite_links(content, lang)

    # Table header
    c = c.replace(
        "| Item | Qty | TM Coin | ICS Coin | ASI Coin | Credits | UniCoin | Vendors |",
        f"| {tr('Item', lang)} | {tr('Qty', lang)} | TM Coin | ICS Coin | ASI Coin | Credits | UniCoin | {tr('Vendors', lang)} |"
    )

    # Breadcrumb
    item_shop = tr("Item shop", lang, "Item shop")
    c = re.sub(r'\[Item shop\]\([^)]+\)', f'[{item_shop}](/{lang}/content/shop/)', c)

    return c


def process_techtree_group_file(content, lang):
    """Translate a techtree group page."""
    c = rewrite_links(content, lang)

    tt = tr("Tech tree", lang, "Tech tree")
    c = re.sub(r'\[Tech tree\]\([^)]+\)', f'[{tt}](/{lang}/content/techtree/)', c)

    # Line descriptions: "**16 nodes** — everything that descends from"
    def repl_nodes(m):
        count = m.group(1)
        nodes_tr = tr("nodes", lang, "nodes")
        from_tr = tr("everything that descends from", lang, "everything that descends from")
        return f"**{count} {nodes_tr}** — {from_tr}"

    c = re.sub(r'\*\*(\d+)\s+nodes\*\*\s*—\s*everything that descends from', repl_nodes, c)

    return c


def process_techtree_node_file(content, lang):
    """Translate an individual tech tree node page."""
    c = rewrite_links(content, lang)

    for field in ["Category", "Unlocks", "Parent node", "Unlocks next", "Enabler extension", "Point prices"]:
        f_tr = tr(field, lang)
        c = re.sub(rf'\|\s*{field}\s*\|', f'| {f_tr} |', c)

    all_nodes = tr("All tech tree nodes", lang)
    c = re.sub(r'\[All tech tree nodes\]\([^)]+\)', f'[{all_nodes}](/{lang}/content/techtree/)', c)

    return c


def process_recipes_file(content, lang):
    """Translate recipes.md (2.9 MB)."""
    c = rewrite_links(content, lang)
    recipes_tr = get_ui(lang, "nav_content_recipes", "Recipes")
    c = re.sub(r'title:\s*"Recipes"', f'title: "{recipes_tr}"', c)
    c = re.sub(r'^#\s*Recipes', f'# {recipes_tr}', c, flags=re.MULTILINE)

    res_lvl = tr("Research level", lang)
    c = re.sub(r'<div class="mission-card-sub">Research level\s+(\d+)</div>',
               rf'<div class="mission-card-sub">{res_lvl} \1</div>', c)

    return c


def process_missions_file(content, lang):
    """Translate missions.md."""
    c = rewrite_links(content, lang)
    missions_tr = get_ui(lang, "nav_content_missions", "Missions")
    c = re.sub(r'title:\s*"Missions"', f'title: "{missions_tr}"', c)
    c = re.sub(r'^#\s*Missions', f'# {missions_tr}', c, flags=re.MULTILINE)

    lvl_tr = tr("Level", lang)
    c = re.sub(r'<div class="mission-card-title">Level\s+(\d+)</div>',
               rf'<div class="mission-card-title">{lvl_tr} \1</div>', c)

    fee_tr = tr("Reward fee", lang)
    c = re.sub(r'<div class="mission-card-sub">Reward fee\s+([^<]+)</div>',
               rf'<div class="mission-card-sub">{fee_tr} \1</div>', c)

    dur_tr = tr("Duration", lang)
    min_tr = tr("min", lang)
    c = re.sub(r'<div class="mission-card-sub">Duration\s+(\d+)\s+min</div>',
               rf'<div class="mission-card-sub">{dur_tr} \1 {min_tr}</div>', c)

    return c


def process_extensions_file(content, lang):
    """Translate extensions.md."""
    c = rewrite_links(content, lang)
    ext_tr = get_ui(lang, "nav_extensions", "Extensions")
    c = re.sub(r'title:\s*"Extensions"', f'title: "{ext_tr}"', c)
    c = re.sub(r'^#\s*Extensions', f'# {ext_tr}', c, flags=re.MULTILINE)

    rank_tr = tr("rank", lang)
    c = re.sub(r'<span class="ext-val-rank">rank\s+(\d+)</span>',
               rf'<span class="ext-val-rank">{rank_tr} \1</span>', c)

    bonus_tr = tr("bonus", lang)
    c = re.sub(r'<span class="ext-val-bonus">bonus\s+([^<]+)</span>',
               rf'<span class="ext-val-bonus">{bonus_tr} \1</span>', c)

    inact_tr = tr("inactive", lang)
    c = re.sub(r'·\s*inactive', f'· {inact_tr}', c)

    nopreq_tr = tr("no prerequisites", lang)
    c = re.sub(r'<div class="ext-card-prereq">no prerequisites</div>',
               rf'<div class="ext-card-prereq">{nopreq_tr}</div>', c)

    return c


def process_content_overview(content, lang):
    """Translate content/_index.md."""
    c = rewrite_links(content, lang)
    content_tr = get_ui(lang, "foot_content", "Content")
    c = re.sub(r'title:\s*"Content"', f'title: "{content_tr}"', c)
    c = re.sub(r'^#\s*Content', f'# {content_tr}', c, flags=re.MULTILINE)
    return c


def process_ores_overview(content, lang):
    """Translate content/ores.md."""
    c = rewrite_links(content, lang)
    ores_tr = get_ui(lang, "nav_content_ores", "Ores")
    c = re.sub(r'title:\s*"Ores"', f'title: "{ores_tr}"', c)
    c = re.sub(r'^#\s*Ores', f'# {ores_tr}', c, flags=re.MULTILINE)

    ore_types_tr = tr("Ore types", lang, "Ore types")
    c = c.replace("## Ore types", f"## {ore_types_tr}")

    c = c.replace("<th>Ore</th>", f"<th>{tr('Ore', lang, 'Ore')}</th>")
    c = c.replace("<th>Amount / extraction</th>", f"<th>{tr('Amount / extraction', lang)}</th>")
    c = c.replace("<th>Extraction type</th>", f"<th>{tr('Extraction type', lang)}</th>")
    c = c.replace("<th>Enabler effect</th>", f"<th>{tr('Enabler effect', lang)}</th>")
    c = c.replace("<th>Geo-scan doc</th>", f"<th>{tr('Geo-scan doc', lang)}</th>")

    no_tr = tr("no", lang, "no")
    req_tr = tr("required", lang, "required")
    c = c.replace("<td>no</td>", f"<td>{no_tr}</td>")
    c = c.replace("<td>required</td>", f"<td>{req_tr}</td>")
    return c


def process_plants_overview(content, lang):
    """Translate content/plants.md."""
    c = rewrite_links(content, lang)
    plants_tr = get_ui(lang, "nav_content_plants", "Plants")
    c = re.sub(r'title:\s*"Plants"', f'title: "{plants_tr}"', c)
    c = re.sub(r'^#\s*Plants', f'# {plants_tr}', c, flags=re.MULTILINE)
    return c


def process_deployables_overview(content, lang):
    """Translate content/deployables.md."""
    c = rewrite_links(content, lang)
    dep_tr = get_ui(lang, "nav_content_deployables", "Deployables")
    c = re.sub(r'title:\s*"Deployables"', f'title: "{dep_tr}"', c)
    c = re.sub(r'^#\s*Deployables', f'# {dep_tr}', c, flags=re.MULTILINE)

    no_tier_tr = tr("no tier", lang)
    c = re.sub(r'<div class="prod-card-body">no tier</div>',
               rf'<div class="prod-card-body">{no_tier_tr}</div>', c)
    return c


def process_robots_overview(content, lang):
    """Translate content/robots.md."""
    c = rewrite_links(content, lang)
    robots_tr = get_ui(lang, "home_robots", "Robots")
    c = re.sub(r'title:\s*"Robots"', f'title: "{robots_tr}"', c)
    c = re.sub(r'^#\s*Robots', f'# {robots_tr}', c, flags=re.MULTILINE)

    desc_tr = tr("How a robot is built, the robot classes, and every robot: player, hybrid and NPC.", lang)
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{desc_tr}"', c)

    intro_tr = tr("Fitting, slots and in-game play are covered in the [Robot](/features/robots/) feature page; this page is the data reference.", lang)
    intro_tr = intro_tr.replace("{lang}", lang)
    c = re.sub(r'Fitting, slots and in-game play are covered in the \[Robot\]\([^)]+\) feature page; this page is the data reference\.', intro_tr, c)

    c = c.replace("## Robot classes", f"## {tr('Robot classes', lang, 'Robot classes')}")
    c = c.replace(
        "A robot's class comes from its parts. Ratings are 1–5 (more icons = higher).",
        tr("A robot's class comes from its parts. Ratings are 1–5 (more icons = higher).", lang)
    )

    # Class ratings table
    c = c.replace("<th>Class</th>", f"<th>{tr('Class', lang)}</th>")
    for stat in ["Combat", "Speed", "Armor", "Storage", "Cost"]:
        stat_tr = tr(stat, lang)
        c = re.sub(rf'<th>{stat}</th>', f'<th>{stat_tr}</th>', c)
        c = re.sub(rf'<span>{stat}</span>', f'<span>{stat_tr}</span>', c)

    # Table rows class names
    for cls in ["Runners", "Crawlers", "Mechs", "Heavy mechs", "Walkers"]:
        c = c.replace(f"<b>{cls}</b>", f"<b>{tr(cls, lang)}</b>")

    c = c.replace("## Player robots", f"## {tr('Player robots', lang, 'Player robots')}")
    c = c.replace(
        "Robots you can acquire and control yourself (80 models), grouped by class.",
        tr("Robots you can acquire and control yourself (80 models), grouped by class.", lang)
    )

    # Subsection headings
    c = c.replace("### Runners (20)", f"### {tr('Runners', lang)} (20)")
    c = c.replace("### Crawlers (11)", f"### {tr('Crawlers', lang)} (11)")
    c = c.replace("### Mechs (19)", f"### {tr('Mechs', lang)} (19)")
    c = c.replace("### Heavy mechs (18)", f"### {tr('Heavy mechs', lang)} (18)")
    c = c.replace("### Walkers (2)", f"### {tr('Walkers', lang)} (2)")
    c = c.replace("### Starter & special (10)", f"### {tr('Starter & special', lang)} (10)")
    c = c.replace("### Named fits (3)", f"### {tr('Named fits', lang)} (3)")
    c = c.replace("## Hybrid builds (27)", f"## {tr('Hybrid builds', lang)} (27)")
    c = c.replace("## NPC units (1)", f"## {tr('NPC units', lang)} (1)")

    # Subsection descriptions
    for desc in [
        "The fast, light class — the cheapest robots to build and pilot.",
        "The mid-size workhorse class.",
        "The main combat class.",
        "The top-tier combat class.",
        "A rare heavy platform class.",
        "The starter bot, the flagship and limited/event models.",
        "Complete cult-designed loadouts unlocked through research — a finished fit rather than a standalone chassis (size comes from the parts it is built from).",
        "*Strengths:* a ready-made combat build with its role in the name (main combat / main support).",
        "*Weaknesses:* fixed by the design — you take the fit as it comes.",
        "Mixed-class builds assembled from parts of different robot classes rather than one pure class. They are built from parts, not sold as a finished robot; the finished size comes from the parts chosen.",
        "*Strengths:* mix the advantages of several classes in one build.",
        "*Weaknesses:* you must assemble the parts yourself — no single finished product to buy.",
        "Combat units fielded by the NPC factions (not acquirable by players).",
    ]:
        c = c.replace(desc, tr(desc, lang))

    # Named fits table header
    c = c.replace("| Robot | Class |", f"| {tr('Robot', lang)} | {tr('Class', lang)} |")

    # Card status labels
    c = c.replace("<span>Stats vary by parts</span>", f"<span>{tr('Stats vary by parts', lang)}</span>")
    c = c.replace("<span>NPC unit — not player-acquirable</span>", f"<span>{tr('NPC unit — not player-acquirable', lang)}</span>")

    return c


def process_techtree_overview(content, lang):
    """Translate content/techtree/_index.md."""
    c = rewrite_links(content, lang)
    tt_tr = get_ui(lang, "nav_content_techtree", "Tech tree")
    c = re.sub(r'title:\s*"Tech tree"', f'title: "{tt_tr}"', c)
    c = re.sub(r'^#\s*Tech tree', f'# {tt_tr}', c, flags=re.MULTILINE)
    c = c.replace("## Categories", f"## {tr('Categories', lang, 'Categories')}")
    return c


def process_shop_overview(content, lang):
    """Translate content/shop.md."""
    c = rewrite_links(content, lang)
    shop_tr = get_ui(lang, "nav_shop", "Item shop")
    c = re.sub(r'title:\s*"Item shop"', f'title: "{shop_tr}"', c)
    c = re.sub(r'^#\s*Item shop', f'# {shop_tr}', c, flags=re.MULTILINE)
    c = c.replace("## Vendors", f"## {tr('Vendors', lang, 'Vendors')}")
    c = c.replace("## Catalog", f"## {tr('Catalog', lang, 'Catalog')}")
    return c


def process_stat_reference_file(content, lang):
    """Translate content/stat-reference.md."""
    c = rewrite_links(content, lang)
    stat_tr = get_ui(lang, "nav_content_statref", "Stat reference")
    c = re.sub(r'title:\s*"Stat reference"', f'title: "{stat_tr}"', c)
    c = re.sub(r'^#\s*Stat reference', f'# {stat_tr}', c, flags=re.MULTILINE)
    return c


def process_generic_file(content, lang):
    """Fallback translation processor with link rewriting and common badges."""
    c = rewrite_links(content, lang)

    no_tier_tr = tr("no tier", lang)
    c = re.sub(r'<div class="prod-card-body">no tier</div>',
               rf'<div class="prod-card-body">{no_tier_tr}</div>', c)

    return c


def main():
    root = Path(".")
    src_content_dir = root / "content" / "content"

    if not src_content_dir.exists():
        print(f"gen_content_translations: source directory {src_content_dir} not found!", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    total_written = 0

    for lang in LANGUAGES:
        dest_dir = root / "content" / lang / "content"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # 1. Section index: _index.md
        src_idx = src_content_dir / "_index.md"
        if src_idx.exists():
            content = process_content_overview(src_idx.read_text(encoding="utf-8"), lang)
            (dest_dir / "_index.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 2. Ores overview & individual ore pages
        src_ores = src_content_dir / "ores.md"
        if src_ores.exists():
            content = process_ores_overview(src_ores.read_text(encoding="utf-8"), lang)
            (dest_dir / "ores.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_ores_dir = src_content_dir / "ores"
        dest_ores_dir = dest_dir / "ores"
        if src_ores_dir.exists():
            dest_ores_dir.mkdir(exist_ok=True)
            for f in src_ores_dir.glob("*.md"):
                content = process_ore_file(f.read_text(encoding="utf-8"), lang)
                (dest_ores_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 3. Plants
        src_plants = src_content_dir / "plants.md"
        if src_plants.exists():
            content = process_plants_overview(src_plants.read_text(encoding="utf-8"), lang)
            (dest_dir / "plants.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 4. Missions
        src_missions = src_content_dir / "missions.md"
        if src_missions.exists():
            content = process_missions_file(src_missions.read_text(encoding="utf-8"), lang)
            (dest_dir / "missions.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 5. Deployables overview & individual pages
        src_dep = src_content_dir / "deployables.md"
        if src_dep.exists():
            content = process_deployables_overview(src_dep.read_text(encoding="utf-8"), lang)
            (dest_dir / "deployables.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_dep_dir = src_content_dir / "deployables"
        dest_dep_dir = dest_dir / "deployables"
        if src_dep_dir.exists():
            dest_dep_dir.mkdir(exist_ok=True)
            for f in src_dep_dir.glob("*.md"):
                content = process_deployable_file(f.read_text(encoding="utf-8"), lang)
                (dest_dep_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 6. Robots overview & individual robot pages
        src_robots = src_content_dir / "robots.md"
        if src_robots.exists():
            content = process_robots_overview(src_robots.read_text(encoding="utf-8"), lang)
            (dest_dir / "robots.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_robots_dir = src_content_dir / "robots"
        dest_robots_dir = dest_dir / "robots"
        if src_robots_dir.exists():
            dest_robots_dir.mkdir(exist_ok=True)
            for f in src_robots_dir.glob("*.md"):
                content = process_robot_file(f.read_text(encoding="utf-8"), lang)
                (dest_robots_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 7. Recipes (2.9 MB)
        src_recipes = src_content_dir / "recipes.md"
        if src_recipes.exists():
            content = process_recipes_file(src_recipes.read_text(encoding="utf-8"), lang)
            (dest_dir / "recipes.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 8. Tech tree overview & groups
        dest_tt_dir = dest_dir / "techtree"
        dest_tt_dir.mkdir(exist_ok=True)
        src_tt_idx = src_content_dir / "techtree" / "_index.md"
        if src_tt_idx.exists():
            content = process_techtree_overview(src_tt_idx.read_text(encoding="utf-8"), lang)
            (dest_tt_dir / "_index.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_tt_grp_dir = src_content_dir / "techtree" / "groups"
        dest_tt_grp_dir = dest_tt_dir / "groups"
        if src_tt_grp_dir.exists():
            dest_tt_grp_dir.mkdir(exist_ok=True)
            for f in src_tt_grp_dir.glob("*.md"):
                content = process_techtree_group_file(f.read_text(encoding="utf-8"), lang)
                (dest_tt_grp_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        src_tt_node_dir = src_content_dir / "techtree" / "nodes"
        dest_tt_node_dir = dest_tt_dir / "nodes"
        if src_tt_node_dir.exists():
            dest_tt_node_dir.mkdir(exist_ok=True)
            for f in src_tt_node_dir.glob("*.md"):
                content = process_techtree_node_file(f.read_text(encoding="utf-8"), lang)
                (dest_tt_node_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 9. Extensions
        src_ext = src_content_dir / "extensions.md"
        if src_ext.exists():
            content = process_extensions_file(src_ext.read_text(encoding="utf-8"), lang)
            (dest_dir / "extensions.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 10. Stat reference
        src_stat = src_content_dir / "stat-reference.md"
        if src_stat.exists():
            content = process_stat_reference_file(src_stat.read_text(encoding="utf-8"), lang)
            (dest_dir / "stat-reference.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 11. Shop overview & categories
        src_shop = src_content_dir / "shop.md"
        if src_shop.exists():
            content = process_shop_overview(src_shop.read_text(encoding="utf-8"), lang)
            (dest_dir / "shop.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_shop_dir = src_content_dir / "shop"
        dest_shop_dir = dest_dir / "shop"
        if src_shop_dir.exists():
            dest_shop_dir.mkdir(exist_ok=True)
            for f in src_shop_dir.glob("*.md"):
                content = process_shop_file(f.read_text(encoding="utf-8"), lang)
                (dest_shop_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 12. Zones: protection levels & zones index
        dest_zones_dir = Path("content") / lang / "zones"
        dest_zones_dir.mkdir(parents=True, exist_ok=True)

        if lang in PROTECTION_DATA:
            title, desc, body = PROTECTION_DATA[lang]
            md = f"---\ntitle: \"{title}\"\ndescription: \"{desc}\"\nweight: 20\n---\n\n{body}\n"
            md = rewrite_links(md, lang)
            (dest_zones_dir / "protection.md").write_text(md, encoding="utf-8")
            total_written += 1

        if lang in ZONES_INDEX_DATA:
            title, desc, body = ZONES_INDEX_DATA[lang]
            md = f"---\ntitle: \"{title}\"\ndescription: \"{desc}\"\nweight: 50\n---\n\n{body}\n"
            md = rewrite_links(md, lang)
            (dest_zones_dir / "_index.md").write_text(md, encoding="utf-8")
            total_written += 1

    elapsed = time.time() - t0
    print(f"gen_content_translations: wrote {total_written} localized files across {len(LANGUAGES)} languages in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
