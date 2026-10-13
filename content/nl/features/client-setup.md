---
title: "Client- en PC-instellingen"
description: "De client draaien op Windows en Linux, multi-boxing binnen de regels, UI-schaalvergroting en starten zonder beheerdersrechten."
weight: 24
---

# Client- en PC-instellingen

Praktische tips voor het draaien van de Perpetuum-client.

## Eerst de regels

Multi-boxing (meerdere clients die meerdere personages besturen) is toegestaan
**binnen bepaalde grenzen**. Fair-playregels om te kennen voordat je het doet:

- **Geen automatisering of multi-client besturingssoftware** — nooit.
- **Niet meer dan 5 gelijktijdig actieve accounts.**
- Geen accounts geregistreerd met neppe, ongeldige of onbereikbare e-mailadressen —
  het adres moet van jou zijn.

Schendingen kunnen leiden tot een onmiddellijke, permanente ban.

## Windows: meerdere clients

1. Installeer de Perpetuum Steam-client.
2. Controleer of de spelmap een `steam_appid.txt` bevat met als inhoud
   `223410`.
3. Kopieer de volledige `Perpetuum`-map één keer per extra client.
4. Voer `Perpetuum.exe` uit in elke kopie (optioneel: voeg de kopies toe aan
   Steam als niet-Steam-spellen).

**Schijfruimte:** `Layers.gbf` en `Perpetuum.gbf` zijn groot en identiek in
elke kopie — maak er symbolische koppelingen (`mklink`) of snelkoppelingen van
zodat ze maar één keer worden opgeslagen.

## Linux: meerdere clients

Elke clientkopie heeft een **andere Proton-versie** nodig, anders weigert deze
te starten:

1. Installeer Steam en Perpetuum zoals gebruikelijk; controleer
   `steam_appid.txt` (`223410`).
2. Kopieer de `Perpetuum`-map per client.
3. Log in op Steam en installeer enkele recente Proton-versies (via Steam,
   handmatig, of GloriousEggroll-builds).
4. Voeg elke kopie toe aan Steam als niet-Steam-spel dat wijst naar de
   bijbehorende `Perpetuum.exe`.
5. Forceer per kopie een **andere Proton-versie** in de startopties.
6. Start eerst de echte Steam-app, start daarna de kopies.

Probleemoplossing:

- Het selecteren van een Proton-versie installeert deze **niet** — je moet het
  spel een keer starten met die versie geselecteerd.
- Als de echte Steam-app niet wil starten, start deze dan eerst in de veilige
  modus.
- Sinds Proton 5.0 draait de DirectX 9/12-emulatie op **Vulkan**. Geen GPU met
  Vulkan-ondersteuning? Voeg `PROTON_USE_WINED3D=1 %command%` toe aan de
  startopties van elke kopie.
- Leeg tekstveld met een rode waarschuwing: installeer `libfreetype6:i386`
  (Debian/Ubuntu-gebaseerde distributies).

## UI-schaalvergroting

De client gebruikt een UI met vaste pixels zonder dynamische schaalvergroting.
Werkarounds:

- **Volledig scherm met lage resolutie** — ga in volledig scherm met een lagere
  resolutie dan je beeldscherm en laat de UI uitrekken om het te vullen
  (venster- en randloze modus gebruiken altijd de native resolutie). Het
  verlagen van de resolutie van het beeldscherm zelf werkt hetzelfde.
- **UI-schaalvergroting-apps** — bijv. Lossless Scaler (Steam, Windows): draai
  de client in venstermodus op je basisgrootte, stel een aangepaste schaalfactor
  in de scaler in, activeer de schaalvergroting en focus het clientvenster.
  Verwacht de gebruikelijke afweging tussen soepelheid en scherpte van tekst.
- **OS-vergrootglas** — het Windows-vergrootglas (of equivalent) voor af en toe
  een nader lezing.

## Starten zonder beheerdersrechten

1. Kopieer de clientbestanden uit de Steam-map naar een schrijfbare locatie.
2. Maak daar een `Perpetuum.bat` met de inhoud
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Start via het batchbestand.

<!--
Ontwikkelaarsnotities: in 2026 herschreven in originele bewoordingen. Een eerdere versie was aangepast van de
Open Perpetuum community-wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); die tekst is
volledig vervangen, niet hergebruikt. Dit zijn client-side procedures voor de retail Steam-clientbuild;
niets hier is verifieerbaar vanuit de backend van deze server, en er wordt geen serverfunctie
beweerd. De Reshader (graphics mod) is bewust weggelaten: deze is bedoeld voor de
retail-clientbuild en is geen OPP-serverfunctie.
-->