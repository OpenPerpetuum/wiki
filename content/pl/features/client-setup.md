---
title: "Konfiguracja klienta i komputera"
description: "Uruchamianie klienta na Windows i Linux, multi-boxing w ramach zasad, skalowanie interfejsu oraz uruchamianie bez uprawnień administratora."
weight: 24
---

# Konfiguracja klienta i komputera

Praktyczne wskazówki dotyczące uruchamiania klienta Perpetuum.

## Najpierw zasady

Multi-boxing (kilka klientów sterujących kilkoma postaciami) jest dozwolone
**w określonych granicach**. Zasady fair play, o których warto wiedzieć przed przystąpieniem:

- **Brak oprogramowania do automatyzacji lub sterowania wieloma klientami** — bez wyjątków.
- **Nie więcej niż 5 jednocześnie aktywnych kont.**
- Brak kont zarejestrowanych na fałszywe, nieprawidłowe lub niedostępne adresy e-mail —
  adres musi być własnością użytkownika.

Naruszenia mogą skutkować natychmiastowym, trwałym banem.

## Windows: wiele klientów

1. Zainstaluj klienta Perpetuum ze Steam.
2. Sprawdź, czy w folderze gry znajduje się plik `steam_appid.txt` o zawartości
   `223410`.
3. Skopiuj cały folder `Perpetuum` — po jednym kopii na każdego dodatkowego klienta.
4. Uruchom `Perpetuum.exe` w każdej kopii (opcjonalnie dodaj kopie do Steam jako
   gry spoza Steam).

**Miejsce na dysku:** `Layers.gbf` i `Perpetuum.gbf` są duże i identyczne w
każdej kopii — utwórz dla nich linki symboliczne (`mklink`) lub skróty, aby były
przechowywane tylko raz.

## Linux: wiele klientów

Każda kopia klienta wymaga **innego wydania Proton**, w przeciwnym razie odmówi uruchomienia:

1. Zainstaluj Steam i Perpetuum w standardowy sposób; zweryfikuj `steam_appid.txt` (`223410`).
2. Skopiuj folder `Perpetuum` dla każdego klienta.
3. Podczas zalogowania do Steam zainstaluj kilka ostatnich wydań Proton (przez Steam,
   ręcznie lub buildy GloriousEggroll).
4. Dodaj każdą kopię do Steam jako grę spoza Steam, wskazując na jej `Perpetuum.exe`.
5. Wymuś **inne wydanie Proton** dla każdej kopii w opcjach uruchamiania.
6. Najpierw uruchom właściwą aplikację Steam, a następnie uruchom kopie.

Rozwiązywanie problemów:

- Wybór wydania Proton **nie** instaluje go — należy uruchomić grę raz z wybranym
  wydaniem.
- Jeśli właściwa aplikacja Steam nie chce się uruchomić, najpierw uruchom ją w trybie awaryjnym.
- Od Proton 5.0 emulacja DirectX 9/12 działa na **Vulkan**. Brak GPU z obsługą
  Vulkan? Dodaj `PROTON_USE_WINED3D=1 %command%` do opcji uruchamiania każdej kopii.
- Puste pole tekstowe z czerwoną ostrzeżeniem: zainstaluj `libfreetype6:i386`
  (dystrybucje oparte na Debianie/Ubuntu).

## Skalowanie interfejsu

Klient używa interfejsu o stałej liczbie pikseli bez dynamicznego skalowania. Rozwiązania:

- **Pełny ekran w niskiej rozdzielczości** — przejdź w tryb pełnoekranowy w niższej
  rozdzielczości niż natywna rozdzielczość wyświetlacza i pozwól, aby interfejs rozciągnął
  się na cały ekran (tryby okienkowy i bezramkowy zawsze używają natywnej rozdzielczości).
  Obniżenie rozdzielczości samego wyświetlacza daje ten sam efekt.
- **Aplikacje do skalowania interfejsu** — np. Lossless Scaler (Steam, Windows): uruchom
  klienta w trybie okienkowym w bazowym rozmiarze, ustaw niestosunek skalowania w skalerze,
  wywołaj skalowanie i ustaw fokus na oknie klienta. Oczekuj typowego kompromisu między
  płynnością a ostrością tekstu.
- **Powiększarka systemu** — Windows Magnifier (lub odpowiednik) do okazjonalnego
  dokładnego odczytu.

## Uruchamianie bez uprawnień administratora

1. Skopiuj pliki klienta z folderu Steam do lokalizacji, w której masz uprawnienia zapisu.
2. Utwórz tam plik `Perpetuum.bat` zawierający
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Uruchom klienta przez plik wsadowy.

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->