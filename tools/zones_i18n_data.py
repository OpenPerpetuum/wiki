"""Localized content data for zones/protection.md and zones/_index.md across all 13 supported languages.
"""

PROTECTION_DATA = {
    "cs": (
        "Úrovně ochrany",
        "Alpha, beta a gamma — tři úrovně ochrany každé zóny, co která dovoluje a jak je poznat v klientovi.",
        """# Úrovně ochrany

Každá zóna má úroveň ochrany: **alpha**, **beta** nebo **gamma**. Úroveň je nastavena pro každou zónu v databázi serveru (příznaky zóny *protected* a *terraformable*) a určuje, co v ní můžete dělat — především zda na vás mohou útočit ostatní hráči a zda lze přetvářet terén.

| Úroveň | Příznak na zóně | PvP | Bloby | Teraformace | Kde se nachází |
|---|---|---|---|---|---|
| **Alpha** | chráněná | není možné | netvoří se | není možná | [Ostrovy Alpha](/zones/map/#alpha), [výcvik](/zones/zone-training/), pevnosti, [PvP aréna](/zones/zone-pvp-arena/) |
| **Beta** | otevřená, standardní terén | otevřené | tvoří se | není možná | PvP protějšky [ostrovů Alpha](/zones/map/#alpha) a pás gamma |
| **Gamma** | otevřená, teraformovatelná | otevřené | tvoří se | možná | Bránové ostrovy tří galaxií a pohraniční pás |

## Alpha — chráněná

V zóně alpha se hráči jednoduše **nemohou navzájem poškodit**: útočné palné zbraně jsou proti ostatním hráčům zakázány a poškození způsobující efekty v boji (bloby) se také netvoří. Je to bezpečná ekonomika: těžte a sklízejte bez obav. Výcviková zóna, tři startovní ostrovy a jejich PvE společníci, pevnosti a PvP aréna fungují jako alpha — aréna si zachovává své jméno pro to, co se děje *uvnitř* skriptované události, nikoli pro volný boj všech proti všem.

V klientovi se zóna alpha zobrazuje s **modrými diodami** na stavovém panelu robota.

## Beta — otevřené PvP, standardní terén

Zóna beta je plně otevřený PvP ostrov se standardním terénem: můžete být kdykoli napadeni, bloby platí a povrch ostrova je takový, jaký vygeneroval server — žádné přetváření hráči. PvP protějšky startovních ostrovů a tranzitní zóny pohraničního pásu jsou beta.

V klientovi se zóna beta zobrazuje s **oranžovými diodami**.

## Gamma — otevřené PvP, teraformovatelná

Zóna gamma je zóna beta s jednou věcí navíc: **terén je teraformovatelný**. Hráči s teraformačními nástroji mohou přetvářet povrch — kopat, zarovnávat a budovat povrch ostrova —, což mění umístění ložisek, rostlin a základen. Osm bránových ostrovů každé galaxie a ostrovy pohraničního pásu jsou gamma.

V klientovi se zóna gamma zobrazuje se **žlutými pruhy** nad a pod názvem zóny.

## Co to znamená pro hráče

- **Rozpočet rizika** — zóny alpha nestojí nic na bezpečnosti; beta a gamma nesou plné riziko PvP. Naplánujte podle toho palivo, doprovod a opravárenské kapacity.
- **Výnos vs. riziko** — otevřené ostrovy nabízejí lepší suroviny (epriton a cenné plodiny se objevují mimo chráněné ostrovy), což je důvod, proč je riziko cenou za výnos.
- **Stabilita terénu** — na ostrovech gamma se terén pod základnou může změnit: přetvořený povrch může přesunout suroviny, které základna využívá, takže dlouhodobá správa území musí počítat s teraformací ostatních.
- **Zkontrolujte před akcí** — diody na stavovém panelu robota vám ukazují úroveň zóny, ve které se nacházíte; špatně přečtená dioda je klasický způsob, jak dorazit do zóny beta s neopancéřovaným transportérem.

Úroveň každé zóny je uvedena v [indexu zón](/zones/zone-index/) (sloupec *Ochrana*) a v nápovědách na [mapě světa](/zones/map/).
"""
    ),
    "de": (
        "Schutzstufen",
        "Alpha, Beta und Gamma — die drei Schutzstufen jeder Zone, was jede erlaubt und wie man sie im Client unterscheidet.",
        """# Schutzstufen

Jede Zone hat eine Schutzstufe: **Alpha**, **Beta** oder **Gamma**. Die Stufe wird pro Zone in der Serverdatenbank festgelegt (die Flags *protected* und *terraformable* der Zone) und bestimmt, was Sie dort tun können — vor allem, ob andere Spieler Sie angreifen können und ob das Gelände umgeformt werden kann.

| Stufe | Flag der Zone | PvP | Blobs | Terraforming | Wo man es findet |
|---|---|---|---|---|---|
| **Alpha** | geschützt | nicht möglich | entstehen nicht | nicht möglich | [Alpha-Inseln](/zones/map/#alpha), [Training](/zones/zone-training/), Festungen, [PvP-Arena](/zones/zone-pvp-arena/) |
| **Beta** | offen, Standardgelände | offen | offen | nicht möglich | Die PvP-Zwillinge der [Alpha-Inseln](/zones/map/#alpha) und der Gamma-Gürtel |
| **Gamma** | offen, terraformbar | offen | offen | möglich | Die Torinseln der drei Galaxien und der Grenzbereich |

## Alpha — geschützt

In einer Alpha-Zone können sich Spieler schlicht **nicht gegenseitig beschädigen**: Angreifende Feuerwaffen sind gegen andere Spieler deaktiviert, und die Schadenseffekte, die sich im Kampf auf Ihnen stapeln (Blobs), entstehen ebenfalls nicht. Es ist die sichere Wirtschaft: Bauen und ernten Sie ab, ohne über die Schulter schauen zu müssen. Die Trainingszone, die drei Startinseln und ihre PvE-Begleiter, die Festungen und die PvP-Arena laufen alle als Alpha — die Arena behält ihren Namen für das, was *innerhalb* des geskripteten Events passiert, nicht für ein Jeder-gegen-jeden.

Im Client wird eine Alpha-Zone durch die **blauen Dioden** auf dem Bot-Status angezeigt.

## Beta — offenes PvP, Standardgelände

Eine Beta-Zone ist eine vollkommen offene PvP-Insel mit Standardgelände: Sie können jederzeit angegriffen werden, Blobs greifen, und der Inselboden ist das, was der Server generiert hat — keine Umformung durch Spieler. Die PvP-Zwillinge der Startinseln (die „echten“ Inseln der drei Galaxien und die TC-Transitzonen des Grenzbereichs) sind Beta.

Im Client wird eine Beta-Zone durch die **orangen Dioden** angezeigt.

## Gamma — offenes PvP, terraformbar

Eine Gamma-Zone ist eine Beta-Zone plus eine weitere Sache: **Das Gelände ist terraformbar**. Spieler mit Terraforming-Werkzeugen können den Boden umformen — graben, ebnen und die Inseloberfläche gestalten —, was ändert, wo Vorkommen, Pflanzen und Basen liegen können. Die acht Torinseln jeder Galaxie und die Inseln des Grenzbereichs sind Gamma.

Im Client wird eine Gamma-Zone durch die **gelben Streifen** über und unter dem Zonennamen angezeigt.

## Was das für Spieler ändert

- **Risikobudget** — Alpha-Zonen kosten nichts an Sicherheit; Beta und Gamma fordern das volle PvP-Risiko. Planen Sie Treibstoff, Geleitschutz und Reparaturkapazität entsprechend.
- **Ertrag vs. Risiko** — Die offenen Inseln beherbergen das bessere Material (Epriton und hochwertige Erntepflanzen erscheinen außerhalb der geschützten Inseln), weshalb das Risiko der Preis des Ertrags ist.
- **Geländestabilität** — Auf Gamma-Inseln kann sich der Boden unter einer Basis verändern: Eine umgeformte Oberfläche kann die Ressourcen verschieben, von denen sich eine Basis speist. Langfristige Territorialarbeit muss Terraforming durch andere einkalkulieren.
- **Prüfen vor dem Einsatz** — Die Dioden auf dem Bot-Status zeigen die Stufe der Zone an, in der Sie sich befinden. Eine falsch abgelesene Diode ist der klassische Weg, mit einem ungepanzerten Transporter in einer Beta-Zone zu landen.

Jede Zonenstufe ist im [Zonenindex](/zones/zone-index/) (Spalte *Schutz*) und in den Tooltips auf der [Weltkarte](/zones/map/) aufgeführt.
"""
    ),
    "es": (
        "Niveles de protección",
        "Alfa, beta y gamma: los tres niveles de protección de cada zona, lo que permite cada uno y cómo diferenciarlos en el cliente.",
        """# Niveles de protección

Cada zona tiene un nivel de protección: **alfa**, **beta** o **gamma**. El nivel se define por zona en la base de datos del servidor (los indicadores *protected* y *terraformable* de la zona) y determina lo que se puede hacer allí, sobre todo si otros jugadores pueden atacarte y si se puede remodelar el terreno.

| Nivel | Indicador de la zona | PvP | Blobs | Terraformación | Dónde encontrarlo |
|---|---|---|---|---|---|
| **Alfa** | protegida | no es posible | no se forman | no es posible | [Islas Alfa](/zones/map/#alpha), [entrenamiento](/zones/zone-training/), fortalezas, [arena PvP](/zones/zone-pvp-arena/) |
| **Beta** | abierta, terreno estándar | abierto | abiertos | no es posible | Las gemelas PvP de las [islas Alfa](/zones/map/#alpha) y el cinturón gamma |
| **Gamma** | abierta, terraformable | abierto | abiertos | posible | Las islas de portal de las tres galaxias y el cinturón fronterizo |

## Alfa — protegida

En una zona alfa los jugadores simplemente **no pueden dañarse entre sí**: las armas de fuego atacantes están deshabilitadas contra otros jugadores y los efectos de acumulación de daño en combate (blobs) no se forman. Es la economía segura: mina y cosecha sin mirar por encima del hombro. La zona de entrenamiento, las tres islas iniciales y sus compañeras PvE, las fortalezas y la arena PvP funcionan como alfa.

En el cliente, una zona alfa se muestra con los **diodos azules** en el estado del robot.

## Beta — PvP abierto, terreno estándar

Una zona beta es una isla PvP totalmente abierta con terreno estándar: puedes ser atacado en cualquier momento, los blobs se aplican y el suelo de la isla es el generado por el servidor, sin remodelación por parte de los jugadores. Las gemelas PvP de las islas iniciales y las zonas de tránsito tc del cinturón fronterizo son beta.

En el cliente, una zona beta se muestra con los **diodos naranjas**.

## Gamma — PvP abierto, terraformable

Una zona gamma es una zona beta con una característica adicional: **el terreno es terraformable**. Los jugadores con herramientas de terraformación pueden remodelar el suelo (cavar, nivelar y construir la superficie de la isla), lo que cambia la ubicación de los yacimientos, plantas y bases. Las ocho islas de portal de cada galaxia y las islas del cinturón fronterizo son gamma.

En el cliente, una zona gamma se muestra con las **franjas amarillas** por encima y por debajo del nombre de la zona.

## Qué cambia esto para el jugador

- **Presupuesto de riesgo** — las zonas alfa no conllevan riesgo para la seguridad; beta y gamma implican todo el riesgo del PvP. Planifica combustible, escoltas y capacidad de reparación en consecuencia.
- **Rendimiento vs. riesgo** — las islas abiertas contienen los mejores materiales (epriton y recursos cosechables de alto nivel), por lo que el riesgo es el precio del rendimiento.
- **Estabilidad del terreno** — en las islas gamma el suelo puede cambiar bajo una base: una superficie modificada puede desplazar los recursos de los que se alimenta la base.
- **Comprueba antes de entrar** — los diodos en el estado del robot te indican el nivel de la zona en la que te encuentras; una lectura incorrecta del diodo es la forma habitual de llegar a una zona beta en un transporte sin blindaje.

El nivel de cada zona figura en el [índice de zonas](/zones/zone-index/) (columna *Protección*) y en la información sobre herramientas del [mapa del mundo](/zones/map/).
"""
    ),
    "fr": (
        "Niveaux de protection",
        "Alpha, bêta et gamma — les trois niveaux de protection de chaque zone, leurs règles et comment les identifier dans le client.",
        """# Niveaux de protection

Chaque zone possède un niveau de protection : **alpha**, **bêta** ou **gamma**. Ce niveau est défini par zone dans la base de données du serveur (les drapeaux *protected* et *terraformable* de la zone) et détermine ce que vous pouvez y faire — en particulier si d'autres joueurs peuvent vous attaquer et si le terrain peut être remodelé.

| Niveau | Drapeau de zone | PvP | Blobs | Terraformation | Où le trouver |
|---|---|---|---|---|---|
| **Alpha** | protégée | impossible | non formés | impossible | [Îles Alpha](/zones/map/#alpha), [entraînement](/zones/zone-training/), forteresses, [arène PvP](/zones/zone-pvp-arena/) |
| **Bêta** | ouverte, terrain standard | ouvert | ouverts | impossible | Les jumelles PvP des [îles Alpha](/zones/map/#alpha) et la ceinture gamma |
| **Gamma** | ouverte, terraformable | ouvert | ouverts | possible | Les îles de portail des trois galaxies et la ceinture frontière |

## Alpha — protégée

Dans une zone alpha, les joueurs **ne peuvent tout simplement pas s'infliger de dégâts** : les armes sont désactivées contre les autres joueurs et les effets de dégâts cumulés en combat (blobs) ne se forment pas. C'est l'économie sécurisée : minez et récoltez l'esprit tranquille. La zone d'entraînement, les trois îles de départ et leurs homologues PvE, les forteresses et l'arène PvP fonctionnent en alpha.

Dans le client, une zone alpha est signalée par des **diodes bleues** sur le statut du robot.

## Bêta — PvP ouvert, terrain standard

Une zone bêta est une île PvP entièrement ouverte avec un terrain standard : vous pouvez être attaqué à tout moment, les blobs s'appliquent et le sol reste celui généré par le serveur — aucun remodelage par les joueurs. Les jumelles PvP des îles de départ et les zones de transit tc de la ceinture frontière sont bêta.

Dans le client, une zone bêta est signalée par des **diodes oranges**.

## Gamma — PvP ouvert, terraformable

Une zone gamma est une zone bêta avec un atout supplémentaire : **le terrain est terraformable**. Les joueurs équipés d'outils de terraformation peuvent modifier le sol — creuser, niveler et bâtir la surface de l'île —, ce qui déplace les gisements, la végétation et les bases. Les huit îles de portail de chaque galaxie et les îles de la frontière sont gamma.

Dans le client, une zone gamma est signalée par des **bandes jaunes** au-dessus et en dessous du nom de la zone.

## Ce que cela change pour le joueur

- **Gestion du risque** — les zones alpha n'ont aucun coût en sécurité ; bêta et gamma comportent tous les risques du PvP. Prévoyez carburant, escortes et réparations en conséquence.
- **Rendement vs risque** — les îles ouvertes abritent les meilleurs matériaux (épriton et récoltes de haut niveau), le risque étant la contrepartie du rendement.
- **Stabilité du terrain** — sur les îles gamma, le sol peut changer sous une base : une surface remodelée peut déplacer les ressources exploitées.
- **Vérifiez avant de vous engager** — les diodes du statut de robot indiquent le niveau de la zone ; se tromper de diode est le moyen classique d'entrer en zone bêta sans blindage.

Le niveau de chaque zone est répertorié dans l'[index des zones](/zones/zone-index/) (colonne *Protection*) et dans les infobulles de la [carte du monde](/zones/map/).
"""
    ),
    "it": (
        "Livelli di protezione",
        "Alpha, beta e gamma: i tre livelli di protezione di ciascuna zona, cosa consentono e come distinguerli nel client.",
        """# Livelli di protezione

Ogni zona ha un livello di protezione: **alpha**, **beta** o **gamma**. Il livello è impostato per ciascuna zona nel database del server (i flag *protected* e *terraformable*) e stabilisce cosa vi è consentito fare, soprattutto se gli altri giocatori possono attaccarvi e se il terreno può essere rimodellato.

| Livello | Flag della zona | PvP | Blob | Terraformazione | Dove trovarlo |
|---|---|---|---|---|---|
| **Alpha** | protetta | non possibile | non formati | non possibile | [Isole Alpha](/zones/map/#alpha), [addestramento](/zones/zone-training/), roccaforti, [arena PvP](/zones/zone-pvp-arena/) |
| **Beta** | aperta, terreno standard | aperto | aperti | non possibile | Le gemelle PvP delle [isole Alpha](/zones/map/#alpha) e la cintura gamma |
| **Gamma** | aperta, terraformabile | aperto | aperti | possibile | Le isole dei portali delle tre galassie e la cintura di frontiera |

## Alpha — protetta

In una zona alpha i giocatori semplicemente **non possono danneggiarsi a vicenda**: le armi da fuoco sono disabilitate contro gli altri giocatori e gli effetti di danno da combattimento (blob) non si formano. È l'economia sicura: estraete e raccogliete senza guardarvi alle spalle. La zona di addestramento, le tre isole iniziali e le relative compagne PvE, le roccaforti e l'arena PvP operano tutte come alpha.

Nel client, una zona alpha viene indicata dai **diodi blu** sullo stato del robot.

## Beta — PvP aperto, terreno standard

Una zona beta è un'isola PvP completamente aperta con terreno standard: potete essere attaccati in qualsiasi momento, i blob si applicano e il suolo è quello generato dal server (nessuna alterazione da parte dei giocatori). Le gemelle PvP delle isole iniziali e le zone di transito tc della cintura di frontiera sono beta.

Nel client, una zona beta viene indicata dai **diodi arancioni**.

## Gamma — PvP aperto, terraformabile

Una zona gamma è una zona beta con una caratteristica in più: **il terreno è terraformabile**. I giocatori con strumenti di terraformazione possono rimodellare il suolo — scavare, livellare e modellare la superficie dell'isola —, modificando la posizione di nodi minerari, piante e basi. Le otto isole dei portali di ciascuna galassia e le isole della frontiera sono gamma.

Nel client, una zona gamma viene indicata dalle **strisce gialle** sopra e sotto il nome della zona.

## Cosa cambia per i giocatori

- **Budget del rischio** — le zone alpha offrono sicurezza totale; beta e gamma comportano l'intero rischio PvP. Pianificate carburante, scorte e riparazioni di conseguenza.
- **Rendimento vs rischio** — le isole aperte contengono i materiali migliori (epriton e piante di alto livello), motivo per cui il rischio è il prezzo della resa.
- **Stabilità del terreno** — nelle isole gamma il terreno sotto una base può cambiare: una superficie rimodellata può spostare le risorse necessarie.
- **Controllate prima di procedere** — i diodi sullo stato del robot indicano il livello della zona attuale; leggere male un diodo è il modo classico per finire in una zona beta con un trasporto privo di corazza.

Il livello di ciascuna zona è indicato nell'[indice delle zone](/zones/zone-index/) (colonna *Protezione*) e nei tooltip sulla [mappa del mondo](/zones/map/).
"""
    ),
    "ja": (
        "保護レベル",
        "アルファ、ベータ、ガンマ — 各ゾーンの3つの保護レベル、許可される行動、クライアントでの識別方法。",
        """# 保護レベル

すべてのゾーンには保護レベル（**アルファ**、**ベータ**、**ガンマ**）が設定されています。このレベルはサーバーデータベースのゾーンフラグ（*protected*および*terraformable*）によってゾーンごとに設定され、他のプレイヤーから攻撃を受けるか、地形を変更できるかなどを決定します。

| レベル | ゾーンフラグ | PvP | ブロブ | テラフォーミング | 主な場所 |
|---|---|---|---|---|---|
| **アルファ** | 保護（protected） | 不可 | 発生なし | 不可 | [アルファ諸島](/zones/map/#alpha)、[訓練](/zones/zone-training/)、拠点要塞、[PvPアリーナ](/zones/zone-pvp-arena/) |
| **ベータ** | 開放・標準地形 | 可能 | 有効 | 不可 | [アルファ諸島](/zones/map/#alpha)のPvP対向島、ガンマベルト |
| **ガンマ** | 開放・テラフォーミング可 | 可能 | 有効 | 可能 | 3銀河のゲート島、フロンティアベルト |

## アルファ — 保護

アルファゾーンでは、プレイヤー同士が**互いにダメージを与えることはできません**。他のプレイヤーに対する射撃武器は無効化され、戦闘ダメージ蓄積効果（ブロブ）も発生しません。安全な経済圏として、警戒することなく採掘や収穫を行うことができます。

クライアントでは、アルファゾーンは機体ステータス上の**青色ダイオード**で表示されます。

## ベータ — 開放型PvP・標準地形

ベータゾーンは標準地形の完全開放型PvP島です。いつでも攻撃を受ける可能性があり、ブロブも適用され、地面はサーバーによって生成された状態のまま維持されます（プレイヤーによる地形改変は不可）。

クライアントでは、ベータゾーンは**オレンジ色ダイオード**で表示されます。

## ガンマ — 開放型PvP・テラフォーミング可

ガンマゾーンはベータゾーンの特性に加え、**地形のテラフォーミングが可能**です。テラフォーミングツールを持つプレイヤーは地面を掘削・整地して島の表面を再成形でき、鉱床や植物、拠点の配置が変化します。

クライアントでは、ガンマゾーンはゾーン名の上下に**黄色いストライプ**で表示されます。

## プレイヤーへの影響

- **リスク管理** — アルファゾーンは安全コストがゼロですが、ベータおよびガンマは全面的なPvPリスクが伴います。燃料、護衛、修理能力を適切に準備してください。
- **収益とリスク** — 開放された島にはより優れた素材（エプリトンや高ティア収穫物）が存在するため、リスクは収益の代償となります。
- **地形の安定性** — ガンマ島では拠点の下の地面が変化する可能性があり、他者によるテラフォーミングを計算に入れる必要があります。
- **突入前の確認** — 機体ステータスのダイオードで現在地の保護レベルを確認できます。

各ゾーンの保護レベルは[ゾーン一覧](/zones/zone-index/)（*保護*列）および[ワールドマップ](/zones/map/)のツールチップに記載されています。
"""
    ),
    "ko": (
        "보호 수준",
        "알파, 베타, 감마 — 각 구역의 3가지 보호 수준과 클라이언트에서의 식별 방법.",
        """# 보호 수준

모든 구역에는 **알파**, **베타**, **감마** 중 하나의 보호 수준이 지정되어 있습니다. 이 수준은 서버 데이터베이스의 구역 플래그(*protected* 및 *terraformable*)에 따라 설정되며, 다른 플레이어의 공격 가능 여부와 지형 변형 가능 여부를 결정합니다.

| 수준 | 구역 플래그 | PvP | 블롭 | 테라포밍 | 위치 |
|---|---|---|---|---|---|
| **알파** | 보호 (protected) | 불가 | 생성 안 됨 | 불가 | [알파 섬](/zones/map/#alpha), [훈련](/zones/zone-training/), 요새, [PvP 아레나](/zones/zone-pvp-arena/) |
| **베타** | 개방, 표준 지형 | 개방 | 적용됨 | 불가 | [알파 섬](/zones/map/#alpha)의 PvP 대칭 섬 및 감마 벨트 |
| **감마** | 개방, 테라포밍 가능 | 개방 | 적용됨 | 가능 | 3개 은하의 게이트 섬 및 개척 벨트 |

## 알파 — 보호 구역

알파 구역에서는 플레이어들이 **서로에게 피해를 입힐 수 없습니다**. 다른 플레이어에 대한 공격 무기가 비활성화되며 전투 피해 누적 효과(블롭)도 생성되지 않습니다. 안전한 경제 구역으로서 주변을 경계하지 않고 채굴과 채집에 전념할 수 있습니다.

클라이언트에서 알파 구역은 로봇 상태창의 **파란색 다이오드**로 표시됩니다.

## 베타 — 개방형 PvP, 표준 지형

베타 구역은 표준 지형을 갖춘 완전 개방형 PvP 섬입니다. 언제든 공격받을 수 있고 블롭이 적용되며, 서버가 생성한 지형 그대로 유지됩니다.

클라이언트에서 베타 구역은 **주황색 다이오드**로 표시됩니다.

## 감마 — 개방형 PvP, 테라포밍 가능

감마 구역은 베타 구역의 특징에 한 가지가 더해진 구역입니다. 바로 **지형을 테라포밍할 수 있다는 점**입니다. 테라포밍 도구를 가진 플레이어는 땅을 파거나 평탄화하여 섬 표면을 재구성할 수 있습니다.

클라이언트에서 감마 구역은 구역 이름 위아래에 **노란색 줄무늬**로 표시됩니다.

## 플레이어 유의 사항

- **위험도 고려** — 알파 구역은 안전하지만, 베타 및 감마 구역은 완전한 PvP 위험을 감수해야 합니다. 연료, 호위, 수리 역량을 미리 준비하세요.
- **수익 대 위험** — 개방된 섬에는 더 귀중한 자원(에프리톤 및 고티어 채집물)이 존재합니다.
- **지형 안정성** — 감마 섬에서는 기지 아래의 지형이 바뀔 수 있으므로 다른 플레이어의 테라포밍을 고려해야 합니다.
- **진입 전 확인** — 로봇 상태창의 다이오드를 통해 현재 구역의 보호 수준을 항상 확인하세요.

모든 구역의 보호 수준은 [구역 색인](/zones/zone-index/) 및 [월드 맵](/zones/map/)의 툴팁에 표시됩니다.
"""
    ),
    "nl": (
        "Beschermingsniveaus",
        "Alpha, beta en gamma — de drie beschermingsniveaus van elke zone, wat elk niveau toestaat en hoe ze in de client te herkennen zijn.",
        """# Beschermingsniveaus

Elke zone heeft een beschermingsniveau: **alpha**, **beta** of **gamma**. Dit niveau wordt per zone ingesteld in de serverdatabase (de vlaggen *protected* en *terraformable*) en bepaalt wat u daar mag doen — vooral of andere spelers u kunnen aanvallen en of het terrein kan worden vervormd.

| Niveau | Vlag op de zone | PvP | Blobs | Terraforming | Waar u het vindt |
|---|---|---|---|---|---|
| **Alpha** | beschermd | niet mogelijk | worden niet gevormd | niet mogelijk | [Alpha-eilanden](/zones/map/#alpha), [training](/zones/zone-training/), bolwerken, [PvP-arena](/zones/zone-pvp-arena/) |
| **Beta** | open, standaardterrein | open | open | niet mogelijk | De PvP-tweeling van de [Alpha-eilanden](/zones/map/#alpha) en de gamma-gordel |
| **Gamma** | open, terraformbaar | open | open | mogelijk | De poorteilanden van de drie melkwegstelsels en de grensgordel |

## Alpha — beschermd

In een alpha-zone kunnen spelers **elkaar simpelweg niet beschadigen**: aanvalswapens zijn uitgeschakeld tegen andere spelers en schade-effecten (blobs) worden niet gevormd. Het is de veilige economie: mijnen en oogsten zonder over uw schouder te hoeven kijken. De trainingszone, de drie starteilanden en hun PvE-metgezellen, de bolwerken en de PvP-arena draaien allemaal als alpha.

In de client is een alpha-zone herkenbaar aan de **blauwe diodes** op de robotstatus.

## Beta — open PvP, standaardterrein

Een beta-zone is een volledig open PvP-eiland met standaardterrein: u kunt op elk moment worden aangevallen, blobs zijn van kracht en de eilandgrond is zoals de server deze heeft gegenereerd — geen aanpassingen door spelers. De PvP-tweelingen van de starteilanden en de transitzones van de grensgordel zijn beta.

In de client is een beta-zone herkenbaar aan de **oranje diodes**.

## Gamma — open PvP, terraformbaar

Een gamma-zone is een beta-zone met één extra eigenschap: **het terrein is terraformbaar**. Spelers met terraforming-gereedschappen kunnen de grond vervormen — graven, egaliseren en bouwen —, wat invloed heeft op waar aders, planten en bases zich bevinden. De acht poorteilanden van elk melkwegstelsel en de eilanden van de grensgordel zijn gamma.

In de client is een gamma-zone herkenbaar aan de **gele strepen** boven en onder de zonenaam.

## Wat dit verandert voor spelers

- **Risicobudget** — alpha-zones kosten niets aan veiligheid; beta en gamma dragen het volledige PvP-risico. Plan brandstof, escortes en reparatiecapaciteit dienovereenkomstig.
- **Opbrengst vs. risico** — de open eilanden bevatten betere grondstoffen (epriton en hoogwaardige gewassen), daarom is het risico de prijs van de opbrengst.
- **Terreinstabiliteit** — op gamma-eilanden kan de grond onder een basis veranderen: een aangepast oppervlak kan grondstoffen verplaatsen.
- **Controleer voor u begint** — de diodes op de robotstatus vertellen u het niveau van de zone waarin u zich bevindt.

Het niveau van elke zone staat vermeld in de [zone-index](/zones/zone-index/) (kolom *Bescherming*) en in de tooltips op de [wereldkaart](/zones/map/).
"""
    ),
    "pl": (
        "Poziomy ochrony",
        "Alpha, beta i gamma — trzy poziomy ochrony każdej strefy, zasady PvP i oznaczenia w kliencie.",
        """# Poziomy ochrony

Każda strefa posiada poziom ochrony: **alpha**, **beta** lub **gamma**. Poziom jest ustawiany dla każdej strefy w bazie danych serwera (flagi strefy *protected* i *terraformable*) i decyduje o dozwolonych działaniach — przede wszystkim o tym, czy inni gracze mogą cię zaatakować oraz czy teren można przekształcać.

| Poziom | Flaga strefy | PvP | Bloby | Terraformowanie | Gdzie go znajdziesz |
|---|---|---|---|---|---|
| **Alpha** | chroniona | niemożliwe | nie powstają | niemożliwe | [Wyspy Alpha](/zones/map/#alpha), [trening](/zones/zone-training/), twierdze, [arena PvP](/zones/zone-pvp-arena/) |
| **Beta** | otwarta, standardowy teren | otwarte | aktywne | niemożliwe | Bliźniacze wyspy PvP [wysp Alpha](/zones/map/#alpha) i pas gamma |
| **Gamma** | otwarta, terraformowalna | otwarte | aktywne | możliwe | Wyspy bram trzech galaktyk i pas graniczny |

## Alpha — chroniona

W strefie alpha gracze po prostu **nie mogą zadawać sobie nawzajem obrażeń**: broń przeciwko innym graczom jest wyłączona, a efekty kumulacji obrażeń w walce (bloby) nie powstają. To bezpieczna gospodarka: wydobywaj i zbieraj surowce bez oglądania się za siebie. Strefa treningowa, trzy wyspy początkowe i ich towarzysze PvE, twierdze oraz arena PvP działają w trybie alpha.

W kliencie strefa alpha jest oznaczona **niebieskimi diodami** na panelu stanu robota.

## Beta — otwarte PvP, standardowy teren

Strefa beta to w pełni otwarta wyspa PvP ze standardowym terenem: możesz zostać zaatakowany w dowolnym momencie, bloby obowiązują, a ukształtowanie terenu pozostaje takie, jakie wygenerował serwer.

W kliencie strefa beta jest oznaczona **pomarańczowymi diodami**.

## Gamma — otwarte PvP, terraformowalna

Strefa gamma to strefa beta z jedną kluczową różnicą: **teren można terraformować**. Gracze posiadający narzędzia do terraformowania mogą modyfikować grunt — kopać, wyrównywać i kształtować powierzchnię wyspy —, co zmienia położenie złóż, roślin i baz.

W kliencie strefa gamma jest oznaczona **żółtymi pasami** nad i pod nazwą strefy.

## Co to oznacza dla gracza

- **Zarządzanie ryzykiem** — strefy alpha zapewniają pełne bezpieczeństwo; beta i gamma niosą ze sobą pełne ryzyko PvP. Odpowiednio zaplanuj paliwo, eskortę i możliwości naprawcze.
- **Wydajność a ryzyko** — otwarte wyspy kryją lepsze surowce (epriton i cenne rośliny), dlatego ryzyko jest ceną za wyższe zyski.
- **Stabilność terenu** — na wyspach gamma grunt pod bazą może ulec zmianie pod wpływem terraformowania przez innych graczy.
- **Sprawdź przed wyruszeniem** — diody na panelu robota wskazują poziom ochrony strefy.

Poziom każdej strefy jest wymieniony w [indeksie stref](/zones/zone-index/) (kolumna *Ochrona*) oraz w podpowiedziach na [mapie świata](/zones/map/).
"""
    ),
    "pt": (
        "Níveis de proteção",
        "Alfa, beta e gama — os três níveis de proteção de cada zona, o que cada um permite e como identificá-los no cliente.",
        """# Níveis de proteção

Cada zona possui um nível de proteção: **alfa**, **beta** ou **gama**. O nível é definido por zona no banco de dados do servidor (sinalizadores *protected* e *terraformable*) e determina o que você pode fazer lá — sobretudo se outros jogadores podem atacá-lo e se o terreno pode ser remodelado.

| Nível | Sinalizador da zona | PvP | Blobs | Terraformação | Onde encontrar |
|---|---|---|---|---|---|
| **Alfa** | protegida | não permitido | não se formam | não permitido | [Ilhas Alfa](/zones/map/#alpha), [treinamento](/zones/zone-training/), fortalezas, [arena PvP](/zones/zone-pvp-arena/) |
| **Beta** | aberta, terreno padrão | aberto | abertos | não permitido | As gêmeas PvP das [ilhas Alfa](/zones/map/#alpha) e o cinturão gama |
| **Gama** | aberta, terraformável | aberto | abertos | permitido | As ilhas de portal das três galáxias e o cinturão de fronteira |

## Alfa — protegida

Em uma zona alfa os jogadores simplesmente **não podem causar dano uns aos outros**: armas de ataque são desativadas contra outros jogadores e os efeitos acumulados de combate (blobs) não se formam. É a economia segura: minere e colha sem se preocupar. A zona de treinamento, as três ilhas iniciais e suas companheiras PvE, as fortalezas e a arena PvP funcionam como alfa.

No cliente, uma zona alfa é indicada pelos **diodos azuis** no status do robô.

## Beta — PvP aberto, terreno padrão

Uma zona beta é uma ilha PvP totalmente aberta com terreno padrão: você pode ser atacado a qualquer momento, os blobs se aplicam e o solo da ilha permanece como gerado pelo servidor — sem remodelação pelos jogadores. As gêmeas PvP das ilhas iniciais e as zonas de trânsito tc do cinturão de fronteira são beta.

No cliente, uma zona beta é indicada pelos **diodos laranjas**.

## Gama — PvP aberto, terraformável

Uma zona gama é uma zona beta com uma característica extra: **o terreno é terraformável**. Jogadores com ferramentas de terraformação podem remodelar o solo — cavar, nivelar e alterar a superfície da ilha —, o que muda a localização de jazidas, plantas e bases. As oito ilhas de portal de cada galáxia e as ilhas da fronteira são gama.

No cliente, uma zona gama é indicada pelas **faixas amarelas** acima e abaixo do nome da zona.

## O que isso muda para o jogador

- **Gestão de risco** — zonas alfa não custam nada em segurança; beta e gama exigem o risco total de PvP. Planeje combustível, escoltas e capacidade de reparo adequadamente.
- **Rendimento vs. risco** — as ilhas abertas abrigam os melhores materiais (epriton e recursos de alto nível), portanto o risco é o preço do rendimento.
- **Estabilidade do terreno** — nas ilhas gama o terreno sob uma base pode mudar: uma superfície remodelada pode deslocar os recursos explorados.
- **Verifique antes de entrar** — os diodos no status do robô indicam o nível da zona atual.

O nível de cada zona está listado no [índice de zonas](/zones/zone-index/) (coluna *Proteção*) e nas dicas da [mapa mundial](/zones/map/).
"""
    ),
    "ru": (
        "Уровни защиты",
        "Альфа, бета и гамма — три уровня защиты каждой зоны, правила PvP и обозначения в клиенте.",
        """# Уровни защиты

Каждая зона обладает уровнем защиты: **альфа**, **бета** или **гамма**. Уровень задается для каждой зоны в базе данных сервера (флаги зоны *protected* и *terraformable*) и определяет возможности игроков — прежде всего, возможность нападения других игроков и изменения рельефа.

| Уровень | Флаг зоны | PvP | Блобы | Терраформирование | Где встречается |
|---|---|---|---|---|---|
| **Альфа** | защищенная | невозможно | не формируются | невозможно | [Альфа-острова](/zones/map/#alpha), [тренировка](/zones/zone-training/), цитадели, [PvP-арена](/zones/zone-pvp-arena/) |
| **Бета** | открытая, стандартный рельеф | открыто | действуют | невозможно | PvP-двойники [альфа-островов](/zones/map/#alpha) и гамма-пояс |
| **Гамма** | открытая, терраформируемая | открыто | действуют | возможно | Острова врат трех галактик и пограничный пояс |

## Альфа — защищенная

В альфа-зоне игроки **не могут наносить урон друг другу**: оружие отключено против других игроков, а боевые эффекты накопления урона (блобы) не формируются. Это безопасная экономика: добыча руды и сбор растений без оглядки на врагов. Тренировочная зона, три стартовых острова и их PvE-компаньоны, цитадели и PvP-арена работают в режиме альфа.

В клиенте альфа-зона обозначается **синими диодами** на панели статуса робота.

## Бета — открытое PvP, стандартный рельеф

Бета-зона — полностью открытый PvP-остров со стандартным рельефом: нападение возможно в любой момент, блобы активны, а поверхность остается неизменной (изменение игроками недоступно). PvP-двойники стартовых островов и транзитные зоны пограничного пояса относятся к бета-уровню.

В клиенте бета-зона обозначается **оранжевыми диодами**.

## Гамма — открытое PvP, терраформируемая

Гамма-зона аналогична бета-зоне с ключевым отличием: **рельеф поддается терраформированию**. Игроки с инструментами терраформирования могут изменять ландшафт — копать, выравнивать и формировать поверхность, смещая залежи руды, растения и основания баз. Острова врат трех галактик и рубежные зоны относятся к гамма-уровню.

В клиенте гамма-зона обозначается **желтыми полосами** сверху и снизу от названия зоны.

## Что это меняет для игрока

- **Оценка рисков** — альфа-зоны абсолютно безопасны; бета и гамма несут полный риск PvP. Планируйте запасы топлива, эскорт и ремонт заранее.
- **Доходность и риск** — на открытых островах находятся ценные материалы (эпритон и редкие растения), поэтому риск является ценой добычи.
- **Стабильность территории** — на гамма-островах рельеф под базой может изменяться другими игроками, влияя на доступ к ресурсам.
- **Проверяйте статус** — диоды на панели робота показывают текущий уровень защиты зоны во избежание случайного входа на незащищенном транспорте в опасную зону.

Уровень защиты каждой зоны указан в [индексе зон](/zones/zone-index/) (колонка *Защита*) и во всплывающих подсказках на [карте мира](/zones/map/).
"""
    ),
    "zh-CN": (
        "安全等级",
        "Alpha、Beta 与 Gamma — 每个区域的三种安全等级、权限规则以及在客户端中的识别方法。",
        """# 安全等级

每个区域都有一个安全等级：**Alpha**、**Beta** 或 **Gamma**。该等级在服务器数据库中按区域进行设置（区域的 *protected* 和 *terraformable* 标记），并决定玩家在该区域的行为规则——尤其是其他玩家是否可以攻击你，以及地形是否可以被改造。

| 等级 | 区域标记 | PvP | 凝块效应 (Blobs) | 地形改造 | 分布位置 |
|---|---|---|---|---|---|
| **Alpha** | 受保护 | 不可用 | 不生成 | 不可用 | [Alpha 岛屿](/zones/map/#alpha)、[训练区](/zones/zone-training/)、据点要塞、[PvP 竞技场](/zones/zone-pvp-arena/) |
| **Beta** | 开放、标准地形 | 开放 | 生效 | 不可用 | [Alpha 岛屿](/zones/map/#alpha)的 PvP 镜像岛以及 Gamma 带 |
| **Gamma** | 开放、可改造地形 | 开放 | 生效 | 可用 | 三大星系的跃迁门岛屿与边境带 |

## Alpha — 受保护区域

在 Alpha 区域中，玩家之间**无法互相造成伤害**：针对其他玩家的进攻性武器会被禁用，战斗中的伤害叠加效应（凝块）也不会形成。这里是安全的经济区：采矿与采集植物无需时刻提防袭击。训练区、三个新手岛及其 PvE 镜像岛、据点要塞以及 PvP 竞技场均采用 Alpha 规则。

在客户端中，Alpha 区域会在机体状态栏上显示**蓝色二极管指示灯**。

## Beta — 开放 PvP、标准地形

Beta 区域是具备标准地形的完全开放 PvP 岛屿：你可能随时受到攻击，凝块效应完全生效，岛屿地面保持服务器生成的原貌——玩家无法改造地形。新手岛的 PvP 镜像岛以及边境带的枢纽中转区均为 Beta 等级。

在客户端中，Beta 区域会在机体状态栏上显示**橙色二极管指示灯**。

## Gamma — 开放 PvP、可改造地形

Gamma 区域在 Beta 区域的基础上增加了一项核心特性：**地形可被改造**。装备地形改造工具的玩家可以重塑地面——挖掘、平整并改变岛屿表面，从而改变矿点、植物和基地的布局位置。三大星系的八座跃迁门岛屿和边境带岛屿均为 Gamma 等级。

在客户端中，Gamma 区域会在区域名称上下方显示**黄色条纹标记**。

## 玩家注意事项

- **风险预算** — Alpha 区域零安全风险；Beta 和 Gamma 区域面临完全的 PvP 风险。请根据风险合理规划燃料、护航和维修能力。
- **收益与风险并存** — 开放岛屿出产更稀有的高价值物资（如 Epriton 矿石与高级植物），高收益对应着高风险。
- **地形稳定性** — 在 Gamma 岛屿上，基地所在的地形可能因其他玩家的地形改造而发生改变，进而影响资源供给。
- **进入前确认** — 机体状态栏上的指示灯会标明当前区域的安全等级；看清指示灯是避免驾驶无武装运输舰误入危险区域的关键。

每个区域的安全等级均在[区域索引](/zones/zone-index/)（*保护等级*列）和[世界地图](/zones/map/)的悬浮提示中列出。
"""
    ),
    "zh-TW": (
        "安全等級",
        "Alpha、Beta 與 Gamma — 每個區域的三種安全等級、權限規則以及在客戶端中的識別方法。",
        """# 安全等級

每個區域都有一個安全等級：**Alpha**、**Beta** 或 **Gamma**。該等級在伺服器資料庫中按區域進行設置（區域的 *protected* 和 *terraformable* 標記），並決定玩家在該區域的行為規則——尤其是其他玩家是否可以攻擊你，以及地形是否可以被改造。

| 等級 | 區域標記 | PvP | 凝塊效應 (Blobs) | 地形改造 | 分布位置 |
|---|---|---|---|---|---|
| **Alpha** | 受保護 | 不可用 | 不生成 | 不可用 | [Alpha 島嶼](/zones/map/#alpha)、[訓練區](/zones/zone-training/)、據點要塞、[PvP 競技場](/zones/zone-pvp-arena/) |
| **Beta** | 開放、標準地形 | 開放 | 生效 | 不可用 | [Alpha 島嶼](/zones/map/#alpha)的 PvP 鏡像島以及 Gamma 帶 |
| **Gamma** | 開放、可改造地形 | 開放 | 生效 | 可用 | 三大星系的躍遷門島嶼與邊境帶 |

## Alpha — 受保護區域

在 Alpha 區域中，玩家之間**無法互相造成傷害**：針對其他玩家的進攻性武器會被禁用，戰鬥中的傷害疊加效應（凝塊）也不會形成。這裡是安全的經濟區：採礦與採集植物無需時刻提防襲擊。訓練區、三個新手島及其 PvE 鏡像島、據點要塞以及 PvP 競技場均採用 Alpha 規則。

在客戶端中，Alpha 區域會在機體狀態欄上顯示**藍色二極管指示燈**。

## Beta — 開放 PvP、標準地形

Beta 區域是具備標準地形的完全開放 PvP 島嶼：你可能隨時受到攻擊，凝塊效應完全生效，島嶼地面保持伺服器生成的原貌——玩家無法改造地形。新手島的 PvP 鏡像島以及邊境帶的樞紐中轉區均為 Beta 等級。

在客戶端中，Beta 區域會在機體狀態欄上顯示**橙色二極管指示燈**。

## Gamma — 開放 PvP、可改造地形

Gamma 區域在 Beta 區域的基礎上增加了一項核心特性：**地形可被改造**。裝備地形改造工具的玩家可以重塑地面——挖掘、平整並改變島嶼表面，從而改變礦點、植物和基地的佈局位置。三大星系的八座躍遷門島嶼和邊境帶島嶼均為 Gamma 等級。

在客戶端中，Gamma 區域會在區域名稱上下方顯示**黃色條紋標記**。

## 玩家注意事項

- **風險預算** — Alpha 區域零安全風險；Beta 和 Gamma 區域面臨完全的 PvP 風險。請根據風險合理規劃燃料、護航和維修能力。
- **收益與風險並存** — 開放島嶼出產更稀有的高價值物資（如 Epriton 礦石與高級植物），高收益對應著高風險。
- **地形穩定性** — 在 Gamma 島嶼上，基地所在的地形可能因其他玩家的地形改造而發生改變，進而影響資源供給。
- **進入前確認** — 機体狀態欄上的指示燈會標明當前區域的安全等級；看清指示燈是避免駕駛無武裝運輸艦誤入危險區域的關鍵。

每個區域的安全等級均在[區域索引](/zones/zone-index/)（*保護等級*列）和[世界地圖](/zones/map/)的懸浮提示中列出。
"""
    ),
}

ZONES_INDEX_DATA = {
    "cs": (
        "Zóny",
        "Jak vznikají zdroje v zónách: rudné žíly, populace rostlin a příklady skutečných zón.",
        """# Zóny

**Zóna** je 2D dlaždicová mapa (obvykle 2048×2048), kde roboti shromažďují suroviny. Každá zóna má dva systémy zdrojů, které server spravuje automaticky:

- **Ložiska rudy** — rozptýlené uzly v zemi s konečným množstvím materiálu na dlaždici. Po vytěžení pod stanovenou mez je uzel odstraněn a na jiném místě vznikne nový.
- **Rostliny** — živá populace, která roste, plodí a šíří se po dlaždicích, udržovaná poblíž cílové **úrodnosti zóny**.

Tato sekce vysvětluje tyto mechanismy a představuje skutečné zóny jako praktické příklady.

| Stránka | Obsah |
|---|---|
| [Mapa](/zones/map/) | Všechny zóny na souřadnicové síti serveru, barevně rozlišené podle galaxie, se známými spoji riftových bran |
| [Úrovně ochrany](/zones/protection/) | Úrovně ochrany alpha, beta a gamma, pravidla PvP, diodové značky a teraformace |
| [Generování](/zones/generation/) | Pravidla: jak se tvoří, rostou a obnovují rudné uzly a populace rostlin |
| [Index zón](/zones/zone-index/) | Každá zóna: typ, ochrana, úrodnost, počet druhů rostlin, konfigurace rud |
| [New Virginia](/zones/zone-tm/) | Příklad — chráněná startovní PvE zóna (3 druhy rudy, základní rostliny) |
| [Daoden](/zones/zone-asi/) | Příklad — otevřená PvP zóna úrovně alpha (8 druhů rud vč. vzácné rudy flux, bohatá flóra) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Příklad — PvP zóna vysoké úrovně (méně uzlů rudy, nízká úrodnost, rostliny 2. úrovně) |

Herní mechaniky těžby a sklizně z pohledu hráče najdete v sekci [Získávání zdrojů](/features/gathering/); tabulky výtěžnosti rud a rostlin jsou v sekci [Obsah](/content/).
"""
    ),
    "de": (
        "Zonen",
        "Wie Zonenressourcen generiert werden: Erzvorkommen, Pflanzenpopulationen und Praxisbeispiele realer Zonen.",
        """# Zonen

Eine **Zone** ist eine 2D-Kachelkarte (meist 2048×2048), auf der Roboter Ressourcen sammeln. Jede Zone verfügt über zwei Ressourcensysteme, die der Server automatisch verwaltet:

- **Erzvorkommen** — verstreute Knoten im Boden mit einer begrenzten Materialmenge pro Kachel. Unterhalb eines Schwellenwerts abgebaut, wird ein Knoten entfernt und an anderer Stelle neu generiert.
- **Pflanzen** — eine lebende Population, die wächst, Früchte trägt und sich Kachel für Kachel ausbreitet, gehalten nahe einem zonenspezifischen **Fruchtbarkeitsziel**.

Dieser Abschnitt erklärt die Mechaniken und zeigt reale Zonen als Praxisbeispiele.

| Seite | Inhalt |
|---|---|
| [Karte](/zones/map/) | Alle Zonen auf dem x/y-Raster des Servers, farblich nach Galaxie geordnet, mit den bekannten Riss-Tor-Verbindungen |
| [Schutzstufen](/zones/protection/) | Alpha-, Beta- und Gamma-Schutzstufen, PvP-Regeln, Dioden-Markierungen und Terraforming |
| [Generierung](/zones/generation/) | Die Regeln: wie Erzknoten und Pflanzenpopulationen entstehen, wachsen und ersetzt werden |
| [Zonenindex](/zones/zone-index/) | Jede Zone: Typ, Schutz, Fruchtbarkeit, Pflanzenartenanzahl, Erzkonfiguration |
| [New Virginia](/zones/zone-tm/) | Praxisbeispiel — eine geschützte PvE-Starterzone (3 Erzarten, Basispflanzen) |
| [Daoden](/zones/zone-asi/) | Praxisbeispiel — eine offene PvP-Alpha-Zone (8 Erzarten inkl. seltenem Flux-Erz, reichhaltige Flora) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Praxisbeispiel — eine hochstufige PvP-Zone (reduzierte Erzknoten, geringe Fruchtbarkeit, Rang-2-Pflanzen) |

Spielerbezogene Abbaumechaniken finden Sie unter [Ressourcengewinnung](/features/gathering/); Ertragsübersichten für Erze und Pflanzen unter [Inhalt](/content/).
"""
    ),
    "es": (
        "Zonas",
        "Cómo se generan los recursos de las zonas: yacimientos de mineral, poblaciones de plantas y ejemplos de zonas reales.",
        """# Zonas

Una **zona** es un mapa 2D de cuadrículas (habitualmente 2048×2048) donde los robots recolectan recursos. Cada zona cuenta con dos sistemas de recursos gestionados automáticamente por el servidor:

- **Yacimientos de mineral** — nodos dispersos en el suelo con una cantidad finita de material por casilla. Al agotarse por debajo del umbral, el nodo se elimina y se genera uno nuevo en otro lugar.
- **Plantas** — una población viva que crece, da frutos y se propaga casilla a casilla, manteniéndose cerca del **objetivo de fertilidad** de la zona.

Esta sección explica las mecánicas y muestra zonas reales como ejemplos prácticos.

| Página | Contenido |
|---|---|
| [Mapa](/zones/map/) | Todas las zonas trazadas en la cuadrícula x/y del servidor, coloreadas por galaxia, con las conexiones de portales conocidas |
| [Niveles de protección](/zones/protection/) | Niveles alfa, beta y gamma, reglas de PvP, indicadores de diodos y terraformación |
| [Generación](/zones/generation/) | Las reglas: cómo se crean, crecen y sustituyen los nodos de mineral y las poblaciones vegetales |
| [Índice de zonas](/zones/zone-index/) | Cada zona: tipo, protección, fertilidad, especies de plantas, configuración de minerales |
| [New Virginia](/zones/zone-tm/) | Ejemplo práctico — zona inicial PvE protegida (3 tipos de mineral, plantas básicas) |
| [Daoden](/zones/zone-asi/) | Ejemplo práctico — zona PvP alfa abierta (8 tipos de mineral incl. flux raro, flora rica) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Ejemplo práctico — zona PvP de alto nivel (menos nodos de mineral, baja fertilidad, plantas tier 2) |

Las mecánicas de recolección para jugadores se encuentran en [Recolección de recursos](/features/gathering/); las tablas de rendimiento de minerales y plantas están en [Contenido](/content/).
"""
    ),
    "fr": (
        "Zones",
        "Comment les ressources de zone sont générées : gisements de minerai, flore et exemples de zones réelles.",
        """# Zones

Une **zone** est une carte 2D de cases (généralement 2048×2048) où les robots récoltent des ressources. Chaque zone dispose de deux systèmes de ressources gérés automatiquement par le serveur :

- **Gisements de minerai** — nœuds dispersés dans le sol avec une quantité finie de matière par case. Épuisé sous un seuil, le nœud disparaît et un nouveau réapparaît ailleurs.
- **Plantes** — une population vivante qui croît, fructifie et se propage de case en case, maintenue proche de l'**objectif de fertilité** de la zone.

Cette section détaille ces mécanismes et présente des zones réelles en exemples concrets.

| Page | Contenu |
|---|---|
| [Carte](/zones/map/) | Toutes les zones tracées sur la grille x/y du serveur, colorées par galaxie, avec les liaisons de portails connues |
| [Niveaux de protection](/zones/protection/) | Niveaux alpha, bêta et gamma, règles PvP, diodes d'état et terraformation |
| [Génération](/zones/generation/) | Les règles : création, croissance et remplacement des nœuds de minerai et de la végétation |
| [Index des zones](/zones/zone-index/) | Chaque zone : type, protection, fertilité, nombre d'espèces végétales, minerais |
| [New Virginia](/zones/zone-tm/) | Exemple concret — zone de départ PvE protégée (3 types de minerai, flore basique) |
| [Daoden](/zones/zone-asi/) | Exemple concret — zone PvP alpha ouverte (8 types de minerai dont flux rare, flore abondante) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Exemple concret — zone PvP de haut niveau (gisements réduits, faible fertilité, flore T2) |

Les mécaniques de récolte côté joueur sont détaillées dans [Collecte de ressources](/features/gathering/) ; les tables de statistiques se trouvent dans [Contenu](/content/).
"""
    ),
    "it": (
        "Zone",
        "Come vengono generate le risorse delle zone: giacimenti minerari, popolazioni di piante ed esempi pratici di zone reali.",
        """# Zone

Una **zona** è una mappa 2D a caselle (solitamente 2048×2048) in cui i robot raccolgono risorse. Ogni zona dispone di due sistemi di risorse gestiti automaticamente dal server:

- **Giacimenti di minerali** — nodi sparsi nel terreno con una quantità finita di materiale per casella. Una volta esaurito sotto una certa soglia, il nodo viene rimosso e ne viene generato uno nuovo altrove.
- **Piante** — una popolazione vivente che cresce, produce frutti e si diffonde di casella in casella, mantenuta vicino a un **obiettivo di fertilità** specifico per la zona.

Questa sezione illustra le meccaniche e presenta zone reali come esempi pratici.

| Pagina | Contenuto |
|---|---|
| [Mappa](/zones/map/) | Tutte le zone tracciate sulla griglia x/y del server, colorate per galassia, con i collegamenti dei portali noti |
| [Livelli di protezione](/zones/protection/) | Livelli alpha, beta e gamma, regole PvP, diodi di stato e terraformazione |
| [Generazione](/zones/generation/) | Le regole: come vengono creati, crescono e si rinnovano i nodi minerari e la flora |
| [Indice delle zone](/zones/zone-index/) | Tutte le zone: tipo, protezione, fertilità, specie vegetali, configurazione mineraria |
| [New Virginia](/zones/zone-tm/) | Esempio pratico — zona iniziale PvE protetta (3 tipi di minerale, piante base) |
| [Daoden](/zones/zone-asi/) | Esempio pratico — zona PvP alpha aperta (8 tipi di minerali incl. raro flux, ricca vegetazione) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Esempio pratico — zona PvP di alto livello (nodi ridotti, bassa fertilità, flora tier 2) |

Le meccaniche di estrazione e raccolta per i giocatori sono spiegate in [Raccolta risorse](/features/gathering/); le tabelle di resa sono disponibili in [Contenuti](/content/).
"""
    ),
    "ja": (
        "ゾーン",
        "ゾーン資源の生成メカニズム：鉱床、植物の生息数、および実在ゾーンの実例。",
        """# ゾーン

**ゾーン**とは、ロボットが資源を採集する2Dタイルマップ（通常2048×2048）です。各ゾーンには、サーバーが自動管理する2つの資源システムが存在します。

- **鉱床** — 1タイルあたり有限の資源量を持つ地中のノード。閾値を下回るまで採掘されるとノードは消滅し、別の場所に新しいノードが生成されます。
- **植物** — タイルごとに成長、結実、拡散する生命群落であり、ゾーンごとの**目標肥沃度**付近に維持されます。

本セクションではこれらのメカニズムを解説し、実際のゾーンを実例として紹介します。

| ページ | 内容 |
|---|---|
| [マップ](/zones/map/) | サーバーのx/yグリッド上に配置された全ゾーン、銀河別の色分け、既知のリフトゲート接続 |
| [保護レベル](/zones/protection/) | アルファ、ベータ、ガンマの保護レベル、PvPルール、ダイオード表示、テラフォーミング |
| [生成](/zones/generation/) | 鉱床ノードと植物群落の生成、成長、置換に関するルール |
| [ゾーン一覧](/zones/zone-index/) | 全ゾーン：種類、保護、肥沃度、植物種数、鉱石構成 |
| [New Virginia](/zones/zone-tm/) | 実例 — 保護された初心者向けPvEゾーン（鉱石3種、基本植物） |
| [Daoden](/zones/zone-asi/) | 実例 — 開放型PvPアルファ層ゾーン（レアなフラックス鉱を含む鉱石8種、豊富な植物） |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | 実例 — 高層PvPゾーン（鉱床削減、低肥沃度、Tier-2植物） |

採掘・収穫メカニズムは[資源採集](/features/gathering/)を、各鉱石や植物の収量データは[コンテンツ](/content/)を参照してください。
"""
    ),
    "ko": (
        "구역",
        "구역 자원 생성 방식: 광석 광맥, 식물 군락, 실제 구역 사례 연구.",
        """# 구역

**구역(Zone)**은 로봇이 자원을 채집하는 2D 타일 맵(기본 2048×2048)입니다. 모든 구역에는 서버가 자동으로 관리하는 두 가지 자원 시스템이 있습니다.

- **광석 매장지** — 타일당 유한한 양의 자원을 가진 지중 노드입니다. 임계값 이하로 채굴되면 노드가 제거되고 다른 위치에 새 노드가 생성됩니다.
- **식물** — 타일 단위로 성장하고 열매를 맺으며 번식하는 생명체 군락으로, 구역별 **비옥도 목표치**에 맞춰 유지됩니다.

이 섹션에서는 관련 메커니즘을 설명하고 실제 구역의 사례를 다룹니다.

| 페이지 | 내용 |
|---|---|
| [지도](/zones/map/) | 서버의 x/y 좌표계에 표시된 모든 구역, 은하별 색상 구분, 리프트 게이트 연결 경로 |
| [보호 수준](/zones/protection/) | 알파, 베타, 감마 보호 수준, PvP 규칙, 다이오드 표시, 테라포밍 |
| [생성](/zones/generation/) | 광석 노드 및 식물 군락의 생성, 성장, 재생성 규칙 |
| [구역 색인](/zones/zone-index/) | 모든 구역: 유형, 보호, 비옥도, 식물 종 수, 광석 구성 |
| [New Virginia](/zones/zone-tm/) | 사례 연구 — 안전한 초보자 PvE 구역 (3가지 광석, 기본 식물) |
| [Daoden](/zones/zone-asi/) | 사례 연구 — 개방형 PvP 알파 구역 (희귀 플럭스 포함 8가지 광석, 풍부한 식물) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | 사례 연구 — 고티어 PvP 구역 (광석 노드 감소, 낮은 비옥도, 2티어 식물) |

플레이어의 채굴 및 수확 메커니즘은 [자원 채집](/features/gathering/)에서 확인할 수 있으며, 자원별 세부 수치는 [콘텐츠](/content/)를 참조하세요.
"""
    ),
    "nl": (
        "Zones",
        "Hoe zonebronnen worden gegenereerd: ertsafzettingen, plantenpopulaties en praktijkvoorbeelden van echte zones.",
        """# Zones

Een **zone** is een 2D-tegelkaart (meestal 2048×2048) waar robots grondstoffen verzamelen. Elke zone beschikt over twee bronsystemen die de server automatisch beheert:

- **Ertsafzettingen** — verspreide knooppunten in de grond met een eindige hoeveelheid materiaal per tegel. Beneden een drempelwaarde ontgonnen, verdwijnt het knooppunt en ontstaat elders een nieuwe.
- **Planten** — een levende populatie die groeit, vrucht draagt en zich tegel voor tegel verspreidt, dicht bij het **vruchtbaarheidsdoel** van de zone gehouden.

Dit gedeelte legt de mechanismen uit en toont echte zones als praktijkvoorbeelden.

| Pagina | Inhoud |
|---|---|
| [Kaart](/zones/map/) | Alle zones uitgezet op het x/y-rooster van de server, gekleurd per melkwegstelsel, met bekende poortverbindingen |
| [Beschermingsniveaus](/zones/protection/) | Alpha-, beta- en gamma-beschermingsniveaus, PvP-regels, diodemarkeringen en terraforming |
| [Generatie](/zones/generation/) | De regels: hoe ertsknooppunten en plantenpopulaties ontstaan, groeien en worden vervangen |
| [Zone-index](/zones/zone-index/) | Elke zone: type, bescherming, vruchtbaarheid, aantal plantensoorten, ertsconfiguratie |
| [New Virginia](/zones/zone-tm/) | Praktijkvoorbeeld — een beschermde PvE-starterszone (3 ertssoorten, basisgewassen) |
| [Daoden](/zones/zone-asi/) | Praktijkvoorbeeld — een open PvP-alpha-zone (8 ertssoorten incl. zeldzaam flux, rijke flora) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Praktijkvoorbeeld — een hoogwaardige PvP-zone (minder ertsknooppunten, lage vruchtbaarheid, tier-2 gewassen) |

Mijn- en oogstmechanieken voor spelers vindt u in [Grondstoffen verzamelen](/features/gathering/); opbrengsttabellen in [Inhoud](/content/).
"""
    ),
    "pl": (
        "Strefy",
        "Jak generowane są zasoby stref: złoża rudy, populacje roślin oraz przykłady rzeczywistych stref.",
        """# Strefy

**Strefa** to dwuwymiarowa mapa kafelkowa (zwykle 2048×2048), w której roboty gromadzą surowce. Każda strefa posiada dwa systemy zasobów zarządzane automatycznie przez serwer:

- **Złoża rudy** — rozproszone węzły w ziemi ze skończoną ilością materiału na kafelek. Po wyczerpaniu poniżej progu węzeł znika, a w innym miejscu powstaje nowy.
- **Rośliny** — żywa populacja, która rośnie, owocuje i rozprzestrzenia się kafel po kafelku, utrzymywana w pobliżu docelowej **żyzności strefy**.

W tej sekcji wyjaśniono mechanikę działania tych systemów oraz przedstawiono rzeczywiste strefy jako przykłady.

| Strona | Zawartość |
|---|---|
| [Mapa](/zones/map/) | Wszystkie strefy naniesione na siatkę x/y serwera, oznaczone kolorami według galaktyki, ze znanymi połączeniami wrót |
| [Poziomy ochrony](/zones/protection/) | Poziomy ochrony alpha, beta i gamma, reguły PvP, wskaźniki diodowe i terraformowanie |
| [Generowanie](/zones/generation/) | Zasady: jak węzły rudy i roślinność powstają, rosną i odnawiają się |
| [Indeks stref](/zones/zone-index/) | Każda strefa: typ, ochrona, żyzność, liczba gatunków roślin, konfiguracja rud |
| [New Virginia](/zones/zone-tm/) | Przykład — bezpieczna strefa startowa PvE (3 rodzaje rudy, podstawowe rośliny) |
| [Daoden](/zones/zone-asi/) | Przykład — otwarta strefa PvP poziomu alpha (8 rodzajów rud w tym rzadki flux, bogata flora) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Przykład — zaawansowana strefa PvP (zredukowane węzły rudy, niska żyzność, rośliny tieru 2) |

Mechaniki wydobycia i zbiorów opisano w sekcji [Zbieranie surowców](/features/gathering/); tabele wydajności w sekcji [Zawartość](/content/).
"""
    ),
    "pt": (
        "Zonas",
        "Como os recursos das zonas são gerados: depósitos minerais, populações de plantas e exemplos práticos de zonas reais.",
        """# Zonas

Uma **zona** é um mapa 2D em grade (geralmente 2048×2048) onde os robôs coletam recursos. Cada zona possui dois sistemas de recursos mantidos automaticamente pelo servidor:

- **Depósitos minerais** — nós dispersos no solo com quantidade finita de material por ladrilho. Minerado abaixo do limite, o nó é removido e um novo é gerado em outro local.
- **Plantas** — uma população viva que cresce, frutifica e se espalha ladrilho a ladrilho, mantida próxima da **meta de fertilidade** da zona.

Esta seção explica a mecânica e apresenta zonas reais como exemplos práticos.

| Página | Conteúdo |
|---|---|
| [Mapa](/zones/map/) | Todas as zonas plotadas na grade x/y do servidor, coloridas por galáxia, com conexões de portais conhecidas |
| [Níveis de proteção](/zones/protection/) | Níveis alfa, beta e gama, regras de PvP, marcadores de diodos e terraformação |
| [Geração](/zones/generation/) | As regras: como os nós de minério e populações vegetais são criados, crescem e se renovam |
| [Índice de zonas](/zones/zone-index/) | Cada zona: tipo, proteção, fertilidade, espécies de plantas, minérios |
| [New Virginia](/zones/zone-tm/) | Exemplo prático — zona inicial PvE protegida (3 tipos de minério, plantas básicas) |
| [Daoden](/zones/zone-asi/) | Exemplo prático — zona PvP alfa aberta (8 tipos de minério incl. flux raro, flora rica) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Exemplo prático — zona PvP de alto nível (menos nós de minério, baixa fertilidade, plantas tier 2) |

As mecânicas de mineração e colheita estão em [Coleta de recursos](/features/gathering/); tabelas de rendimento em [Conteúdo](/content/).
"""
    ),
    "ru": (
        "Зоны",
        "Как генерируются ресурсы зон: залежи руды, популяции растений и примеры реальных зон.",
        """# Зоны

**Зона** — это двухмерная тайловая карта (обычно 2048×2048), на которой роботы добывают ресурсы. В каждой зоне действуют две системы ресурсов, автоматически поддерживаемые сервером:

- **Залежи руды** — разрозненные узлы в грунте с ограниченным запасом материала на тайл. При выработке ниже порога узел удаляется, а новый появляется в другом месте.
- **Растения** — живая популяция, которая растет, плодоносит и распространяется по тайлам, удерживаясь около **целевого уровня плодородия** зоны.

В этом разделе описываются правила генерации и приводятся практические примеры зон.

| Страница | Описание |
|---|---|
| [Карта](/zones/map/) | Все зоны на координатной сетке сервера с разбивкой по галактикам и связями врат |
| [Уровни защиты](/zones/protection/) | Уровни защиты альфа, бета и гамма, правила PvP, индикаторы диодов и терраформирование |
| [Генерация](/zones/generation/) | Правила: создание, рост и возобновление рудных узлов и флоры |
| [Индекс зон](/zones/zone-index/) | Полный перечень: тип, защита, плодородие, виды растений, рудная конфигурация |
| [New Virginia](/zones/zone-tm/) | Пример — защищенная стартовая PvE-зона (3 вида руды, базовые растения) |
| [Daoden](/zones/zone-asi/) | Пример — открытая альфа-зона PvP (8 видов руды включая редкий флюкс, богатая флора) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Пример — зона PvP высокого уровня (меньше рудных узлов, низкое плодородие, растения 2-го ранга) |

Механика добычи для игроков изложена в разделе [Сбор ресурсов](/features/gathering/); таблицы характеристик руд и растений — в разделе [Контент](/content/).
"""
    ),
    "zh-CN": (
        "区域",
        "区域资源的生成机制：矿点分布、植被群落与真实区域案例。",
        """# 区域

**区域 (Zone)** 是一个 2D 网格地图（通常为 2048×2048），机器人在其中采集各类资源。服务器为每个区域自动维护两大资源生态系统：

- **矿点沉积** — 分布在地下的矿石节点，每个地块拥有有限的矿石储量。当开采量低于阈值时，节点会被移除并在其他位置重新生成。
- **植被群落** — 逐格生长、结果和扩散的活体植物群落，服务器会将其数量维持在区域**肥沃度目标值**附近。

本节将详细阐述这些机制，并结合具体区域进行案例分析。

| 页面 | 内容概要 |
|---|---|
| [地图](/zones/map/) | 服务器 x/y 坐标系上的所有区域，按星系色彩分类，标注已知的跃迁裂隙门连接 |
| [安全等级](/zones/protection/) | Alpha、Beta 和 Gamma 安全等级、PvP 规则、二极管状态指示灯与地形改造 |
| [生成机制](/zones/generation/) | 规则：矿点与植被群落的生成、生长和更替机制 |
| [区域索引](/zones/zone-index/) | 所有区域概览：类型、安全等级、肥沃度、植被种类数与矿物配置 |
| [New Virginia](/zones/zone-tm/) | 案例分析 — 受保护的初始 PvE 区域（3 种矿石、基础植被） |
| [Daoden](/zones/zone-asi/) | 案例分析 — 开放 PvP 的 Alpha 等级区域（8 种矿石包括稀有 Flux 矿、丰富植物） |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | 案例分析 — 高等级 PvP 区域（矿点减少、低肥沃度、二阶植物） |

玩家采矿与采伐的具体操作指南请参阅[资源采集](/features/gathering/)；各矿石与植物的详细属性数据请参阅[游戏内容](/content/)。
"""
    ),
    "zh-TW": (
        "區域",
        "區域資源的生成機制：礦點分佈、植被群落與真實區域案例。",
        """# 區域

**區域 (Zone)** 是一個 2D 網格地圖（通常為 2048×2048），机器人在其中採集各類資源。伺服器為每個區域自動維護兩大資源生態系統：

- **礦點沉積** — 分佈在地下的礦石節點，每個地塊擁有有限的礦石儲量。當開採量低於閾值時，節點會被移除並在其他位置重新生成。
- **植被群落** — 逐格生長、結果和擴散的活體植物群落，伺服器會將其數量維持在區域**肥沃度目標值**附近。

本節將詳細闡述這些機制，並結合具體區域進行案例分析。

| 頁面 | 內容概要 |
|---|---|
| [地圖](/zones/map/) | 伺服器 x/y 座標系上的所有區域，按星系色彩分類，標註已知的躍遷裂隙門連接 |
| [安全等級](/zones/protection/) | Alpha、Beta 和 Gamma 安全等級、PvP 規則、二極管狀態指示燈與地形改造 |
| [生成機制](/zones/generation/) | 規則：礦點與植被群落的生成、生長和更替機制 |
| [區域索引](/zones/zone-index/) | 所有區域概覽：類型、安全等級、肥沃度、植被種類數與礦物配置 |
| [New Virginia](/zones/zone-tm/) | 案例分析 — 受保護的初始 PvE 區域（3 種礦石、基礎植被） |
| [Daoden](/zones/zone-asi/) | 案例分析 — 開放 PvP 的 Alpha 等級區域（8 種礦石包括稀有 Flux 礦、豐富植物） |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | 案例分析 — 高等級 PvP 區域（礦點減少、低肥沃度、二階植物） |

玩家採礦與採伐的具體操作指南請參閱[資源採集](/features/gathering/)；各礦石與植物的詳細屬性數據請參閱[遊戲內容](/content/)。
"""
    ),
}
