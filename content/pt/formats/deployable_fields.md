---
title: "Campos de implantáveis"
description: "Como os implantáveis são identificados, o emparelhamento cápsula-objeto e os campos agregados que controlam objetos posicionados na zona."
weight: 40
---

# Campos de implantáveis

Um **implantável** (*deployable*) é um item que pode ser posicionado em uma zona como uma unidade (teleportes móveis, minas terrestres, emissores de efeito de campo, estruturas PBS, …). Ele é identificado por sinalizadores (*flags*), emparelhado com uma definição de cápsula↔objeto e controlado em tempo de execução por campos agregados.

## Identificação

- **Sinalizador de categoria** `cf_deployable_structure` = `0x998` (máscara de bits) em
  `entitydefaults.categoryflags` — o conjunto verificado pelo registro de entidades para registrar
  classes de itens implantadores (`EntitiesModule.cs`, por exemplo, `PlantSeedDeployer` é registrado
  para esta categoria).
- **Sinalizador de atributo** `deployable` = bit **23** em `entitydefaults.attributeflags`
  (máscara `1 << 23`).
- O catálogo completo (com atributos/estatísticas) é gerado em [Deployables](/content/deployables/).

## Emparelhamento cápsula ↔ objeto

Os implantáveis vêm em pares: uma **cápsula** (o item transportado no inventário) e o
**objeto** (a unidade que surge na zona). Esse par é definido pela coluna do banco de dados
`entitydefaults.targetdefinition`, que é **bidirecional**:

- cápsula.`targetdefinition` → a definição do objeto
- objeto.`targetdefinition` → a definição da cápsula

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` resolvem qualquer uma
das direções. Exemplo de par: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Fluxo de implantação

`ItemDeployer.cs` (base para implantáveis não-PBS):

1. `Deploy(zone, player)` calcula a posição de surgimento (*spawn*) no centro do jogador.
2. `CreateDeployableItem` constrói a unidade do **objeto** (não a cápsula) e a salva.
3. Um "feixe de implantação" (*deploy beam*) de 5 segundos é renderizado.
4. Na confirmação da transação (*commit*), o objeto é adicionado à zona (`ZoneEnterType.Deploy`).

Estruturas PBS utilizam o fluxo separado de `PBSDeployer` / `PBSObjectHelper`; quando um objeto
PBS é desconstruído, ele é removido da zona e sua **cápsula** é adicionada ao
espólio (*loot*) (`PBSObjectHelper.cs`).

## Campos agregados em tempo de execução

Esses campos (de `aggregatevalues`, por definição) controlam um objeto posicionado assim que ele
está na zona. O consumidor de cada um é indicado a seguir.

| Campo | Significado | Consumidor |
|---|---|---|
| `despawn_time` | Tempo de vida do objeto posicionado, em **milissegundos**. Ao expirar, a unidade é removida da zona (ou destruída, se for controlada remotamente). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → aplica `effect_despawn_timer`. |
| `armor_max` | Blindagem máxima da unidade posicionada. | combate da unidade |
| `resist_chemical/explosive/kinetic/thermal` | Resistências a dano. | combate da unidade |
| `signature_radius` | Tamanho da assinatura de escaneamento. | scanner / camuflagem (*stealth*) |
| `stealth_strength` | Força de camuflagem (*stealth*). | scanner / camuflagem (*stealth*) |
| `effect_*` (ex.: `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modificadores de efeito de campo emitidos pelo objeto. | `FieldEffectGenerators/*` (ex.: `FieldEccmEffectGeneratorDeployer` lê `despawn_time` e os campos de efeito através de `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Tempo de recarga (*cooldown*, em ms) entre usos de um teleporte móvel. | unidade de teleporte móvel |
| `trigger_mass` | Limiar de massa que arma o gatilho de uma mina terrestre. | unidade de mina terrestre |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Dano causado pela mina terrestre por atributo. | unidade de mina terrestre |

`despawn_time` é o campo determinante: todo objeto posicionado recebe um
`UnitDespawnHelper` cujo `IntervalTimer` (com ciclo de 650 ms) verifica novamente o
efeito `effect_despawn_timer` e, quando este expira, executa a estratégia de desaparecimento (*despawn*).

### Exemplo prático — `def_mobile_field_eccm`

De [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 s = tempo de vida de 15 min
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Implantar a cápsula faz o objeto surgir na posição do robô; ele dura 15 minutos,
possui 15.000 de blindagem com 150% de resistência e, enquanto estiver ativo, emite um campo que aumenta
a potência dos sensores em 100% e reduz a radiação do reator em 25%.

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