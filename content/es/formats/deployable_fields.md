---
title: "Campos desplegables"
description: "Cómo se identifican los desplegables, el emparejamiento cápsula-objeto y los campos agregados que controlan los objetos colocados en la zona."
weight: 40
---

# Campos desplegables

Un **desplegable** es un objeto que puede colocarse en una zona como una unidad (teletransportadores móviles,
minas terrestres, emisores de efectos de campo, estructuras PBS, …). Se identifica mediante indicadores (flags),
se empareja con una definición de cápsula↔objeto y se controla en tiempo de ejecución mediante campos agregados.

## Identificación

- **Flag de categoría** `cf_deployable_structure` = `0x998` (máscara de bits) en
  `entitydefaults.categoryflags` — el conjunto que escanea el registro de entidades para registrar
  las clases de objetos desplegadores (`EntitiesModule.cs`, p. ej., `PlantSeedDeployer` está registrado
  para esta categoría).
- **Flag de atributo** `deployable` = bit **23** en `entitydefaults.attributeflags`
  (máscara `1 << 23`).
- El catálogo completo (con estadísticas) se genera en [Desplegables](/es/content/deployables/).

## Emparejamiento cápsula ↔ objeto

Los desplegables vienen en parejas: una **cápsula** (el objeto que llevas en el inventario) y el
**objeto** (la unidad que aparece en la zona). La pareja está determinada por la columna de la base de datos
`entitydefaults.targetdefinition`, que es **bidireccional**:

- cápsula.`targetdefinition` → la definición del objeto
- objeto.`targetdefinition` → la definición de la cápsula

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` resuelven cualquiera de las
dos direcciones. Ejemplo de pareja: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Flujo de despliegue

`ItemDeployer.cs` (base para desplegables que no son PBS):

1. `Deploy(zone, player)` calcula la posición de aparición en el centro del jugador.
2. `CreateDeployableItem` construye la unidad del **objeto** (no la cápsula) y la guarda.
3. Se renderiza un "haz de despliegue" de 5 segundos.
4. Al confirmar la transacción, el objeto se añade a la zona (`ZoneEnterType.Deploy`).

Las estructuras PBS utilizan la ruta independiente `PBSDeployer` / `PBSObjectHelper`; cuando se deconstruye un
objeto PBS, se elimina de la zona y su **cápsula** se añade al
botín (`PBSObjectHelper.cs`).

## Campos agregados en tiempo de ejecución

Estos campos (de `aggregatevalues`, por definición) controlan un objeto colocado una vez que está
en la zona. Se indica el consumidor.

| Campo | Significado | Consumidor |
|---|---|---|
| `despawn_time` | Tiempo de vida del objeto colocado, en **milisegundos**. Al expirar, la unidad se elimina de la zona (o se destruye, si es controlada remotamente). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → aplica `effect_despawn_timer`. |
| `armor_max` | Blindaje máximo de la unidad colocada. | combate de unidades |
| `resist_chemical/explosive/kinetic/thermal` | Resistencias a tipos de daño. | combate de unidades |
| `signature_radius` | Tamaño de la firma de escaneo. | escáner / sigilo |
| `stealth_strength` | Fuerza de sigilo. | escáner / sigilo |
| `effect_*` (p. ej., `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modificadores de efectos de campo emitidos por el objeto. | `FieldEffectGenerators/*` (p. ej., `FieldEccmEffectGeneratorDeployer` lee `despawn_time` y los campos de efecto mediante `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Tiempo de reutilización (ms) entre usos de un teletransportador móvil. | unidad de teletransporte móvil |
| `trigger_mass` | Umbral de masa que activa el detonador de una mina terrestre. | unidad de mina terrestre |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Daño que inflige una mina terrestre por atributo. | unidad de mina terrestre |

`despawn_time` es el campo definitorio: cada objeto colocado recibe un
`UnitDespawnHelper` cuyo `IntervalTimer` (intervalo de 650 ms) vuelve a comprobar el
efecto `effect_despawn_timer` y, cuando desaparece, ejecuta la estrategia de desaparición (despawn).

### Ejemplo práctico — `def_mobile_field_eccm`

De [Desplegables](/es/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 s = 15 min lifetime
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Desplegar la cápsula genera el objeto en la posición del robot; vive durante 15 minutos,
tiene 15 000 de blindaje con un 150% de resistencia y, mientras está activo, emite un campo que aumenta la fuerza
del sensor en un 100% y reduce la radiación del reactor en un 25%.

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
