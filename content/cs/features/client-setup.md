---
title: "Nastavení klienta a PC"
description: "Spouštění klienta na Windows a Linuxu, multi-boxing v rámci pravidel, škálování UI a spouštění bez administrátorských práv."
weight: 24
---

# Nastavení klienta a PC

Praktické poznámky ke spouštění klienta Perpetuum.

## Nejdřív pravidla

Multi-boxing (více klientů ovládajících více postav) je povoleno
**v omezeném rozsahu**. Pravidla fair play, která je třeba znát předem:

- **Žádná automatizace ani software pro ovládání více klientů** — nikdy.
- **Ne více než 5 současně aktivních účtů.**
- Žádné účty registrované s falešnou, neplatnou nebo nedostupnou e-mailovou
  adresou — adresa musí být vaše.

Porušení může znamenat okamžité a trvalé zákaz.

## Windows: více klientů

1. Nainstalujte Steam klienta Perpetuum.
2. Zkontrolujte, že složka hry obsahuje soubor `steam_appid.txt` s obsahem
   `223410`.
3. Zkopírujte celou složku `Perpetuum` jednou pro každý další klient.
4. Spusťte `Perpetuum.exe` v každé kopii (volitelně přidejte kopie do Steamu
   jako ne-Steam hry).

**Místo na disku:** `Layers.gbf` a `Perpetuum.gbf` jsou velké a v každé kopii
identické — vytvořte z nich symbolické odkazy (`mklink`) nebo zkratky, aby se
ukládaly jen jednou.

## Linux: více klientů

Každá kopie klienta potřebuje **jinou verzi Protonu**, jinak se odmítne
spustit:

1. Nainstalujte Steam a Perpetuum obvyklým způsobem; ověřte `steam_appid.txt`
   (`223410`).
2. Zkopírujte složku `Perpetuum` pro každý klient.
3. Při přihlášení do Steamu nainstalujte několik nedávných verzí Protonu
   (přes Steam, ručně, nebo buildy GloriousEggroll).
4. Přidejte každou kopii do Steamu jako ne-Steam hru ukazující na její
   `Perpetuum.exe`.
5. V spouštěcích volbách každé kopie vynuťte **jinou verzi Protonu**.
6. Nejprve spusťte skutečnou aplikaci Steam, poté spusťte kopie.

Řešení problémů:

- Vybrání verze Protonu ji **nenainstaluje** — hru je potřeba jednou spustit
  s touto verzí vybranou.
- Pokud se skutečná aplikace Steam nespustí, spusťte ji nejdřív v režimu
  Safe mode.
- Od Protonu 5.0 běží emulace DirectX 9/12 na **Vulkanu**. Nemáte GPU s
  podporou Vulkanu? Přidejte `PROTON_USE_WINED3D=1 %command%` do spouštěcích
  voleb každé kopie.
- Prázdné textové pole s červeným varováním: nainstalujte `libfreetype6:i386`
  (distribuce založené na Debianu/Ubuntu).

## Škálování UI

Klient používá UI s pevným rozlišením pixelů bez dynamického škálování.
Obcházecí řešení:

- **Celá obrazovka s nižším rozlišením** — přepněte do režimu celé obrazovky
  s nižším rozlišením než má váš displej a nechte UI natáhnout tak, aby ho
  vyplnilo (okenný a bezokrajový režim vždy používají nativní rozlišení).
  Snížení rozlišení samotného displeje dosáhne stejného efektu.
- **Aplikace pro škálování UI** — např. Lossless Scaler (Steam, Windows):
  spusťte klienta v okenném režimu ve vašem základním rozlišení, nastavte v
  škálovací aplikaci vlastní poměr škálování, spusťte škálování a zaostřte okno
  klienta. Očekávejte obvyklý kompromis mezi plynulostí a ostrostí textu.
- **Zvětšovač OS** — Windows Zvětšovač (nebo ekvivalent) pro občasné bližší
  čtení.

## Spouštění bez administrátorských práv

1. Zkopírujte soubory klienta ze složky Steamu do zápisovatelné polohy.
2. Vytvořte tam soubor `Perpetuum.bat` obsahující
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Spusťte přes batch soubor.

<!--
Poznámky pro vývojáře: přepsáno v roce 2026 originálním textem. Ranější verze byla adaptována
z komunitního wiki Open Perpetuum (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); tento text byl
zcela nahrazen, nebyl znovu použit. Jedná se o klientské postupy pro retail Steam klient;
nic z toho zde není ověřitelné z backendu tohoto serveru a není zde tvrděna žádná serverová
funkce. Reshader (grafický mod) byl záměrně vynechán: cílí na
retail klient a nejde o funkci OPP serveru.
-->