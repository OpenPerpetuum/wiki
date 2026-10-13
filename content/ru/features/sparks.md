---
title: "Искры"
description: "Искры — это наноботное воплощение вашего агента: пассивные бонусы к характеристикам, авторизация и стоимость переключения."
weight: 10
---

# Искры

**Искра** (spark) — это специализация наноботов, установленная на вашем персонаже.
Пока она активна, её бонусы действуют на каждого пилотируемого вами робота:
например, искра боевой ветки фракции повышает урон оружия и шанс критического
удара с каждым уровнем, тогда как промышленная ветка увеличивает ёмкость
ядра и объём добычи ресурсов.

У каждого персонажа есть **искра по умолчанию**, выдаваемая при создании.
Помимо неё, искры разделены по семействам: базовые начальные ветки, боевые/промышленные/социальные
ветки каждой фракции (по три уровня в каждой), платные ветки Синдиката
и особые лимитированные ветки. Точные бонусы искры представляют собой фиксированный
набор уровней навыков, с которыми можно ознакомиться на [странице расширений](/content/extensions/).
[Обзор семейств ниже](#semeistva-iskr) позволяет сразу перейти к искрам нужной категории.

## Разблокировка (авторизация) искры

Чтобы установить искру, которой у вас ещё нет, её необходимо предварительно
**разблокировать** (только на станции). В зависимости от искры сервер проверяет:

- **стоимость** в NIC (платные ветки — например, вспомогательные искры Синдиката
  и редкие специальные искры),
- **отношения (standing)** с мегакорпорацией разработчиков (фракционные ветки требуют
  минимального уровня отношений с мегакорпорацией соответствующей стороны,
  который прокачивается выполнением [миссий](/ru/features/missions/)),
- или **предмет**, изымаемый из вашего инвентаря (некоторые особые искры
  разблокируются специальным предметом-ключом).

Разблокировка производится один раз: открытая искра навсегда остаётся в вашей коллекции.

```mermaid
stateDiagram-v2
    [*] --> Active: персонаж создан (установлена искра по умолчанию)
    Active --> Active: одна искра за раз
    Active --> Cooldown: смена (стоит NIC, зависит от искры)
    Cooldown --> Active: через 1 час (бонусы новой искры применяются ко всем роботам)
```
<a id="switching-sparks"></a>

## Смена искр

- Одновременно может быть активна только **одна искра**; выбор другой заменяет текущую.
- Каждое переключение **стоит NIC** — сумма зависит от конкретной искры (обычные
  линейки стоят 10k, платные специальные — вплоть до одного миллиона).
- Между сменами действует **кулдаун в один час**: сервер фиксирует время активации
  текущей искры и запрещает переключение до истечения этого интервала.

Поскольку смена искры всегда требует затрат NIC и занимает час времени, выбирайте
ту искру, которая лучше всего подходит для занятия, отнимающего у вас больше
всего времени, и относитесь к переспециализации как к периодическому решению,
а не к действию для каждой отдельной игровой сессии.
<!-- sparkfamilies:generated -->
<a id="families"></a>

## Семейства искр

Краткий обзор 47 искр в 6 семействах: по одному блоку на каждое семейство (количество искр, способ разблокировки) в порядке добавления линеек (слева направо, сверху вниз). **Нажмите на блок, чтобы перейти к искрам соответствующего семейства ниже.** **Прокручивайте колесо мыши над схемой для масштабирования**, перетаскивайте для панорамирования и используйте кнопку ⟲ для сброса.

<div class="map-zoom-wrap sparkfam-wrap">
<button type="button" class="zoommap-reset" title="Reset the zoom">⟲</button>
<svg class="zoommap" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1008 278" width="960" height="264" role="img" aria-label="Spark families: 6 families, 47 sparks; click a family to jump to its sparks below">
  <rect x="0" y="0" width="1008" height="278" fill="#10151f" stroke="#39445a" stroke-width="1"/>
  <g><title>Event &amp; special: 9 sparks, unlocks with free</title><a href="#family-special"><rect x="24" y="40" width="300" height="84" rx="10" fill="#10151f" stroke="#c8d2e0" stroke-width="1.5"/><text x="174" y="68" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">Event &amp; special</text><text x="174" y="92" text-anchor="middle" fill="#c8d2e0" font-size="12">9 sparks · free</text></a></g>
  <g><title>TM (Truhold-Markson): 9 sparks, unlocks with TM standing</title><a href="#family-tm"><rect x="354" y="40" width="300" height="84" rx="10" fill="#10151f" stroke="#41d3ff" stroke-width="1.5"/><text x="504" y="68" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">TM (Truhold-Markson)</text><text x="504" y="92" text-anchor="middle" fill="#41d3ff" font-size="12">9 sparks · TM standing</text></a></g>
  <g><title>ICS: 9 sparks, unlocks with ICS standing</title><a href="#family-ics"><rect x="684" y="40" width="300" height="84" rx="10" fill="#10151f" stroke="#6ee7a0" stroke-width="1.5"/><text x="834" y="68" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">ICS</text><text x="834" y="92" text-anchor="middle" fill="#6ee7a0" font-size="12">9 sparks · ICS standing</text></a></g>
  <g><title>ASI: 9 sparks, unlocks with ASI standing</title><a href="#family-asi"><rect x="24" y="154" width="300" height="84" rx="10" fill="#10151f" stroke="#f5a05a" stroke-width="1.5"/><text x="174" y="182" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">ASI</text><text x="174" y="206" text-anchor="middle" fill="#f5a05a" font-size="12">9 sparks · ASI standing</text></a></g>
  <g><title>Syndicate (NIC): 5 sparks, unlocks with NIC price</title><a href="#family-syndicate"><rect x="354" y="154" width="300" height="84" rx="10" fill="#10151f" stroke="#a78bfa" stroke-width="1.5"/><text x="504" y="182" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">Syndicate (NIC)</text><text x="504" y="206" text-anchor="middle" fill="#a78bfa" font-size="12">5 sparks · NIC price</text></a></g>
  <g><title>Limited: 6 sparks, unlocks with NIC price</title><a href="#family-limited"><rect x="684" y="154" width="300" height="84" rx="10" fill="#10151f" stroke="#f472b6" stroke-width="1.5"/><text x="834" y="182" text-anchor="middle" fill="#e8eefc" font-size="15" font-weight="700">Limited</text><text x="834" y="206" text-anchor="middle" fill="#f472b6" font-size="12">6 sparks · NIC price</text></a></g>
</svg>
</div>

<a id="family-special"></a>

### Event &amp; special (9)

Разблокировка: бесплатно — это базовые начальные линейки. Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">ww</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">wi</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">ws</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">iw</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">ii</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">is</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">sw</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">si</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
<div class="ext-card">
<div class="ext-card-name">ss</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">бесплатно</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Искра по умолчанию — установлена при создании персонажа</div>
</div>
</div>

<a id="family-tm"></a>

### TM (Truhold-Markson) (9)

Разблокировка: отношения (standing) с мегакорпорацией TM (2 → 4 → 6 в зависимости от уровня). Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">Combat Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с TM</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с TM</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с TM</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с TM</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с TM</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с TM</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с TM</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с TM</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с TM</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
</div>

<a id="family-ics"></a>

### ICS (9)

Разблокировка: отношения (standing) с мегакорпорацией ICS (2 → 4 → 6 в зависимости от уровня). Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">Combat Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ICS</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ICS</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ICS</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ICS</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ICS</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ICS</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ICS</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ICS</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ICS</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
</div>

<a id="family-asi"></a>

### ASI (9)

Разблокировка: отношения (standing) с мегакорпорацией ASI (2 → 4 → 6 в зависимости от уровня). Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">Combat Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ASI</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ASI</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Combat Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ASI</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ASI</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ASI</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Indy Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ASI</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 3 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl1</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 2 с ASI</span> · смена <span class="ext-val-price">10k NIC</span></div>
<div class="ext-card-prereq">Включает 5 уровней расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl2</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 4 с ASI</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 6 уровней расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Social Lvl3</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-bonus">отношения 6 с ASI</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 6 уровней расширений</div>
</div>
</div>

<a id="family-syndicate"></a>

### Syndicate (NIC) (5)

Разблокировка: стоимость в NIC (1M за искру). Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">Syndicate Nic Combat</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">1M NIC</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Syndicate Nic Scout</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">1M NIC</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Syndicate Nic Coreboost</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">1M NIC</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Syndicate Nic Allresist</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">1M NIC</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 4 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Syndicate Nic Fitboost</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">1M NIC</span> · смена <span class="ext-val-price">100k NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
</div>

<a id="family-limited"></a>

### Limited (6)

Разблокировка: стоимость в NIC (25–50M за искру). Каждое переключение стоит NIC (сумма зависит от искры, см. карточки) и запускает часовой кулдаун — см. раздел [Смена искр](#smena-iskr) выше.

<div class="ext-cards">
<div class="ext-card">
<div class="ext-card-name">Anniversary Combat</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">25M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 6 уровней расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Anniversary Logistic</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">25M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 6 уровней расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Amazon c1 Combat</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">25M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Amazon c1 Indy</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">25M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Steam a</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">50M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
<div class="ext-card">
<div class="ext-card-name">Steam b</div>
<div class="ext-card-meta">разблокировка <span class="ext-val-price">50M NIC</span> · смена <span class="ext-val-price">1M NIC</span></div>
<div class="ext-card-prereq">Включает 2 уровня расширений</div>
</div>
</div>

<!--
Written from scratch against the server backend, 2026-09-27:
RequestHandlers/Sparks/SparkUnlock.cs (unlock rules: price, standing, item),
RequestHandlers/Sparks/SparkChange.cs + Services/Sparks/SparkHelper.cs
(60-minute switch cooldown, per-spark change price),
Services/Sparks/Spark.cs, sparks + sparkextensions tables (47 sparks, per-line
bonus bundles).
An earlier version of this page was adapted from the Open Perpetuum
community wiki (perpetuum.miraheze.org) and has been fully rewritten from
backend sources; no text was reused.
-->