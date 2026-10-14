---
title: "Pierwsze kroki"
description: "Tworzenie postaci, odbieranie robota startowego i podstawy postaci."
weight: 10
---

# Pierwsze kroki

Ta strona obejmuje pierwsze kroki: tworzenie postaci, otrzymanie pierwszego robota
oraz ustawienia na poziomie postaci, z którymi spotkasz się na początku.

> Lokalizacje w interfejsie użytkownika są opisane w [przeglądzie interfejsu klienta](/pl/features/ui/). Mechaniki poniżej zostały potwierdzone
> w implementacji serwerowej.

## Pobranie gry

Perpetuum jest dostępne za darmo na [Steam](https://store.steampowered.com/app/223410/Perpetuum/).

<div class="steam-card">
  <a class="steam-card-link" href="https://store.steampowered.com/app/223410/Perpetuum/" target="_blank" rel="noopener">
    <img src="https://cdn.akamai.steamstatic.com/steam/apps/223410/header.jpg"
         alt="Perpetuum w sklepie Steam" class="steam-card-img" width="460" height="215" loading="lazy">
    <span class="steam-card-label">Perpetuum na Steam — gra za darmo</span>
  </a>
</div>

## Najpierw obejrzyj

Poradniki od Open Perpetuum Project. Kliknij kartę, aby odtworzyć wideo tutaj.

<div class="video-grid">
  <div class="video-card" role="button" tabindex="0" aria-label="Odtwórz wideo: Perpetuum Online Tutorial Walkthrough. + Extension Advice and lots more." data-id="mHd3nOHvEuM" data-title="Perpetuum Online Tutorial Walkthrough. + Extension Advice and lots more.">
    <img src="https://i.ytimg.com/vi/mHd3nOHvEuM/hqdefault.jpg" alt="Perpetuum Online Tutorial Walkthrough. + Extension Advice and lots more."
         width="480" height="270" referrerpolicy="origin">
    <span class="video-play" aria-hidden="true">&#9654;</span>
    <div class="video-title">Perpetuum Online Tutorial Walkthrough. + Extension Advice and lots more.</div>
  </div>
  <div class="video-card" role="button" tabindex="0" aria-label="Odtwórz wideo: Syndicate Careers Help - Artifacting" data-id="lQgrO6RNBSg" data-title="Syndicate Careers Help - Artifacting">
    <img src="https://i.ytimg.com/vi/lQgrO6RNBSg/hqdefault.jpg" alt="Syndicate Careers Help - Artifacting"
         width="480" height="270" referrerpolicy="origin">
    <span class="video-play" aria-hidden="true">&#9654;</span>
    <div class="video-title">Syndicate Careers Help — Artifacting</div>
  </div>
  <div class="video-card" role="button" tabindex="0" aria-label="Odtwórz wideo: Open Perpetuum Tutorial - How to run multiple clients" data-id="sRBouSF8Gu4" data-title="Open Perpetuum Tutorial - How to run multiple clients">
    <img src="https://i.ytimg.com/vi/sRBouSF8Gu4/hqdefault.jpg" alt="Open Perpetuum Tutorial - How to run multiple clients"
         width="480" height="270" referrerpolicy="origin">
    <span class="video-play" aria-hidden="true">&#9654;</span>
    <div class="video-title">Open Perpetuum Tutorial — How to run multiple clients</div>
  </div>
</div>

<script>
    // Click-to-play: swap the thumbnail card for the YouTube embed on demand
    // (keeps the home page light until a video is actually wanted).
    (function () {
        var cards = document.querySelectorAll(".video-card");
        function activate(card) {
            if (card.querySelector("iframe")) return;
            var f = document.createElement("iframe");
            f.src = "https://www.youtube.com/embed/" + card.getAttribute("data-id") + "?autoplay=1&rel=0";
            f.title = card.getAttribute("data-title");
            f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
            f.allowFullscreen = true;
            card.innerHTML = "";
            card.appendChild(f);
            card.removeAttribute("tabindex");
            card.removeAttribute("role");
            card.removeAttribute("aria-label");
            card.style.cursor = "default";
        }
        cards.forEach(function (card) {
            card.addEventListener("click", function () { activate(card); });
            card.addEventListener("keydown", function (e) {
                if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activate(card); }
            });
        });
    })();
</script>

```mermaid
flowchart TD
    A["Utwórz postać"] --> B["Strefa tutorialu\nLista kontrolna rekruta"]
    B --> C{"Wybierz wyjście"}
    C -->|Pelistal| D1["Castel + zestaw rakietowy"]
    C -->|Nuimqol| D2["Yagel + zestaw z działem railgun"]
    C -->|Thelodica| D3["Prometheus + zestaw laserowy"]
    C -->|Industrial| D4["Argano + zestaw wydobywczy"]
    D1 --> E["Otwarty świat\nkorporacja startowa + umiejętności"]
    D2 --> E
    D3 --> E
    D4 --> E
```

## Tworzenie postaci

- Możesz **sprawdzić, czy nazwa jest wolna**, zanim ją utworzysz (`characterCheckNick`).
- **Utwórz postać** — zostanie przypisana do Twojego konta. Jedno konto może
  zawierać wiele postaci; grasz jedną naraz.
- **Wybierz postać**, aby nią grać. Przełączenie postaci odznacza bieżącą.
- Możesz później **zmienić nazwę** postaci (nazwa musi być dostępna).
- Możesz **usunąć** postać, której już nie używasz.

## Twój pierwszy robot

- Gdy jesteś **dodokowany na bazie**, możesz **zlecić robota startowego** (udogodnienia
  bazy — patrz [przegląd interfejsu klienta](/pl/features/ui/), aby dowiedzieć się, gdzie
  znajdują się akcje bazy).
  - Baza musi mieć roboty startowe na stanie — na popularnych bazach mogą się
    wyczerpać, w takim przypadku zlecenie nie powiedzie się.
  - Między zleceniami robota startowego na jedną postać obowiązuje **5-minutowy cooldown**.
  - Nowy robot jest dostarczany do publicznego kontenera bazy.

- Gdy jesteś dodokowany, możesz również **zlecić „nieskończony kontener"**: specjalny
  kontener dodawany do Twojego ekwipunku za **opłatą 5 000 kredytów**. To kontener
  wygodny, a nie źródło darmowych zasobów.

## Ustawienia postaci {#character-settings}

- **Awatar** — wygląd Twojej postaci.
- **Komunikat nastroju** — krótki tekst widoczny dla innych graczy.
- **Notatka prywatna** — notatka widoczna tylko dla Ciebie na jednej z Twoich postaci.
- **Baza domowa** — ustaw lub wyczyść bazę domową; to Twoje domyślne miejsce
  dokowania, gdy gra musi Cię umieścić w bezpiecznym miejscu.
- **Ustawienia** — preferencje na poziomie postaci (get/set).
- **Blokada handlu** — włącz lub wyłącz handel dla postaci.
- **Kredyty** — przelewaj kredyty między własnymi postaciami; przeglądaj historię
  transakcji.
- **Poziom konta** — zmień e-mail/hasło sesji, przeglądaj historię transakcji konta
  oraz historię EP za aktywność.

## Wylogowanie / ponowne logowanie

- **Wylogowanie** kończy sesję; **wybór postaci** ją wznowia.
- Jeśli serwer Cię wyrzuci (np. przymusowe dodokowanie na bazie), ponownie
  pojawisz się dodokowany — patrz [ruch](/pl/features/movement/).

## Tutorial

Nowe postacie zaczynają w strefie treningowej z **Listą kontrolną rekruty** —
ukończ ją: obejmuje podstawy i wypłaca kilka robotów z modułami i amunicją.
Możesz ją pominąć (oddokuj i wejdź na wyjście frakcji), ale stracisz nagrody
i nie będziesz mógł wrócić do strefy treningowej. Co dają cztery wyjścia frakcji,
opisano w [FAQ](/pl/features/faq/).

## Przetrwanie

Perpetuum to sandbox oparty na ryzyku i nagrodzie, a gdy Twój robot ginie,
tracisz go — niezależnie od tego, czy był dodokowany, czy zabity przez gracza
lub NPC — i ponownie pojawia się na Twojej [bazie domowej](#character-settings)
(możesz tam zlecić darmowego robota startowego, jeśli przybywasz z pustymi rękami).
Kilka zasad, które sprawiają, że straty są do przeżycia:

- **Angażuj tylko to, co możesz zastąpić.** Odkowanie to zakład: jeśli robot
  zginie, on i jego zamontowane moduły przepadną (lub staną się łupem).
  Przed startem upewnij się, że taka strata jest do przeżycia.
- **Poznaj strefy.** Ochronione (PvE) wyspy są bezpieczne przed graczami;
  wyspy otwartego PvP to wolna walka bez systemu przestępstw i kar.
  Patrz [strefy](/zones/), aby zobaczyć mapę.
- **Poznaj NPC.** Pomarańczowe znaczniki atakują tylko, gdy zostaną sprowokowane;
  czerwone znaczniki atakują przy zbliżeniu. Uciekaj i przerywaj linię widzenia,
  aby stracić aggro. Patrz [NPC i łowy PvE](/pl/features/npcs/).
- **Mityguj ryzyko, nie tylko je akceptuj.** Wchodzenie na wyspę otwartego PvP
  w swoim najlepszym mechu z T4 to sposób, w jaki mechy giną. Tańszy,
  wymienny sprzęt, który się zwraca w kilka wypraw, wygrywa z drogim botem,
  który wymaga dwudziestu.
- **Zbuduj zrównoważony cykl.** Cokolwiek robisz — misje, zbieranie, łowy,
  produkcja, transport — ktoś płaci za to NIC. Trzymaj zapasowe aktywa,
  aby jeden zły dzień nie zniweczył Twojego dochodu.

## Co dalej

1. Wybierz robota startowego i poznaj ekran [hangaru i montażu](/pl/features/robots/).
2. Odkuj i rusz do strefy — patrz [ruch](/pl/features/movement/).
3. Skanuj teren i zacznij zbierać zasoby — patrz [zbieranie](/pl/features/gathering/).
4. Zbadaj swoje pierwsze rozszerzenia — patrz [badania](/pl/features/research/).
5. Wybierz karierę — [FAQ](/pl/features/faq/) ma menu.

<!-- TODO(Phase 1): verify client UI flow (account creation screen, character wizard).
     UI model: see features/ui.md (EVE-style, project-provided).
     Developer notes: Perpetuum.RequestHandlers.Characters/* (CharacterCreate,
     CharacterSelect, CharacterRename, CharacterSetHomeBase, ...);
     RequestStarterRobot (5-minute cooldown, base stock), RequestInfiniteBox
     (5000 credits, docked-only). -->