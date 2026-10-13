#!/usr/bin/env python3
"""Generate localized zone pages in content/<lang>/zones/ for all 13 supported languages.

Generates:
- content/<lang>/zones/alpha.md
- content/<lang>/zones/beta.md
- content/<lang>/zones/gamma.md
- content/<lang>/zones/zone-index.md
- content/<lang>/zones/map.md
- All 79 generated content/<lang>/zones/zone_*.md pages

Preserves hand-written worked examples and generation.md when already present.
Rewrites all internal links to /{lang}/ routes.
"""
import os
import re
import sys
import time
from pathlib import Path

LANGUAGES = [
    "cs", "de", "es", "fr", "it", "ja", "ko",
    "nl", "pl", "pt", "ru", "zh-CN", "zh-TW"
]

I18N = {
    # Headings & Navigation
    "World map": {
        "cs": "Mapa světa", "de": "Weltkarte", "es": "Mapa del mundo", "fr": "Carte du monde",
        "it": "Mappa del mondo", "ja": "ワールドマップ", "ko": "월드 맵", "nl": "Wereldkaart",
        "pl": "Mapa świata", "pt": "Mapa mundi", "ru": "Карта мира", "zh-CN": "世界地图", "zh-TW": "世界地圖"
    },
    "World": {
        "cs": "Svět", "de": "Welt", "es": "Mundo", "fr": "Monde",
        "it": "Mondo", "ja": "世界", "ko": "월드", "nl": "Wereld",
        "pl": "Świat", "pt": "Mundo", "ru": "Мир", "zh-CN": "世界", "zh-TW": "世界"
    },
    "Zone index": {
        "cs": "Index zón", "de": "Zonenindex", "es": "Índice de zonas", "fr": "Index des zones",
        "it": "Indice delle zone", "ja": "ゾーン一覧", "ko": "존 색인", "nl": "Zone-index",
        "pl": "Indeks stref", "pt": "Índice de zonas", "ru": "Индекс зон", "zh-CN": "区域索引", "zh-TW": "區域索引"
    },
    "Protection levels": {
        "cs": "Úrovně ochrany", "de": "Schutzstufen", "es": "Niveles de protección", "fr": "Niveaux de protection",
        "it": "Livelli di protezione", "ja": "保護レベル", "ko": "보호 레벨", "nl": "Beschermingsniveaus",
        "pl": "Poziomy ochrony", "pt": "Níveis de proteção", "ru": "Уровни защиты", "zh-CN": "保护级别", "zh-TW": "保護級別"
    },
    "Ore configuration": {
        "cs": "Konfigurace rudy", "de": "Erzkonfiguration", "es": "Configuración de mineral", "fr": "Configuration du minerai",
        "it": "Configurazione minerale", "ja": "鉱石構成", "ko": "광석 구성", "nl": "Ertsconfiguratie",
        "pl": "Konfiguracja rudy", "pt": "Configuração de minério", "ru": "Конфигурация руды", "zh-CN": "矿石配置", "zh-TW": "礦石配置"
    },

    # Worldmap card body
    "worldmap_card_desc": {
        "cs": "kde se tato zóna nachází mezi ostatními, se spoji teleportů. Otevřít celou mapu.",
        "de": "wo diese Zone unter allen anderen liegt, mit den Teleportverbindungen. Vollständige Karte öffnen.",
        "es": "dónde se ubica esta zona entre todas las demás, con las conexiones de teletransporte. Abrir el mapa completo.",
        "fr": "où se situe cette zone parmi toutes les autres, avec les liaisons de téléportation. Ouvrir la carte complète.",
        "it": "dove si trova questa zona tra tutte le altre, con i collegamenti di teletrasporto. Apri la mappa completa.",
        "ja": "テレポート接続を含む、全ゾーンの中でのこのゾーンの位置。マップ全体を開く。",
        "ko": "텔레포트 연결을 포함하여 다른 모든 존 사이에서 이 존의 위치. 전체 지도 열기.",
        "nl": "waar deze zone ligt tussen alle andere, met de teleportverbindingen. Open de volledige kaart.",
        "pl": "gdzie znajduje się ta strefa wśród pozostałych, wraz z połączeniami teleportów. Otwórz pełną mapę.",
        "pt": "onde esta zona fica entre todas as outras, com as conexões de teletransporte. Abrir o mapa completo.",
        "ru": "расположение этой зоны среди всех остальных с телепортационными связями. Открыть полную карту.",
        "zh-CN": "该区域在所有区域中的位置及传送连接。打开完整地图。",
        "zh-TW": "該區域在所有區域中的位置及傳送連接。打開完整地圖。"
    },

    # Map image caption
    "map_caption_main": {
        "cs": "Kde stojí teleportační sloupy této zóny (body označené cílem — ztlumené, pokud je sloup vypnutý), místa přistání teleportů přicházejících z jiných zón (čárkované kruhy) a výstupní brány (kosočtverce), pokud existují. Pozice odpovídají souřadnicím dlaždic evidovaným serverem.",
        "de": "Standorte der Teleportsäulen dieser Zone (Punkte mit Zielbeschriftung — gedimmt, wenn die Säule inaktiv ist), Landepunkte eingehender Teleporte aus anderen Zonen (gestrichelte Kreise) und Ausgangstore (Rauten), sofern vorhanden. Die Positionen entsprechen den vom Server erfassten Kachelkoordinaten.",
        "es": "Ubicación de las columnas de teletransporte de esta zona (puntos etiquetados con el destino — atenuados si la columna está desactivada), puntos de llegada de teletransportes desde otras zonas (círculos discontinuos) y puertas de salida (rombos) si existen. Las posiciones corresponden a las coordenadas de casillas registradas por el servidor.",
        "fr": "Emplacements des colonnes de téléportation de cette zone (points étiquetés avec la destination — estompés si la colonne est désactivée), points d'arrivée des téléportations depuis d'autres zones (cercles en pointillés) et portes de sortie (losanges) le cas échéant. Les positions correspondent aux coordonnées de cases enregistrées par le serveur.",
        "it": "Posizioni delle colonne di teletrasporto di questa zona (punti con etichetta di destinazione — oscurati se la colonna è disattivata), punti di arrivo dei teletrasporti da altre zone (cerchi tratteggiati) e varchi di uscita (rombi) ove presenti. Le posizioni sono le coordinate delle tessere registrate dal server.",
        "ja": "このゾーンのテレポート柱の位置（行き先ラベル付きの点 — 停止中の柱は薄暗く表示）、他ゾーンからのテレポート着地点（破線の円）、および出口ゲート（菱形）を示します。位置はサーバーに記録されたタイル座標です。",
        "ko": "이 존의 텔레포트 기둥 위치(목적지가 표시된 점 — 기둥이 비활성화된 경우 흐리게 표시), 다른 존에서 도착하는 텔레포트 착륙 지점(점선 원), 그리고 출구 게이트(다이아몬드)를 나타냅니다. 위치는 서버에 기록된 타일 좌표입니다.",
        "nl": "Waar de teleportkolommen van deze zone staan (stippen met bestemmingslabel — gedimd als de kolom is uitgeschakeld), landingsplekken van teleports uit andere zones (stippellijnen cirkels) en uitgangspoorten (ruiten) waar aanwezig. Posities zijn tegelcoördinaten die de server registreert.",
        "pl": "Lokalizacje kolumn teleportacyjnych tej strefy (punkty z etykietą celu — przyciemnione, gdy kolumna jest wyłączona), miejsca lądowania teleportów z innych stref (przerywane okręgi) oraz bramy wyjściowe (romby), jeśli istnieją. Pozycje odpowiadają współrzędnym pól rejestrowanym przez serwer.",
        "pt": "Onde ficam as colunas de teletransporte desta zona (pontos rotulados com o destino — esmaecidos se a coluna estiver desativada), locais de aterrissagem de teletransportes vindos de outras zonas (círculos tracejados) e portões de saída (losangos) onde existirem. As posições são as coordenadas de blocos registradas pelo servidor.",
        "ru": "Расположение телепортационных колонн этой зоны (точки с указанием назначения — затемнены, если колонна отключена), точки прибытия телепортов из других зон (пунктирные круги) и выходные врата (ромбы) при их наличии. Координаты соответствуют данным сервера.",
        "zh-CN": "本区域传送柱位置（带目标标记的点 — 当前关闭的柱子呈暗淡显示）、来自其他区域的传送着陆点（虚线圆圈）以及出口通道（菱形）。坐标为服务器记录的网格坐标。",
        "zh-TW": "本區域傳送柱位置（帶目標標記的點 — 當前關閉的柱子呈暗淡顯示）、來自其他區域的傳送著陸點（虛線圓圈）以及出口通道（菱形）。座標為伺服器記錄的網格座標。"
    },
    "map_caption_local": {
        "cs": " Čárkované čáry spojují dvojice místních (vnitrozónových) teleportačních sloupů.",
        "de": " Die gestrichelten Linien verbinden lokale (zoneninterne) Teleportsäulenpaare.",
        "es": " Las líneas discontinuas conectan los pares de columnas de teletransporte locales (dentro de la zona).",
        "fr": " Les lignes en pointillés relient les paires de colonnes de téléportation locales (dans la zone).",
        "it": " Le linee tratteggiate collegano le coppie di colonne di teletrasporto locali (interne alla zona).",
        "ja": " 破線はゾーン内ローカルテレポート柱のペアを結んでいます。",
        "ko": " 점선은 로컬(존 내부) 텔레포트 기둥 쌍을 연결합니다.",
        "nl": " De stippellijnen verbinden de paren lokale (binnen de zone) teleportkolommen.",
        "pl": " Przerywane linie łączą pary lokalnych kolumn teleportacyjnych wewnątrz strefy.",
        "pt": " As linhas tracejadas conectam os pares de colunas de teletransporte locais (dentro da zona).",
        "ru": " Пунктирные линии соединяют пары локальных (внутризонных) телепортационных колонн.",
        "zh-CN": " 虚线连接本地（区域内）传送柱对。",
        "zh-TW": " 虛線連接本地（區域內）傳送柱對。"
    },
    "Teleport columns in": {
        "cs": "Teleportační sloupy v", "de": "Teleportsäulen in", "es": "Columnas de teletransporte en", "fr": "Colonnes de téléportation à",
        "it": "Colonne di teletrasporto in", "ja": "のテレポート柱", "ko": "의 텔레포트 기둥", "nl": "Teleportkolommen in",
        "pl": "Kolumny teleportacyjne w", "pt": "Colunas de teletransporte em", "ru": "Телепортационные колонны в", "zh-CN": "传送柱分布：", "zh-TW": "傳送柱分布："
    },

    # Facts Table Headers & Rows
    "Fact": {
        "cs": "Fakt", "de": "Tatsache", "es": "Dato", "fr": "Fait", "it": "Dato",
        "ja": "項目", "ko": "항목", "nl": "Feit", "pl": "Fakt", "pt": "Fato",
        "ru": "Факт", "zh-CN": "项目", "zh-TW": "項目"
    },
    "Value": {
        "cs": "Hodnota", "de": "Wert", "es": "Valor", "fr": "Valeur", "it": "Valore",
        "ja": "値", "ko": "값", "nl": "Waarde", "pl": "Wartość", "pt": "Valor",
        "ru": "Значение", "zh-CN": "数值", "zh-TW": "數值"
    },
    "Zone id": {
        "cs": "ID zóny", "de": "Zonen-ID", "es": "ID de zona", "fr": "ID de zone", "it": "ID zona",
        "ja": "ゾーンID", "ko": "존 ID", "nl": "Zone-ID", "pl": "ID strefy", "pt": "ID da zona",
        "ru": "ID зоны", "zh-CN": "区域ID", "zh-TW": "區域ID"
    },
    "Type": {
        "cs": "Typ", "de": "Typ", "es": "Tipo", "fr": "Type", "it": "Tipo",
        "ja": "タイプ", "ko": "유형", "nl": "Type", "pl": "Typ", "pt": "Tipo",
        "ru": "Тип", "zh-CN": "类型", "zh-TW": "類型"
    },
    "Protection": {
        "cs": "Ochrana", "de": "Schutz", "es": "Protección", "fr": "Protection", "it": "Protezione",
        "ja": "保護", "ko": "보호", "nl": "Bescherming", "pl": "Ochrona", "pt": "Proteção",
        "ru": "Защита", "zh-CN": "保护", "zh-TW": "保護"
    },
    "Size": {
        "cs": "Velikost", "de": "Größe", "es": "Tamaño", "fr": "Taille", "it": "Dimensioni",
        "ja": "サイズ", "ko": "크기", "nl": "Grootte", "pl": "Rozmiar", "pt": "Tamanho",
        "ru": "Размер", "zh-CN": "尺寸", "zh-TW": "尺寸"
    },
    "Tier": {
        "cs": "Tier", "de": "Tier", "es": "Nivel (Tier)", "fr": "Palier (Tier)", "it": "Livello (Tier)",
        "ja": "ティア", "ko": "티어", "nl": "Tier", "pl": "Poziom (Tier)", "pt": "Nível (Tier)",
        "ru": "Уровень (Tier)", "zh-CN": "阶级 (Tier)", "zh-TW": "階級 (Tier)"
    },
    "Fertility": {
        "cs": "Úrodnost", "de": "Fruchtbarkeit", "es": "Fertilidad", "fr": "Fertilité", "it": "Fertilità",
        "ja": "肥沃度", "ko": "비옥도", "nl": "Vruchtbaarheid", "pl": "Żyzność", "pt": "Fertilidade",
        "ru": "Плодородность", "zh-CN": "肥沃度", "zh-TW": "肥沃度"
    },
    "Plant species": {
        "cs": "Rostlinné druhy", "de": "Pflanzenarten", "es": "Especies vegetales", "fr": "Espèces végétales", "it": "Specie vegetali",
        "ja": "植物種", "ko": "식물 종", "nl": "Plantsoorten", "pl": "Gatunki roślin", "pt": "Espécies de plantas",
        "ru": "Виды растений", "zh-CN": "植物物种", "zh-TW": "植物物種"
    },
    "Ore types": {
        "cs": "Typy rud", "de": "Erzarten", "es": "Tipos de mineral", "fr": "Types de minerai", "it": "Tipi di minerale",
        "ja": "鉱石の種類", "ko": "광석 종류", "nl": "Erstypes", "pl": "Typy rud", "pt": "Tipos de minério",
        "ru": "Типы руды", "zh-CN": "矿石类型", "zh-TW": "礦石類型"
    },
    "Total ore nodes": {
        "cs": "Celkem ložisek rudy", "de": "Erzvorkommen insgesamt", "es": "Nodos de mineral totales", "fr": "Nœuds de minerai totaux", "it": "Nodi di minerale totali",
        "ja": "総鉱石ノード数", "ko": "총 광석 노드 수", "nl": "Totaal aantal ertsknopen", "pl": "Łącznie złoża rudy", "pt": "Total de nós de minério",
        "ru": "Всего рудных узлов", "zh-CN": "矿石节点总数", "zh-TW": "礦石節點總數"
    },
    "Round time limit": {
        "cs": "Časový limit kola", "de": "Rundenzeitlimit", "es": "Límite de tiempo de ronda", "fr": "Limite de temps de manche", "it": "Limite di tempo del round",
        "ja": "ラウンド制限時間", "ko": "라운드 제한 시간", "nl": "Rondetijdslimiet", "pl": "Limit czasu rundy", "pt": "Limite de tempo da rodada",
        "ru": "Лимит времени раунда", "zh-CN": "回合时间限制", "zh-TW": "回合時間限制"
    },
    "PBS tech limit": {
        "cs": "Technologický limit PBS", "de": "PBS-Technologielimit", "es": "Límite tecnológico de PBS", "fr": "Limite technologique PBS", "it": "Limite tecnologico PBS",
        "ja": "PBS技術制限", "ko": "PBS 테크 한도", "nl": "PBS-techlimiet", "pl": "Limit technologii PBS", "pt": "Limite tecnológico da PBS",
        "ru": "Технологический лимит PBS", "zh-CN": "PBS科技限制", "zh-TW": "PBS科技限制"
    },
    "Max docking bases": {
        "cs": "Max. dokovací základny", "de": "Max. Andockbasen", "es": "Bases de acoplamiento máx.", "fr": "Bases d'amarrage max.", "it": "Basi di attracco max.",
        "ja": "最大ドッキング基地数", "ko": "최대 도킹 기지", "nl": "Max. dockingbases", "pl": "Maks. bazy dokowania", "pt": "Bases de atracação máx.",
        "ru": "Макс. стыковочных баз", "zh-CN": "最大停靠基地数", "zh-TW": "最大停靠基地數"
    },

    # Protection descriptions in Facts table
    "prot_alpha_desc": {
        "cs": "chráněná, PvP zakázáno", "de": "geschützt, PvP deaktiviert", "es": "protegida, PvP deshabilitado", "fr": "protégée, JcJ désactivé",
        "it": "protetta, PvP disabilitato", "ja": "保護区、PvP無効", "ko": "보호 구역, PvP 비활성화", "nl": "beschermd, PvP uitgeschakeld",
        "pl": "chroniona, PvP wyłączone", "pt": "protegida, PvP desativado", "ru": "защищенная, PvP отключено", "zh-CN": "受保护，禁用PvP", "zh-TW": "受保護，禁用PvP"
    },
    "prot_beta_desc": {
        "cs": "otevřené PvP, standardní terén", "de": "offenes PvP, Standardgelände", "es": "PvP abierto, terreno estándar", "fr": "JcJ ouvert, terrain standard",
        "it": "PvP aperto, terreno standard", "ja": "オープンPvP、標準地形", "ko": "오픈 PvP, 표준 지형", "nl": "open PvP, standaard terrein",
        "pl": "otwarte PvP, standardowy teren", "pt": "PvP aberto, terreno padrão", "ru": "открытое PvP, стандартная местность", "zh-CN": "开放PvP，标准地形", "zh-TW": "開放PvP，標準地形"
    },
    "prot_gamma_desc": {
        "cs": "otevřené PvP, teraformovatelná", "de": "offenes PvP, terraformbar", "es": "PvP abierto, terraformable", "fr": "JcJ ouvert, terraformable",
        "it": "PvP aperto, terraformabile", "ja": "オープンPvP、テラフォーミング可能", "ko": "오픈 PvP, 테라포밍 가능", "nl": "open PvP, terraformbaar",
        "pl": "otwarte PvP, zdatna do terraformowania", "pt": "PvP aberto, terraformável", "ru": "открытое PvP, терраформируемая", "zh-CN": "开放PvP，可地形改造", "zh-TW": "開放PvP，可地形改造"
    },

    # Fact Table Values
    "tiles": {
        "cs": "dlaždic", "de": "Kacheln", "es": "casillas", "fr": "cases", "it": "caselle",
        "ja": "タイル", "ko": "타일", "nl": "tegels", "pl": "pól", "pt": "blocos",
        "ru": "клеток", "zh-CN": "格", "zh-TW": "格"
    },
    "(server-recorded)": {
        "cs": "(zaznamenáno serverem)", "de": "(vom Server erfasst)", "es": "(registrado en el servidor)", "fr": "(enregistré par le serveur)",
        "it": "(registrato dal server)", "ja": "(サーバー記録)", "ko": "(서버 기록)", "nl": "(geregistreerd door server)",
        "pl": "(zarejestrowane przez serwer)", "pt": "(registrado no servidor)", "ru": "(по данным сервера)", "zh-CN": "(服务器记录)", "zh-TW": "(伺服器記錄)"
    },
    "rule set": {
        "cs": "pravidla", "de": "Regelsatz", "es": "conjunto de reglas", "fr": "ensemble de règles", "it": "set di regole",
        "ja": "ルールセット", "ko": "규칙 세트", "nl": "regelset", "pl": "zestaw reguł", "pt": "conjunto de regras",
        "ru": "набор правил", "zh-CN": "规则集", "zh-TW": "規則集"
    },
    "– (no ruleset)": {
        "cs": "– (žádná pravidla)", "de": "– (kein Regelsatz)", "es": "– (sin reglas)", "fr": "– (aucun ensemble de règles)", "it": "– (nessun set di regole)",
        "ja": "– (ルールセットなし)", "ko": "– (규칙 세트 없음)", "nl": "– (geen regelset)", "pl": "– (brak reguł)", "pt": "– (sem conjunto de regras)",
        "ru": "– (нет набора правил)", "zh-CN": "– (无规则集)", "zh-TW": "– (無規則集)"
    },
    "none": {
        "cs": "žádné", "de": "keine", "es": "ninguna", "fr": "aucune", "it": "nessuna",
        "ja": "なし", "ko": "없음", "nl": "geen", "pl": "brak", "pt": "nenhuma",
        "ru": "нет", "zh-CN": "无", "zh-TW": "無"
    },

    # Ore configuration table
    "ore_config_p": {
        "cs": "Generování uzlů, které tato zóna udržuje. Výtěžnost jednotlivých rud a vzorce generování najdete v sekci [Rudy]({ores_link}) (sekce této zóny je odkazována níže).",
        "de": "Die Knotengenerierung, die diese Zone aufrechterhält. Erträge pro Erz und die Generierungsformeln finden Sie unter [Erze]({ores_link}) (der Abschnitt dieser Zone ist unten verlinkt).",
        "es": "La generación de nodos que mantiene esta zona. El rendimiento por mineral y las fórmulas de generación se encuentran en [Minerales]({ores_link}) (la sección de esta zona está enlazada abajo).",
        "fr": "La génération de nœuds maintenue par cette zone. Le rendement par minerai et les formules de génération se trouvent dans [Minerais]({ores_link}) (la section de cette zone est liée ci-dessous).",
        "it": "La generazione dei nodi mantenuta da questa zona. Le rese per minerale e le formule di generazione si trovano in [Minerali]({ores_link}) (la sezione di questa zona è collegata sotto).",
        "ja": "このゾーンが維持するノード生成。鉱石ごとの産出量と生成式は[鉱石]({ores_link})にあります（このゾーンのセクションは下記にリンク）。",
        "ko": "이 존이 유지하는 노드 생성입니다. 광석별 산출량 및 생성 공식은 [광석]({ores_link})에서 확인할 수 있습니다(이 존의 섹션은 아래에 링크됨).",
        "nl": "De knoopgeneratie die deze zone handhaaft. Opbrengsten per erts en de generatieformules zijn te vinden in [Ertsen]({ores_link}) (de sectie van deze zone is hieronder gelinkt).",
        "pl": "Generowanie złóż utrzymywane przez tę strefę. Wydajność poszczególnych rud i wzory generowania znajdują się w sekcji [Rudy]({ores_link}) (sekcja tej strefy jest podlinkowana poniżej).",
        "pt": "A geração de nós que esta zona mantém. Os rendimentos por minério e as fórmulas de geração estão em [Minérios]({ores_link}) (a seção desta zona está linkada abaixo).",
        "ru": "Генерация узлов, поддерживаемая этой зоной. Выход ресурсов и формулы генерации описаны в разделе [Руды]({ores_link}) (раздел этой зоны указан ниже).",
        "zh-CN": "该区域维持的矿石节点生成。每种矿石的产出和生成公式请参阅[矿石]({ores_link})（该区域的对应部分见下方链接）。",
        "zh-TW": "該區域維持的礦石節點生成。每種礦石的產出和生成公式請參閱[礦石]({ores_link})（該區域的對應部分見下方鏈接）。"
    },
    "Material": {
        "cs": "Materiál", "de": "Material", "es": "Material", "fr": "Matériau", "it": "Materiale",
        "ja": "素材", "ko": "재료", "nl": "Materiaal", "pl": "Materiał", "pt": "Material",
        "ru": "Материал", "zh-CN": "材料", "zh-TW": "材料"
    },
    "Nodes": {
        "cs": "Uzly", "de": "Knoten", "es": "Nodos", "fr": "Nœuds", "it": "Nodi",
        "ja": "ノード", "ko": "노드", "nl": "Knopen", "pl": "Złoża", "pt": "Nós",
        "ru": "Узлы", "zh-CN": "节点", "zh-TW": "節點"
    },
    "Max tiles/node": {
        "cs": "Max. dlaždic/uzel", "de": "Max. Kacheln/Knoten", "es": "Casillas máx./nodo", "fr": "Cases max./nœud", "it": "Caselle max./nodo",
        "ja": "最大タイル/ノード", "ko": "최대 타일/노드", "nl": "Max. tegels/knoop", "pl": "Maks. pól/złoże", "pt": "Blocos máx./nó",
        "ru": "Макс. клеток/узел", "zh-CN": "最大格数/节点", "zh-TW": "最大格數/節點"
    },
    "Total per node": {
        "cs": "Celkem na uzel", "de": "Gesamt pro Knoten", "es": "Total por nodo", "fr": "Total par nœud", "it": "Totale per nodo",
        "ja": "ノードあたり合計", "ko": "노드당 총량", "nl": "Totaal per knoop", "pl": "Łącznie na złoże", "pt": "Total por nó",
        "ru": "Всего на узел", "zh-CN": "单节点总量", "zh-TW": "單節點總量"
    },
    "Min threshold": {
        "cs": "Min. práh", "de": "Min. Schwellenwert", "es": "Umbral mín.", "fr": "Seuil min.", "it": "Soglia min.",
        "ja": "最小しきい値", "ko": "최소 임계값", "nl": "Min. drempel", "pl": "Min. próg", "pt": "Limiar mín.",
        "ru": "Мин. порог", "zh-CN": "最小阈值", "zh-TW": "最小閾值"
    },
    "pie_title": {
        "cs": "Zásoby rudy v ustáleném stavu podle typu (miliony jednotek)",
        "de": "Erzbestand im stabilen Zustand nach Typ (Millionen Einheiten)",
        "es": "Reservas de mineral en estado estacionario por tipo (millones de unidades)",
        "fr": "Stock de minerai à l'état stable par type (millions d'unités)",
        "it": "Scorte di minerali a regime per tipo (milioni di unità)",
        "ja": "鉱石の種類別定常在庫（百万単位）",
        "ko": "유형별 정상 상태 광석 비축량 (백만 단위)",
        "nl": "Voorraad erts in stabiele toestand per type (miljoen eenheden)",
        "pl": "Zapas rudy w stanie ustalonym wg typu (miliony jednostek)",
        "pt": "Estoque de minério em estado estacionário por tipo (milhões de unidades)",
        "ru": "Запасы руды в установившемся режиме по типам (млн единиц)",
        "zh-CN": "稳态各类矿石储量（百万单位）",
        "zh-TW": "穩態各類礦石儲量（百萬單位）"
    },

    # Description parts
    "ore types": {
        "cs": "typů rudy", "de": "Erzarten", "es": "tipos de mineral", "fr": "types de minerai", "it": "tipi di minerale",
        "ja": "種類の鉱石", "ko": "종류의 광석", "nl": "erstypes", "pl": "typów rudy", "pt": "tipos de minério",
        "ru": "типов руды", "zh-CN": "种矿石", "zh-TW": "種礦石"
    },
    "plant species": {
        "cs": "druhů rostlin", "de": "Pflanzenarten", "es": "especies vegetales", "fr": "espèces végétales", "it": "specie vegetali",
        "ja": "種の植物", "ko": "종의 식물", "nl": "plantsoorten", "pl": "gatunków roślin", "pt": "espécies de plantas",
        "ru": "видов растений", "zh-CN": "种植物", "zh-TW": "種植物"
    },
    "no plant rules": {
        "cs": "bez vegetace", "de": "keine Pflanzenregeln", "es": "sin reglas de plantas", "fr": "aucune règle de végétation", "it": "nessuna regola di vegetazione",
        "ja": "植物ルールなし", "ko": "식물 규칙 없음", "nl": "geen plantregels", "pl": "brak reguł roślin", "pt": "sem regras de plantas",
        "ru": "без правил растений", "zh-CN": "无植物规则", "zh-TW": "無植物規則"
    },
    "zone": {
        "cs": "zóna", "de": "Zone", "es": "zona", "fr": "zone", "it": "zona",
        "ja": "ゾーン", "ko": "존", "nl": "zone", "pl": "strefa", "pt": "zona",
        "ru": "зона", "zh-CN": "区域", "zh-TW": "區域"
    },
    "protected": {
        "cs": "chráněná", "de": "geschützte", "es": "protegida", "fr": "protégée", "it": "protetta",
        "ja": "保護区", "ko": "보호", "nl": "beschermde", "pl": "chroniona", "pt": "protegida",
        "ru": "защищенная", "zh-CN": "受保护", "zh-TW": "受保護"
    },
    "open": {
        "cs": "otevřená", "de": "offene", "es": "abierta", "fr": "ouverte", "it": "aperta",
        "ja": "オープン", "ko": "오픈", "nl": "open", "pl": "otwarta", "pt": "aberta",
        "ru": "открытая", "zh-CN": "开放", "zh-TW": "開放"
    },
    "open-terraformable": {
        "cs": "otevřená-teraformovatelná", "de": "offene-terraformbare", "es": "abierta y terraformable", "fr": "ouverte et terraformable", "it": "aperta e terraformabile",
        "ja": "テラフォーミング可能なオープン", "ko": "오픈 테라포밍 가능", "nl": "open-terraformbare", "pl": "otwarta i zdatna do terraformowania", "pt": "aberta e terraformável",
        "ru": "открытая терраформируемая", "zh-CN": "开放且可地形改造", "zh-TW": "開放且可地形改造"
    }
}

# Family / Galaxy localized strings
FAMILIES = {
    "frontier belt": {
        "cs": "pohraničního pásu", "de": "des Grenzgürtels", "es": "del cinturón fronterizo", "fr": "de la ceinture frontière",
        "it": "della cintura di frontiera", "ja": "フロンティアベルト", "ko": "프론티어 벨트", "nl": "van de grensstrook",
        "pl": "pasa granicznego", "pt": "do cinturão de fronteira", "ru": "пограничного пояса", "zh-CN": "边境地带", "zh-TW": "邊境地帶"
    },
    "New Virginia (TM)": {
        "cs": "New Virginia (TM)", "de": "New Virginia (TM)", "es": "New Virginia (TM)", "fr": "New Virginia (TM)",
        "it": "New Virginia (TM)", "ja": "New Virginia (TM)", "ko": "New Virginia (TM)", "nl": "New Virginia (TM)",
        "pl": "New Virginia (TM)", "pt": "New Virginia (TM)", "ru": "New Virginia (TM)", "zh-CN": "New Virginia (TM)", "zh-TW": "New Virginia (TM)"
    },
    "Attalica (ICS)": {
        "cs": "Attalica (ICS)", "de": "Attalica (ICS)", "es": "Attalica (ICS)", "fr": "Attalica (ICS)",
        "it": "Attalica (ICS)", "ja": "Attalica (ICS)", "ko": "Attalica (ICS)", "nl": "Attalica (ICS)",
        "pl": "Attalica (ICS)", "pt": "Attalica (ICS)", "ru": "Attalica (ICS)", "zh-CN": "Attalica (ICS)", "zh-TW": "Attalica (ICS)"
    },
    "Daoden (ASI)": {
        "cs": "Daoden (ASI)", "de": "Daoden (ASI)", "es": "Daoden (ASI)", "fr": "Daoden (ASI)",
        "it": "Daoden (ASI)", "ja": "Daoden (ASI)", "ko": "Daoden (ASI)", "nl": "Daoden (ASI)",
        "pl": "Daoden (ASI)", "pt": "Daoden (ASI)", "ru": "Daoden (ASI)", "zh-CN": "Daoden (ASI)", "zh-TW": "Daoden (ASI)"
    }
}

# The 7 intro templates
def translate_intro(text, lang):
    # Match: "A protected (Alpha) {fam} zone — safe from player attack, the standard gathering ground for the {fam} galaxy."
    m = re.search(r'A protected \(Alpha\) (.*?) zone — safe from player attack, the standard gathering ground for the \1 galaxy\.', text)
    if m:
        fam = m.group(1)
        intros = {
            "cs": f"Chráněná zóna (Alpha) oblasti {fam} — bezpečná před útoky hráčů, standardní těžební oblast galaxie {fam}.",
            "de": f"Eine geschützte (Alpha) {fam}-Zone — sicher vor Spielerangriffen, das reguläre Sammelgebiet der {fam}-Galaxie.",
            "es": f"Una zona protegida (Alpha) de {fam} — a salvo de ataques de jugadores, el terreno habitual de recolección para la galaxia {fam}.",
            "fr": f"Une zone protégée (Alpha) de {fam} — à l'abri des attaques des joueurs, zone de collecte standard pour la galaxie {fam}.",
            "it": f"Una zona protetta (Alpha) di {fam} — al sicuro dagli attacchi dei giocatori, la normale area di raccolta per la galassia {fam}.",
            "ja": f"{fam}の保護（Alpha）ゾーン — プレイヤーの攻撃から安全で、{fam}銀河の標準的な採集地です。",
            "ko": f"{fam}의 보호(Alpha) 존 — 플레이어의 공격으로부터 안전하며 {fam} 은하의 기본 자원 채집지입니다.",
            "nl": f"Een beschermde (Alpha) {fam}-zone — veilig voor aanvallen van spelers, het standaard verzamelgebied voor het {fam}-stelsel.",
            "pl": f"Chroniona strefa (Alpha) obszaru {fam} — bezpieczna przed atakami graczy, standardowy teren zbieractwa dla galaktyki {fam}.",
            "pt": f"Uma zona protegida (Alpha) de {fam} — a salvo de ataques de jogadores, a área de coleta padrão para a galáxia {fam}.",
            "ru": f"Защищенная зона (Alpha) региона {fam} — безопасна от атак игроков, стандартная область сбора ресурсов галактики {fam}.",
            "zh-CN": f"{fam}的受保护（Alpha）区域 — 免受玩家攻击，是{fam}星系的标准资源采集地。",
            "zh-TW": f"{fam}的受保護（Alpha）區域 — 免受玩家攻擊，是{fam}星系的標準資源採集地。"
        }
        res = intros.get(lang, intros["en"] if "en" in intros else text)
        return append_maintains(res, text, lang)

    # Match: "An open-PvP (beta) {fam} island — players can attack freely and blobs apply."
    m = re.search(r'An open-PvP \(beta\) (.*?) island — players can attack freely and blobs apply\.', text)
    if m:
        fam = m.group(1)
        intros = {
            "cs": f"Otevřený PvP (beta) ostrov oblasti {fam} — hráči mohou volně útočit a platí bloby.",
            "de": f"Eine offene PvP-(Beta-)Insel von {fam} — Spieler können frei angreifen und Blobs greifen.",
            "es": f"Una isla de PvP abierto (beta) de {fam} — los jugadores pueden atacar libremente y se aplican blobs.",
            "fr": f"Une île JcJ ouverte (bêta) de {fam} — les joueurs peuvent s'attaquer librement et les effets de blob s'appliquent.",
            "it": f"Un'isola PvP aperta (beta) di {fam} — i giocatori possono attaccare liberamente e si applicano i blob.",
            "ja": f"{fam}のオープンPvP（Beta）島 — プレイヤーは自由に攻撃でき、ブロブが適用されます。",
            "ko": f"{fam}의 오픈 PvP(Beta) 섬 — 플레이어가 자유롭게 공격할 수 있으며 블롭이 적용됩니다.",
            "nl": f"Een open-PvP (beta) {fam}-eiland — spelers kunnen vrij aanvallen en blobs zijn van toepassing.",
            "pl": f"Wyspa otwartego PvP (beta) obszaru {fam} — gracze mogą atakować bez ograniczeń, obowiązują bloby.",
            "pt": f"Uma ilha de PvP aberto (beta) de {fam} — jogadores podem atacar livremente e bloqueios se aplicam.",
            "ru": f"Остров с открытым PvP (бета) региона {fam} — игроки могут свободно атаковать, действуют блобы.",
            "zh-CN": f"{fam}的开放PvP（Beta）岛屿 — 玩家可自由攻击且适用群体干扰（blob）。",
            "zh-TW": f"{fam}的開放PvP（Beta）島嶼 — 玩家可自由攻擊且適用群體干擾（blob）。"
        }
        res = intros.get(lang, text)
        return append_maintains(res, text, lang)

    # Match: "An open-PvP, terraformable (gamma) {fam} island — the ground can be reshaped by players."
    m = re.search(r'An open-PvP, terraformable \(gamma\) (.*?) island — the ground can be reshaped by players\.', text)
    if m:
        fam = m.group(1)
        intros = {
            "cs": f"Otevřený PvP, teraformovatelný (gamma) ostrov oblasti {fam} — terén mohou hráči přetvářet.",
            "de": f"Eine offene, terraformbare PvP-(Gamma-)Insel von {fam} — das Gelände kann von Spielern umgeformt werden.",
            "es": f"Una isla de PvP abierto y terraformable (gamma) de {fam} — el terreno puede ser modificado por los jugadores.",
            "fr": f"Une île JcJ ouverte et terraformable (gamma) de {fam} — le sol peut être remodelé par les joueurs.",
            "it": f"Un'isola PvP aperta e terraformabile (gamma) di {fam} — il terreno può essere rimodellato dai giocatori.",
            "ja": f"{fam}のオープンPvP・テラフォーミング可能（Gamma）島 — プレイヤーが地面を造成できます。",
            "ko": f"{fam}의 오픈 PvP, 테라포밍 가능(Gamma) 섬 — 플레이어가 지형을 변경할 수 있습니다.",
            "nl": f"Een open-PvP, terraformbaar (gamma) {fam}-eiland — het terrein kan door spelers worden aangepast.",
            "pl": f"Otwarta, zdatna do terraformowania wyspa PvP (gamma) obszaru {fam} — teren może być przekształcany przez graczy.",
            "pt": f"Uma ilha de PvP aberto e terraformável (gamma) de {fam} — o terreno pode ser remodelado pelos jogadores.",
            "ru": f"Терраформируемый остров с открытым PvP (гамма) региона {fam} — игроки могут изменять ландшафт.",
            "zh-CN": f"{fam}的开放PvP且可地形改造（Gamma）岛屿 — 地形可由玩家重塑。",
            "zh-TW": f"{fam}的開放PvP且可地形改造（Gamma）島嶼 — 地形可由玩家重塑。"
        }
        res = intros.get(lang, text)
        return append_maintains(res, text, lang)

    # Match: "A small transit zone of the frontier belt — a pure travel node with no ore configuration."
    if "small transit zone of the frontier belt" in text:
        intros = {
            "cs": "Malá tranzitní zóna pohraničního pásu — čistě cestovní uzel bez konfigurace rudy.",
            "de": "Eine kleine Transitzone des Grenzgürtels — ein reiner Reisetrip-Knotenpunkt ohne Erzkonfiguration.",
            "es": "Una pequeña zona de tránsito del cinturón fronterizo: un nodo exclusivo de viaje sin configuración de mineral.",
            "fr": "Une petite zone de transit de la ceinture frontière — un pur nœud de voyage sans configuration de minerai.",
            "it": "Una piccola zona di transito della cintura di frontiera — un puro nodo di viaggio privo di configurazione minerale.",
            "ja": "フロンティアベルトの小さな通過ゾーン — 鉱石構成のない純粋な移動ノードです。",
            "ko": "프론티어 벨트의 소형 이동 존 — 광석 구성이 없는 순수한 이동 노드입니다.",
            "nl": "Een kleine transitzone van de grensstrook — een puur reisknooppunt zonder ertsconfiguratie.",
            "pl": "Niewielka strefa tranzytowa pasa granicznego — czysty węzeł podróżny bez konfiguracji złóż rudy.",
            "pt": "Uma pequena zona de trânsito do cinturão de fronteira — um nó exclusivo de viagem sem configuração de minério.",
            "ru": "Небольшая транзитная зона пограничного пояса — чистый узел перемещения без рудных залежей.",
            "zh-CN": "边境地带的小型过境区域 — 纯粹的通行节点，无矿石配置。",
            "zh-TW": "邊境地帶的小型過境區域 — 純粹的通行節點，無礦石配置。"
        }
        return intros.get(lang, text)

    # Match: "The virtual training island — where new characters start and learn the basics."
    if "virtual training island" in text:
        intros = {
            "cs": "Virtuální výcvikový ostrov — kde nové postavy začínají a učí se základy.",
            "de": "Die virtuelle Trainingsinsel — wo neue Charaktere starten und die Grundlagen erlernen.",
            "es": "La isla virtual de entrenamiento: donde los nuevos personajes comienzan y aprenden lo básico.",
            "fr": "L'île d'entraînement virtuelle — où les nouveaux personnages commencent et apprennent les bases.",
            "it": "L'isola virtuale di addestramento — dove i nuovi personaggi iniziano e apprendono le basi.",
            "ja": "仮想トレーニング島 — 新規キャラクターが開始し、基本を学ぶ場所です。",
            "ko": "가상 훈련 섬 — 신규 캐릭터가 시작하여 기본기를 익히는 장소입니다.",
            "nl": "Het virtuele trainingseiland — waar nieuwe personages beginnen en de basis leren.",
            "pl": "Wirtualna wyspa treningowa — gdzie nowe postacie rozpoczynają grę i uczą się podstaw.",
            "pt": "A ilha virtual de treinamento — onde novos personagens começam e aprendem o básico.",
            "ru": "Виртуальный тренировочный остров — где новые персонажи начинают путь и осваивают основы игры.",
            "zh-CN": "虚拟训练岛 — 新角色启程并学习基础知识的场所。",
            "zh-TW": "虛擬訓練島 — 新角色啟程並學習基礎知識的場所。"
        }
        return intros.get(lang, text)

    # Match: "The PvP arena — a scripted combat event zone."
    if "The PvP arena" in text:
        intros = {
            "cs": "PvP aréna — skriptovaná zóna bojových událostí.",
            "de": "Die PvP-Arena — eine geskriptete Kampf-Event-Zone.",
            "es": "La arena PvP: una zona de eventos de combate con guión.",
            "fr": "L'arène JcJ — une zone d'événement de combat scénarisé.",
            "it": "L'arena PvP — una zona per eventi di combattimento scriptati.",
            "ja": "PvPアリーナ — スクリプト化された戦闘イベントゾーンです。",
            "ko": "PvP 아레나 — 스크립트 기반 전투 이벤트 존입니다.",
            "nl": "De PvP-arena — een gescripte gevechtsevenementenzone.",
            "pl": "Arena PvP — oskryptowana strefa wydarzeń bojowych.",
            "pt": "A arena PvP — uma zona de evento de combate roteirizado.",
            "ru": "PvP-арена — зона скриптовых боевых событий.",
            "zh-CN": "PvP竞技场 — 脚本化战斗事件区域。",
            "zh-TW": "PvP競技場 — 腳本化戰鬥事件區域。"
        }
        return intros.get(lang, text)

    # Match: "A stronghold — a protected instance zone with its own exit gate."
    if "A stronghold" in text:
        intros = {
            "cs": "Pevnost — chráněná instanční zóna s vlastní výstupní bránou.",
            "de": "Eine Festung — eine geschützte Instanzzone mit eigenem Ausgangstor.",
            "es": "Una fortaleza: una zona de instancia protegida con su propia puerta de salida.",
            "fr": "Un bastion — une zone d'instance protégée avec sa propre porte de sortie.",
            "it": "Una roccaforte — una zona di istanza protetta con un proprio varco di uscita.",
            "ja": "ストロングホールド — 専用の出口ゲートを備えた保護されたインスタンスゾーンです。",
            "ko": "요새 — 고유한 출구 게이트가 있는 보호된 인스턴스 존입니다.",
            "nl": "Een bolwerk — een beschermde instantiezone met een eigen uitgangspoort.",
            "pl": "Twierdza — chroniona strefa instancyjna z własną bramą wyjściową.",
            "pt": "Uma fortaleza — uma zona de instância protegida com seu próprio portão de saída.",
            "ru": "Цитадель — защищенная инстанс-зона с собственными выходными вратами.",
            "zh-CN": "要塞 — 具有专属出口通道的受保护副本区域。",
            "zh-TW": "要塞 — 具有專屬出口通道的受保護副本區域。"
        }
        return intros.get(lang, text)

    return text

def append_maintains(translated_base, original_full, lang):
    m = re.search(r'It maintains (\d+) ore types?\.', original_full)
    if not m:
        return translated_base
    n = m.group(1)
    tails = {
        "cs": f" Udržuje {n} druhů rudy.",
        "de": f" Sie verwaltet {n} Erzarten.",
        "es": f" Mantiene {n} tipos de mineral.",
        "fr": f" Elle maintient {n} types de minerai.",
        "it": f" Mantiene {n} tipi di minerale.",
        "ja": f" {n}種類の鉱石を維持しています。",
        "ko": f" {n}가지 광석 유형을 유지합니다.",
        "nl": f" Het onderhoudt {n} erstypes.",
        "pl": f" Utrzymuje {n} typów rudy.",
        "pt": f" Ela mantém {n} tipos de minério.",
        "ru": f" Здесь поддерживается {n} типов руды.",
        "zh-CN": f" 维持{n}种矿石类型。",
        "zh-TW": f" 維持{n}種礦石類型。"
    }
    return translated_base + tails.get(lang, f" It maintains {n} ore types.")

def tr(key, lang):
    return I18N.get(key, {}).get(lang, key)

def rewrite_zone_links(text, lang):
    """Rewrite /zones/ and /content/ links to /{lang}/ while keeping /content/items/ and assets untouched."""
    # /zones/...
    def repl_zones(m):
        path = m.group(1)
        # Don't prefix if already prefixed
        if path.startswith(f"/{lang}/"):
            return m.group(0)
        return f"({path[:1]}{lang}{path[1:]})"

    # Match markdown link targets: (/zones/...) -> (/{lang}/zones/...)
    text = re.sub(r'\((/zones/[^)]*)\)', rf'(/{lang}\1)', text)
    # Match href="/zones/...": href="/{lang}/zones/..."
    text = re.sub(r'href="(/zones/[^"]*)"', rf'href="/{lang}\1"', text)

    # Match /content/ores/... links
    text = re.sub(r'\((/content/ores/[^)]*)\)', rf'(/{lang}\1)', text)
    text = re.sub(r'href="(/content/ores/[^"]*)"', rf'href="/{lang}\1"', text)

    return text

def process_generated_zone_page(content, lang):
    c = rewrite_zone_links(content, lang)

    # 1. Frontmatter description
    # e.g.: description: "PvP open-terraformable zone: 7 ore types, 17 plant species, 2048×2048 tiles."
    # e.g.: description: "PvE protected zone: 5 ore types, 19 plant species, 2048×2048 tiles."
    # e.g.: description: "PvP open zone: no plant rules, 256×256 tiles."
    desc_m = re.search(r'description:\s*"([^"]+)"', c)
    if desc_m:
        orig_desc = desc_m.group(1)
        type_word = "PvP" if "PvP" in orig_desc else ("PvE" if "PvE" in orig_desc else ("Training" if "Training" in orig_desc else ""))
        prot_word = "protected" if "protected" in orig_desc else ("open-terraformable" if "open-terraformable" in orig_desc else ("open" if "open" in orig_desc else ""))
        ore_m = re.search(r'(\d+)\s+ore types?', orig_desc)
        ore_cnt = f"{ore_m.group(1)} {tr('ore types', lang)}, " if ore_m else ""
        plant_m = re.search(r'(\d+)\s+plant species', orig_desc)
        plant_cnt = f"{plant_m.group(1)} {tr('plant species', lang)}" if plant_m else ("no plant rules" if "no plant rules" in orig_desc else "")
        if plant_cnt == "no plant rules":
            plant_cnt = tr("no plant rules", lang)
        size_m = re.search(r'(\d+[×x]\d+)\s+tiles', orig_desc)
        size_part = f", {size_m.group(1)} {tr('tiles', lang)}." if size_m else "."
        
        # Localized description
        if lang in ["zh-CN", "zh-TW"]:
            new_desc = f"{type_word} {tr(prot_word, lang)}{tr('zone', lang)}：{ore_cnt}{plant_cnt}{size_part}"
        elif lang in ["ja", "ko"]:
            new_desc = f"{type_word} {tr(prot_word, lang)} {tr('zone', lang)}: {ore_cnt}{plant_cnt}{size_part}"
        else:
            new_desc = f"{tr('zone', lang).capitalize()} {type_word} {tr(prot_word, lang)}: {ore_cnt}{plant_cnt}{size_part}"
        c = c.replace(f'description: "{orig_desc}"', f'description: "{new_desc}"')

    # 2. Worldmap card
    c = c.replace("<strong>World map</strong> — where this zone sits among all the others, with the teleport connections. Open the full map.",
                  f"<strong>{tr('World map', lang)}</strong> — {tr('worldmap_card_desc', lang)}")

    # 3. Teleport image alt
    tele_prefix = tr("Teleport columns in", lang)
    if lang in ["ja", "ko"]:
        c = re.sub(r'!\[Teleport columns in ([^\]]+)\]', rf'![\1{tele_prefix}]', c)
    else:
        c = re.sub(r'!\[Teleport columns in ([^\]]+)\]', rf'![{tele_prefix} \1]', c)

    # 4. Map caption
    has_local = "The dashed lines connect the pairs of local" in c
    caption_txt = tr("map_caption_main", lang) + (tr("map_caption_local", lang) if has_local else "")
    c = re.sub(r'Where this zone\'s teleport columns stand \(dots.*?\.\n', caption_txt + "\n", c, flags=re.DOTALL)

    # 5. Intro paragraph
    # Match paragraph between caption and facts table:
    intro_m = re.search(r'(\n\n)([^\n|#]+)(\n\n\|\s*Fact)', c)
    if intro_m:
        orig_intro = intro_m.group(2).strip()
        trans_intro = translate_intro(orig_intro, lang)
        c = c.replace(orig_intro, trans_intro)

    # 6. Facts table headers & row keys
    c = c.replace("| Fact | Value |", f"| {tr('Fact', lang)} | {tr('Value', lang)} |")
    for fact_key in [
        "Zone id", "Type", "Protection", "Size", "Tier", "Fertility",
        "Plant species", "Ore types", "Total ore nodes", "Round time limit",
        "PBS tech limit", "Max docking bases"
    ]:
        c = re.sub(rf'^\|\s*{re.escape(fact_key)}\s*\|', f"| {tr(fact_key, lang)} |", c, flags=re.MULTILINE)

    # Facts table values
    c = c.replace("— protected, PvP disabled", f"— {tr('prot_alpha_desc', lang)}")
    c = c.replace("— open PvP, standard terrain", f"— {tr('prot_beta_desc', lang)}")
    c = c.replace("— open PvP, terraformable", f"— {tr('prot_gamma_desc', lang)}")
    c = re.sub(r'(\d+[×x]\d+)\s+tiles', rf'\1 {tr("tiles", lang)}', c)
    c = c.replace("(server-recorded)", tr("(server-recorded)", lang))
    c = re.sub(r'\(rule set (\d+)\)', rf'({tr("rule set", lang)} \1)', c)
    c = c.replace("– (no ruleset)", tr("– (no ruleset)", lang))
    c = re.sub(r'\|\s*none\s*\|', f"| {tr('none', lang)} |", c)

    # 7. Ore configuration section
    c = c.replace("## Ore configuration", f"## {tr('Ore configuration', lang)}")
    ores_link = f"/{lang}/content/ores/"
    ore_desc = tr("ore_config_p", lang).format(ores_link=ores_link)
    c = re.sub(r'The node generation this zone maintains\..*?\n\n', ore_desc + "\n\n", c)

    # Table headers
    c = c.replace("| Material | Nodes | Max tiles/node | Total per node | Min threshold |",
                  f"| {tr('Material', lang)} | {tr('Nodes', lang)} | {tr('Max tiles/node', lang)} | {tr('Total per node', lang)} | {tr('Min threshold', lang)} |")

    # Pie chart title
    c = c.replace("title Steady-state ore stock by type (million units)",
                  f"title {tr('pie_title', lang)}")

    # 8. Bottom links
    # [Zone index](/zones/zone-index/) · [World map](/zones/map/#...) · [Protection levels](/zones/protection/)
    zone_idx_tr = tr("Zone index", lang)
    world_map_tr = tr("World map", lang)
    prot_levels_tr = tr("Protection levels", lang)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{zone_idx_tr}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/([^)]*)\)', rf'[{world_map_tr}](/{lang}/zones/map/\1)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{prot_levels_tr}](/{lang}/zones/protection/)', c)

    return c

ALPHA_DESC = {
    "cs": "Každá zóna alpha — chráněné hlavní ostrovy a jejich společníci PvE, každý s vlastní stránkou.",
    "de": "Jede Alpha-Zone — die geschützten Hauptinseln und ihre PvE-Gefährten, jeweils mit eigener Seite.",
    "es": "Cada zona alpha: las islas principales protegidas y sus compañeras PvE, cada una con su propia página.",
    "fr": "Toutes les zones alpha — les îles principales protégées et leurs compagnes JcE, chacune avec sa propre page.",
    "it": "Tutte le zone alpha — le principali isole protette e le loro compagne PvE, ciascuna con la propria pagina.",
    "ja": "すべてのAlphaゾーン — 保護された主要な島とPvEコンパニオン島、それぞれ専用ページあり。",
    "ko": "모든 Alpha 존 — 보호된 주요 섬과 PvE 동반 섬, 각 섬별 고유 페이지 제공.",
    "nl": "Elke alpha-zone — de belangrijkste beschermde eilanden en hun PvE-metgezellen, elk met een eigen pagina.",
    "pl": "Każda strefa alpha — główne chronione wyspy i ich towarzysze PvE, każda z osobną stroną.",
    "pt": "Cada zona alpha — as principais ilhas protegidas e suas companheiras PvE, cada uma com sua própria página.",
    "ru": "Все зоны alpha — основные защищенные острова и их PvE-спутники, каждый со своей страницей.",
    "zh-CN": "所有Alpha区域 — 受保护的主岛及其PvE伴生岛，每个岛屿均有独立页面。",
    "zh-TW": "所有Alpha區域 — 受保護的主島及其PvE伴生島，每個島嶼均有獨立頁面。"
}

BETA_DESC = {
    "cs": "Každá zóna beta — ostrovy s otevřeným PvP, každý s vlastní stránkou.",
    "de": "Jede Beta-Zone — die offenen PvP-Inseln, jeweils mit eigener Seite.",
    "es": "Cada zona beta: las islas de PvP abierto, cada una con su propia página.",
    "fr": "Toutes les zones bêta — les îles JcJ ouvertes, chacune avec sa propre page.",
    "it": "Tutte le zone beta — le isole PvP aperte, ciascuna con la propria pagina.",
    "ja": "すべてのBetaゾーン — オープンPvPの島々、それぞれ専用ページあり。",
    "ko": "모든 Beta 존 — 오픈 PvP 섬, 각 섬별 고유 페이지 제공.",
    "nl": "Elke beta-zone — de open-PvP-eilanden, elk met een eigen pagina.",
    "pl": "Każda strefa beta — wyspy otwartego PvP, każda z osobną stroną.",
    "pt": "Cada zona beta — as ilhas de PvP aberto, cada uma com sua própria página.",
    "ru": "Все зоны beta — острова с открытым PvP, каждый со своей страницей.",
    "zh-CN": "所有Beta区域 — 开放PvP岛屿，每个岛屿均有独立页面。",
    "zh-TW": "所有Beta區域 — 開放PvP島嶼，每個島嶼均有獨立頁面。"
}

GAMMA_DESC = {
    "cs": "Každá zóna pohraničního pásu: tranzitní zóny tc a ostrovy úrovní T1–T4, každý s vlastní stránkou.",
    "de": "Jede Grenzgürtel-Zone: die tc-Transitzonen und die T1–T4-Stufeninseln, jeweils mit eigener Seite.",
    "es": "Cada zona del cinturón fronterizo: las zonas de tránsito tc y las islas de nivel T1–T4, cada una con su página.",
    "fr": "Toutes les zones de la ceinture frontière : zones de transit tc et îles des paliers T1–T4, chacune avec sa page.",
    "it": "Tutte le zone della cintura di frontiera: le zone di transito tc e le isole di livello T1–T4, ciascuna con la propria pagina.",
    "ja": "すべてのフロンティアベルトゾーン：tc通過ゾーンとT1–T4ティア島、それぞれ専用ページあり。",
    "ko": "모든 프론티어 벨트 존: tc 이동 존과 T1–T4 티어 섬, 각 섬별 고유 페이지 제공.",
    "nl": "Elke grensstrook-zone: de tc-transitzones en de T1–T4-niveau-eilanden, elk met een eigen pagina.",
    "pl": "Każda strefa pasa granicznego: strefy tranzytowe tc i wyspy poziomów T1–T4, każda z osobną stroną.",
    "pt": "Cada zona do cinturão de fronteira: as zonas de trânsito tc e as ilhas de nível T1–T4, cada uma com sua página.",
    "ru": "Все зоны пограничного пояса: транзитные зоны tc и уровневые острова T1–T4, каждый со своей страницей.",
    "zh-CN": "所有边境地带区域：tc过境区域与T1–T4阶梯岛屿，每个岛屿均有独立页面。",
    "zh-TW": "所有邊境地帶區域：tc過境區域與T1–T4階梯島嶼，每個島嶼均有獨立頁面。"
}

ZONE_INDEX_DESC = {
    "cs": "Každá zóna se spojením teleportu do jiné zóny, seskupená podle rodiny.",
    "de": "Jede Zone mit einer Teleportverbindung zu einer anderen Zone, gruppiert nach Familie.",
    "es": "Cada zona con conexión de teletransporte a otra zona, agrupada por familia.",
    "fr": "Toutes les zones disposant d'une liaison de téléportation vers une autre zone, regroupées par famille.",
    "it": "Tutte le zone con un collegamento di teletrasporto a un'altra zona, raggruppate per famiglia.",
    "ja": "別ゾーンへのテレポート接続を持つ全ゾーン、ファミリー別にグループ化。",
    "ko": "다른 존으로 연결되는 텔레포트가 있는 모든 존, 패밀리별 그룹화.",
    "nl": "Elke zone met een teleportverbinding naar een andere zone, gegroepeerd per familie.",
    "pl": "Każda strefa z połączeniem teleportacyjnym do innej strefy, pogrupowana według rodzin.",
    "pt": "Cada zona com conexão de teletransporte para outra zona, agrupada por família.",
    "ru": "Все зоны с телепортационной связью с другой зоной, сгруппированные по семействам.",
    "zh-CN": "具有通往其他区域传送连接的所有区域，按家族分组。",
    "zh-TW": "具有通往其他區域傳送連接的所有區域，按家族分組。"
}

MAP_DESC = {
    "cs": "Každá zóna zakreslená se skutečným terénem na své souřadnicové pozici, ohraničená podle galaxie, se spoji teleportů a bran z databáze.",
    "de": "Jede Zone gezeichnet mit ihrem realen Gelände an ihrer Rasterposition, umrissen nach Galaxie, mit den Teleport- und Torverbindungen aus der Datenbank.",
    "es": "Cada zona dibujada con su terreno real en su posición de cuadrícula, delimitada por galaxia, con las conexiones de teletransporte y puertas de la base de datos.",
    "fr": "Toutes les zones représentées avec leur relief réel à leur position sur la grille, délimitées par galaxie, avec les liaisons de téléportation et de portes de la base de données.",
    "it": "Ogni zona disegnata con il suo terreno reale nella sua posizione di griglia, delineata per galassia, con i collegamenti di teletrasporto e varchi dal database.",
    "ja": "グリッド位置に実際の地形で描かれた全ゾーン、銀河別に概説され、データベースのテレポートおよびゲート接続を含む。",
    "ko": "그리드 위치에 실제 지형으로 그려진 모든 존, 은하별 윤곽선 표시, 데이터베이스의 텔레포트 및 게이트 연결 포함.",
    "nl": "Elke zone getekend met zijn echte terrein op zijn rasterpositie, omlijnd per sterrenstelsel, met de teleport- en poortverbindingen uit de database.",
    "pl": "Każda strefa narysowana z rzeczywistym ukształtowaniem terenu na siatce, obrysowana według galaktyki, z połączeniami teleportów i bram z bazy danych.",
    "pt": "Cada zona desenhada com seu relevo real em sua posição na grade, delineada por galáxia, com as conexões de teletransporte e portões do banco de dados.",
    "ru": "Все зоны, отрисованные с реальным рельефом на координатной сетке, очерченные по галактикам, со связями телепортов и врат из базы данных.",
    "zh-CN": "每个区域均以实际地形绘制在其网格位置上，按星系轮廓划分，并包含数据库中的传送和通道连接。",
    "zh-TW": "每個區域均以實際地形繪製在其網格位置上，按星系輪廓劃分，並包含資料庫中的傳送和通道連接。"
}

def process_alpha_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    if lang in ALPHA_DESC:
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{ALPHA_DESC[lang]}"', c)
    intros = {
        "cs": "Hlavní chráněné ostrovy a jejich společníci z druhé vlny PvE — bezpečná startovní ekonomika (viz [Úrovně ochrany](/{lang}/zones/protection/)).",
        "de": "Die geschützten Hauptinseln und ihre PvE-Gefährten der zweiten Welle — die sichere Starterwirtschaft (siehe [Schutzstufen](/{lang}/zones/protection/)).",
        "es": "Las islas protegidas principales y sus compañeras PvE de segunda ola: la economía inicial segura (consulte [Niveles de protección](/{lang}/zones/protection/)).",
        "fr": "Les îles principales protégées et leurs compagnes JcE de seconde vague — l'économie sûre des débutants (voir [Niveaux de protection](/{lang}/zones/protection/)).",
        "it": "Le principali isole protette e le loro compagne PvE di seconda ondata — l'economia iniziale sicura (vedi [Livelli di protezione](/{lang}/zones/protection/)).",
        "ja": "主要な保護島と第2波のPvEコンパニオン島 — 安全なスターター経済（[保護レベル](/{lang}/zones/protection/)を参照）。",
        "ko": "주요 보호 섬과 2차 PvE 동반 섬 — 안전한 초반 경제([보호 레벨](/{lang}/zones/protection/) 참조).",
        "nl": "De belangrijkste beschermde eilanden en hun PvE-metgezellen van de tweede golf — de veilige starterseconomie (zie [Beschermingsniveaus](/{lang}/zones/protection/)).",
        "pl": "Główne chronione wyspy i ich towarzysze PvE drugiej fali — bezpieczna gospodarka startowa (zobacz [Poziomy ochrony](/{lang}/zones/protection/)).",
        "pt": "As principais ilhas protegidas e suas companheiras PvE de segunda onda — a economia inicial segura (consulte [Níveis de proteção](/{lang}/zones/protection/)).",
        "ru": "Основные защищенные острова и их спутники второй волны PvE — безопасная начальная экономика (см. [Уровни защиты](/{lang}/zones/protection/)).",
        "zh-CN": "主要受保护岛屿及其第二波PvE伴生岛 — 安全的初期经济（参见[保护级别](/{lang}/zones/protection/)）。",
        "zh-TW": "主要受保護島嶼及其第二波PvE伴生島 — 安全的初期經濟（參見[保護級別](/{lang}/zones/protection/)）。"
    }
    desc_intro = intros.get(lang, intros["fr"]).format(lang=lang)
    c = re.sub(r'The main protected islands and their second-wave PvE companions.*?\n', desc_intro + "\n", c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{tr("World map", lang)}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{tr("Zone index", lang)}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{tr("Protection levels", lang)}](/{lang}/zones/protection/)', c)
    return c

def process_beta_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    if lang in BETA_DESC:
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{BETA_DESC[lang]}"', c)
    intros = {
        "cs": "Ostrovy s otevřeným PvP: PvP protějšky tří hlavních ostrovů (názvy '_real'), osm bránových ostrovů každé galaxie a speciální zóny ([PvP aréna](/{lang}/zones/zone-pvp-arena/) a pevnosti — chráněné instance, uvedené zde pro úplnost).",
        "de": "Die offenen PvP-Inseln: die PvP-Zwillinge der drei Hauptinseln (die '_real'-Namen), die acht Torinseln jeder Galaxie und die Sonderzonen (die [PvP-Arena](/{lang}/zones/zone-pvp-arena/) und die Festungen — geschützte Instanzen, der Vollständigkeit halber aufgeführt).",
        "es": "Las islas de PvP abierto: las gemelas PvP de las tres islas principales (los nombres '_real'), las ocho islas de puerta de cada galaxia y las zonas especiales (la [arena PvP](/{lang}/zones/zone-pvp-arena/) y las fortalezas: instancias protegidas, enumeradas aquí para mayor integridad).",
        "fr": "Les îles JcJ ouvertes : les jumelles JcJ des trois îles principales (noms '_real'), les huit îles de porte de chaque galaxie et les zones spéciales (l'[arène JcJ](/{lang}/zones/zone-pvp-arena/) et les bastions — instances protégées, répertoriées pour mémoire).",
        "it": "Le isole PvP aperte: le gemelle PvP delle tre isole principali (i nomi '_real'), le otto isole varco di ciascuna galassia e le zone speciali (l'[arena PvP](/{lang}/zones/zone-pvp-arena/) e le roccaforti — istanze protette, elencate qui per completezza).",
        "ja": "オープンPvPの島々：3つの主要島のPvPツイン（'_real'名）、各銀河の8つのゲート島、および特別ゾーン（[PvPアリーナ](/{lang}/zones/zone-pvp-arena/)とストロングホールド — 完全性のために記載された保護インスタンス）。",
        "ko": "오픈 PvP 섬: 세 주요 섬의 PvP 트윈('_real' 이름), 각 은하의 8개 게이트 섬, 특수 존([PvP 아레나](/{lang}/zones/zone-pvp-arena/) 및 요새 — 완전성을 위해 나열된 보호 인스턴스).",
        "nl": "De open-PvP-eilanden: de PvP-tweeling van de drie hoofdeilanden (de '_real'-namen), de acht poorteilanden van elk sterrenstelsel en de speciale zones (de [PvP-arena](/{lang}/zones/zone-pvp-arena/) en de bolwerken — beschermde instanties, hier vermeld voor de volledigheid).",
        "pl": "Wyspy otwartego PvP: bliźniacze wyspy PvP trzech głównych wysp (nazwy '_real'), osiem wysp bramowych każdej galaktyki oraz strefy specjalne ([arena PvP](/{lang}/zones/zone-pvp-arena/) i twierdze — chronione instancje wymienione dla kompletności).",
        "pt": "As ilhas de PvP aberto: os pares PvP das três ilhas principais (os nomes '_real'), as oito ilhas de portão de cada galáxia e as zonas especiais (a [arena PvP](/{lang}/zones/zone-pvp-arena/) e as fortalezas — instâncias protegidas, listadas aqui para fins de integridade).",
        "ru": "Острова с открытым PvP: PvP-двойники трех главных островов (названия '_real'), восемь вратных островов каждой галактики и особые зоны ([PvP-арена](/{lang}/zones/zone-pvp-arena/) и цитадели — защищенные инстансы, приведенные здесь для полноты).",
        "zh-CN": "开放PvP岛屿：三大主岛的PvP孪生岛（'_real'名称）、各星系的八个通道岛以及特殊区域（[PvP竞技场](/{lang}/zones/zone-pvp-arena/)和要塞 — 受保护的副本，在此列出以确保完整性）。",
        "zh-TW": "開放PvP島嶼：三大主島的PvP攣生島（'_real'名稱）、各星系的八個通道島以及特殊區域（[PvP競技場](/{lang}/zones/zone-pvp-arena/)和要塞 — 受保護的副本，在此列出以確保完整性）。"
    }
    desc_intro = intros.get(lang, intros["fr"]).format(lang=lang)
    c = re.sub(r'The open-PvP islands: the three main islands\' PvP twins.*?\n', desc_intro + "\n", c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{tr("World map", lang)}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{tr("Zone index", lang)}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{tr("Protection levels", lang)}](/{lang}/zones/protection/)', c)
    return c

def process_gamma_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    if lang in GAMMA_DESC:
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{GAMMA_DESC[lang]}"', c)
    c = c.replace("## Gamma T0 — tc transit", "## Gamma T0 — transit tc" if lang == "fr" else ("## Gamma T0 — tc Transit" if lang == "de" else "## Gamma T0 — tc transit"))
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{tr("World map", lang)}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{tr("Zone index", lang)}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{tr("Protection levels", lang)}](/{lang}/zones/protection/)', c)
    return c

def process_zone_index_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    if lang in ZONE_INDEX_DESC:
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{ZONE_INDEX_DESC[lang]}"', c)
    c = re.sub(r'title:\s*"Zone index"', f'title: "{tr("Zone index", lang)}"', c)
    c = re.sub(r'^#\s*Zone index', f'# {tr("Zone index", lang)}', c, flags=re.MULTILINE)
    c = c.replace("## Training", f"## {tr('Training', lang)}")
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{tr("World map", lang)}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{tr("Protection levels", lang)}](/{lang}/zones/protection/)', c)
    return c

def process_map_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    world_tr = tr("World", lang)
    if lang in MAP_DESC:
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{MAP_DESC[lang]}"', c)
    c = re.sub(r'title:\s*"World"', f'title: "{world_tr}"', c)
    c = re.sub(r'^#\s*World', f'# {world_tr}', c, flags=re.MULTILINE)
    return c

def main():
    root = Path(".")
    src_zones_dir = root / "content" / "zones"

    if not src_zones_dir.exists():
        print(f"gen_zone_translations: source directory {src_zones_dir} not found!", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    generated_count = 0

    HANDWRITTEN_PROSE = {
        "_index.md", "protection.md", "generation.md",
        "zone_tm.md", "zone_asi.md", "zone_gamma_z106.md"
    }

    all_zone_files = sorted(src_zones_dir.glob("*.md"))

    for lang in LANGUAGES:
        dest_dir = root / "content" / lang / "zones"
        dest_dir.mkdir(parents=True, exist_ok=True)

        for src_file in all_zone_files:
            fname = src_file.name

            # Skip the 6 rich prose pages (managed separately by translators)
            if fname in HANDWRITTEN_PROSE:
                continue

            content = src_file.read_text(encoding="utf-8")

            if fname == "alpha.md":
                out_content = process_alpha_overview(content, lang)
            elif fname == "beta.md":
                out_content = process_beta_overview(content, lang)
            elif fname == "gamma.md":
                out_content = process_gamma_overview(content, lang)
            elif fname == "zone-index.md":
                out_content = process_zone_index_overview(content, lang)
            elif fname == "map.md":
                out_content = process_map_overview(content, lang)
            else:
                out_content = process_generated_zone_page(content, lang)

            dest_path = dest_dir / fname
            dest_path.write_text(out_content, encoding="utf-8")
            generated_count += 1

    dt = time.time() - t0
    print(f"gen_zone_translations: wrote {generated_count} localized zone files across {len(LANGUAGES)} languages in {dt:.2f}s")

if __name__ == "__main__":
    main()
