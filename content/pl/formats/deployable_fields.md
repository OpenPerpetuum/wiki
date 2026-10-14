---
title: "Pola rozkładanych"
description: "Sposób identyfikacji rozkładanych, parowanie kapsuła–obiekt oraz pola agregowane sterujące obiektami umieszczonymi w strefie."
weight: 40
---

# Pola rozkładanych

**Rozkładany** to przedmiot, który można umieścić w strefie jako jednostkę (mobilne teleporty,
miny, emitery efektów pola, struktury PBS, …). Jest identyfikowany przez flagi,
parowany z definicją kapsuła↔obiekt i sterowany w czasie rzeczywistym przez pola agregowane.

## Identyfikacja

- **Flaga kategorii** `cf_deployable_structure` = `0x998` (maska bitowa) na
  `entitydefaults.categoryflags` — zbiór, który rejestr encji skanuje, aby zarejestrować
  klasy przedmiotów-wyrzutni (`EntitiesModule.cs`, np. `PlantSeedDeployer` jest zarejestrowany
  dla tej kategorii).
- **Flaga atrybutu** `deployable` = bit **23** na `entitydefaults.attributeflags`
  (maska `1 << 23`).
- Pełny katalog (ze statystykami) jest generowany w [Deployables](/content/deployables/).

## Parowanie kapsuła ↔ obiekt

Rozkładane występują parami: **kapsuła** (przedmiot noszony w ekwipunku) i
**obiekt** (jednostka pojawiająca się w strefie). Parę stanowi kolumna bazy danych
`entitydefaults.targetdefinition`, która jest **dwukierunkowa**:

- kapsuła.`targetdefinition` → definicja obiektu
- obiekt.`targetdefinition` → definicja kapsuły

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` rozwiązuje
obie kierunki. Przykład pary: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Przepływ rozkładania

`ItemDeployer.cs` (klasa bazowa dla rozkładanych innych niż PBS):

1. `Deploy(zone, player)` oblicza pozycję pojawienia się w centrum gracza.
2. `CreateDeployableItem` buduje jednostkę **obiektu** (nie kapsuły) i zapisuje ją.
3. Renderowana jest 5-sekundowa „wyrzutnia promieniowa".
4. Po zatwierdzeniu transakcji obiekt jest dodawany do strefy (`ZoneEnterType.Deploy`).

Struktury PBS korzystają z osobnej ścieżki `PBSDeployer` / `PBSObjectHelper`; gdy obiekt PBS
zostanie rozłożony, jest usuwany ze strefy, a jego **kapsuła** jest dodawana do łupów
(`PBSObjectHelper.cs`).

## Pola agregowane w czasie rzeczywistym

Te pola (z `aggregatevalues`, per definicja) sterują umieszczonym obiektem, gdy znajduje się
w strefie. Konsument jest podany.

| Pole | Znaczenie | Konsument |
|---|---|---|
| `despawn_time` | Czas życia umieszczonego obiektu, w **milisekundach**. Po upływie jednostka jest usuwana ze strefy (lub zabijana, jeśli sterowana zdalnie). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → stosuje `effect_despawn_timer`. |
| `armor_max` | Maksymalny pancerz umieszczonej jednostki. | walka jednostki |
| `resist_chemical/explosive/kinetic/thermal` | Odporności na obrażenia. | walka jednostki |
| `signature_radius` | Rozmiar sygnatury skanowania. | skaner / stealth |
| `stealth_strength` | Siła ukrycia. | skaner / stealth |
| `effect_*` (np. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modyfikatory efektów pola emitowane przez obiekt. | `FieldEffectGenerators/*` (np. `FieldEccmEffectGeneratorDeployer` odczytuje `despawn_time` i pola efektów przez `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Czas odnowy (ms) między użyciami mobilnego teleportu. | jednostka mobilnego teleportu |
| `trigger_mass` | Próg masy uzbrajający wyzwalacz miny. | jednostka miny |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Obrażenia zadawane przez minę per atrybut. | jednostka miny |

`despawn_time` jest polem kluczowym: każdy umieszczony obiekt otrzymuje
`UnitDespawnHelper`, którego `IntervalTimer` (tyk 650 ms) ponownie sprawdza
efekt `effect_despawn_timer` i, gdy zniknie, uruchamia strategię usunięcia.

### Przykład — `def_mobile_field_eccm`

Z [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (obiekt) / 50 (kapsuła w pancerzu)
despawn_time=900000          → 900 s = 15 min czasu życia
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Rozłożenie kapsuły generuje obiekt w pozycji robota; żyje 15 minut,
ma 15 000 pancerza z 150% odpornością, a podczas życia emituje pole, które zwiększa
moc czujników o 100% i zmniejsza promieniowanie reaktora o 25%.

<!-- Developer notes: EntitiesModule.cs:449 (ByCategoryFlags<PlantSeedDeployer>
     cf_deployable_structure); ExportedTypes/CategoryFlags.cs (cf_deployable_structure
     = 0x998), ExportedTypes/AttributeFlags.cs (deployable = 23);
     EntityFramework/DefinitionConfig.cs (targetdefinition column, TargetEntityDefault);
     Deployers/ItemDeployer.cs (Deploy flow, 5s beam, ZoneEnterType.Deploy);
     Zones/PBS/PBSHelper.cs (capsule<->object), Zones/PBS/PBSObjectHelper.cs
     (deconstruct -> capsule loot); Units/UnitDespawnHelper.cs (despawn_time ->
     effect_despawn_timer, 650ms tick, CancellableDespawnHelper for strongholds);
     Zones/FieldEffectGenerators/FieldEccmEffectGeneratorDeployer.cs
     (GetPropertyModifier(AggregateField.despawn_time) + effect_* fields). -->