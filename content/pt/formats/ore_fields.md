---
title: "Campos de minérios"
description: "As tabelas minerals e mineralconfigs, fórmulas de geração de veios, ciclo de vida dos nós e mecânicas de extração."
weight: 30
---

# Campos de minérios

Os dados de minérios possuem dois níveis: **por tipo** (`minerals` — qual é o material e quanto rende
uma extração) e **por zona por tipo** (`mineralconfigs` — quantos veios/nós, qual o tamanho e
nível de preenchimento). O estado em tempo de execução dos veios reside na tabela `mineralnodes`.

## `minerals`

| Coluna | Tipo | Usado por | Significado |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | O valor ordinal do enum `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Todas as junções utilizam `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Nome do tipo ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | A definição do item produzido pela extração (ex.: titan → def 168). |
| `amount` | int | `DrillerModule` | **Unidades base por extração** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Sólido (`OreLayer`), 1 = Líquido (`LiquidLayer`). |
| `enablereffectrequired` | bit | controle de módulos | Se um efeito habilitador é necessário para extrair. |
| `geoscandocument` | int | itens de escaneamento | Item de documento de geo-escaneamento para este material. |

## `mineralconfigs`

Uma linha por (zona, material). Consumida por `MineralConfigurationReader` → uma
`MineralLayer` por linha:

| Coluna | Tipo | Usado por | Significado |
|---|---|---|---|
| `zoneId` | int | construção da camada | Zona proprietária. |
| `materialtype` | int | → `minerals.idx` | O material. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Número de nós que a zona mantém deste tipo. |
| `maxtilespernode` | int | gerador | Máximo de blocos (tiles) por mancha de nó; também determina o raio de espaçamento (abaixo). |
| `totalamountpernode` | int | gerador | Quantidade total de material em um nó novo, distribuída pelos blocos da mancha. |
| `minthreshold` | double | gerador | Preenchimento mínimo normalizado por bloco (0–1); blocos abaixo dele são descartados. |

### Fórmulas de geração de nós (`MineralNodeGeneratorBase.cs`)

Para um novo nó de um tipo com a configuração acima:

```
raio        = floor( sqrt(maxtilespernode / π) ) × 2
espaçamento = a posição inicial deve ser ≥ 2 × raio do nó existente mais próximo
mancha      = preenchimento aleatório por difusão (pincel de 4 blocos) até maxtilespernode blocos válidos
tile[i]     = ( noise[i] / max(noise) ) normalizado no intervalo [minthreshold, 1]
             × (tile[i] / Σtile) × totalamountpernode
             × uniform(0.9, 1.1)          // variação aleatória, depois truncada para uint
```

Zonas de exclusão ao redor de bases de atracação e teletransportadores (`KeepOutDist`): epriton = 100 blocos
(`MINERAL_DISTANCE_FROM_BASE_MIN`), flux ore = 200; todos os outros tipos = 0.

### Exemplo prático — Daoden (zone_ASI) petróleo bruto / crude (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
raio        = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → espaçamento ≥ 80 blocos
mancha      = até 1257 blocos
bloco(tile) = fração ∈ [0.5, 1.0] × (125.000.000 / Σnormalizado) × variação
```

Um veio cheio de petróleo bruto contém 125 milhões de unidades; com a taxa básica de extração de 1.500 unidades por ciclo de
perfuratriz, são ~83.000 ciclos de material por veio, totalizando ~666.000 em todos os 8 veios da zona.

## Estado do nó — `mineralnodes`

| Coluna | Significado |
|---|---|
| `zoneid`, `materialtype` | Zona proprietária + tipo |
| `x, y, width, height` | Caixa delimitadora do nó (área da mancha) |
| `data` | `uint` comprimido por bloco (ordem por linhas na área) |

Ciclo de vida (`MineralNode.cs`, `MineralLayer.cs`):

- **Carregamento**: na inicialização da zona, todos os nós salvos são carregados; um nó cujo total seja ≤ **1%** de
  `totalamountpernode` é excluído.
- **Reposição**: se restarem menos de `maxnodes`, novos nós são gerados (fórmula acima).
- **Expiração**: um nó **intocado** expira após **7 dias** (`TimeTracker`); a mineração
  reinicia o cronômetro. Um nó cujo valor máximo de bloco chegue a 0 também expira.
- **Persistência**: nós alterados são gravados no banco de dados a cada **30 minutos**.
- **Acoplamento de minério Flux (Flux ore)**: a diminuição/expiração de um nó de `FluxOre` publica
  `OreNpcSpawnMessage` → o gerador de NPCs responde (`OreNPCSpawner`).

## Mecânicas de extração (`MineralExtractor.cs`, `DrillerModule.cs`)

A quantidade de extração é `minerals.amount` multiplicada pela propriedade
`mining_amount_modifier` do robô (agregada de `mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Sólido** (`OreLayer`): retira `min(valor do bloco, quantidade)` do **único bloco** sobre
  o qual o robô está posicionado.
- **Líquido** (`LiquidLayer`): drena o **nó inteiro**, priorizando os blocos mais próximos
  (fila de prioridade por distância ao quadrado), até que a quantidade seja atendida.
- **Cascalho / Gravel** (apenas zonas de treinamento, `GravelLayer`): lê o valor do bloco, mas não
  o reduz — nós de cascalho são inesgotáveis.

O rendimento por tipo (produtos refinados) encontra-se em [Minérios](/content/ores/); as contagens de nós por zona
estão no [Índice de zonas](/zones/zone-index/).

<!-- Developer notes: Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     (reader + config), MineralLayer.cs (LoadMineralNodes 1% delete + top-up,
     GenerateNewNode radius/tile/amount wiring, FluxOre events),
     Generators/MineralNodeGeneratorBase.cs (FindStartPosition, NormalizeNoise,
     CreateMineralNode, KeepOutDist), Generators/RandomWalkMineralNodeGenerator.cs
     (flood fill, 50k step cap), MineralNode.cs (uint[] values, 7-day expiry,
     30-min save), MineralNodeRepository.cs (mineralnodes table, compressed
     values), Minerals/MineralExtractor.cs (solid/liquid/gravel extraction),
     Modules/DrillerModule.cs (amount property + modifiers), Materials/MaterialHelper.cs
     (minerals.definition -> item), Zones/DistanceConstants.cs
     (MINERAL_DISTANCE_FROM_BASE_MIN = 100). -->
